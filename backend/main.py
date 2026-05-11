"""
海外微短剧APP素材投放榜单 - FastAPI 后端
"""
import json
import os
from collections import Counter
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import AsyncOpenAI

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "ranking.json"

# 加载 .env
load_dotenv(BASE_DIR / ".env")

app = FastAPI(
    title="海外微短剧APP素材投放榜单 API",
    description="基于 DataEye 海外微短剧APP素材投放榜单数据的 RESTful API",
    version="1.0.0",
)

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_data() -> dict:
    if not DATA_FILE.exists():
        raise RuntimeError(f"数据文件不存在: {DATA_FILE}")
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/", summary="健康检查")
def root():
    return {"status": "ok", "service": "海外微短剧APP素材投放榜单 API"}


@app.get("/api/meta", summary="获取榜单元信息")
def get_meta():
    data = load_data()
    return {
        "title": data["title"],
        "source": data["source"],
        "period": data["period"],
        "total": len(data["list"]),
    }


@app.get("/api/ranking", summary="获取榜单完整列表")
def get_ranking(
    region: Optional[str] = Query(None, description="按主要投放国家/地区筛选，例如：美国"),
    keyword: Optional[str] = Query(None, description="按产品名或公司名搜索"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="返回前N条"),
):
    data = load_data()
    items = data["list"]

    if region:
        items = [it for it in items if region in it["regions"]]

    if keyword:
        kw = keyword.lower()
        items = [
            it for it in items
            if kw in it["product"].lower() or kw in it["company"].lower()
        ]

    if limit:
        items = items[:limit]

    return {
        "title": data["title"],
        "source": data["source"],
        "period": data["period"],
        "total": len(items),
        "list": items,
    }


@app.get("/api/ranking/{rank}", summary="按排名查询单个产品")
def get_by_rank(rank: int):
    data = load_data()
    for it in data["list"]:
        if it["rank"] == rank:
            return it
    raise HTTPException(status_code=404, detail=f"未找到排名为 {rank} 的产品")


@app.get("/api/stats/regions", summary="主要投放国家/地区分布统计")
def stats_regions():
    """统计每个国家/地区在榜单中出现的次数（作为主要投放区域）。"""
    data = load_data()
    counter: Counter = Counter()
    for it in data["list"]:
        for r in it["regions"]:
            counter[r] += 1
    sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return [{"region": k, "count": v} for k, v in sorted_items]


@app.get("/api/stats/companies", summary="公司投放素材数汇总")
def stats_companies():
    """按公司汇总投放素材数（同一公司多个产品累加）。"""
    data = load_data()
    agg: dict = {}
    for it in data["list"]:
        c = it["company"]
        if c == "-":
            continue
        agg.setdefault(c, {"company": c, "materials": 0, "products": []})
        agg[c]["materials"] += it["materials"]
        agg[c]["products"].append(it["product"])
    result = sorted(agg.values(), key=lambda x: x["materials"], reverse=True)
    return result


@app.get("/api/stats/top", summary="素材投放数 TOP N")
def stats_top(n: int = Query(10, ge=1, le=30)):
    data = load_data()
    items = sorted(data["list"], key=lambda x: x["materials"], reverse=True)[:n]
    return [
        {"product": it["product"], "company": it["company"], "materials": it["materials"]}
        for it in items
    ]


# ============================================================
# 豆包流式对话接口
# ============================================================

VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY", "").strip()
VOLCANO_BASE_URL = os.getenv("VOLCANO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").strip()
VOLCANO_MODEL_NAME = os.getenv("VOLCANO_MODEL_NAME", "doubao-seed-1-6-251015").strip()


def build_ranking_context() -> str:
    """把完整榜单整理成文本，作为系统提示词的上下文。"""
    data = load_data()
    period = data["period"]
    lines = [
        f"【榜单名称】{data['title']}",
        f"【数据来源】{data['source']}",
        f"【统计时间】{period['start']} ~ {period['end']}",
        f"【共 {len(data['list'])} 个产品】",
        "",
        "排名 | 产品名 | 公司 | 主要投放国家/地区 | 投放素材数",
    ]
    for it in data["list"]:
        lines.append(
            f"{it['rank']} | {it['product']} | {it['company']} | "
            f"{'、'.join(it['regions'])} | {it['materials_text']}"
        )
    return "\n".join(lines)


SYSTEM_PROMPT_TEMPLATE = """你是一名「海外微短剧APP素材投放榜单专家」，名字叫「短剧小助手」。
请基于以下榜单数据回答用户问题，回答要简洁、专业、口语化，可以使用 Markdown 列表/加粗。
当用户问及榜单之外的内容时，可以适度发挥，但要明确说明数据来源。
当用户询问排名/对比/筛选时，请直接基于下面的榜单给出准确答案，不要编造数据。

==== 榜单数据开始 ====
{ranking_context}
==== 榜单数据结束 ====
"""


class ChatMessage(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


def get_openai_client() -> AsyncOpenAI:
    if not VOLCANO_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="未配置 VOLCANO_API_KEY，请在 backend/.env 中设置",
        )
    return AsyncOpenAI(api_key=VOLCANO_API_KEY, base_url=VOLCANO_BASE_URL)


@app.post("/api/chat/stream", summary="豆包流式对话（SSE）")
async def chat_stream(req: ChatRequest):
    """
    SSE 流式对话接口，接收 messages 数组（含历史），返回 text/event-stream。
    每个 chunk 格式： data: {"type":"delta","content":"..."}
    结束：       data: [DONE]
    错误：       data: {"type":"error","error":"..."}
    """
    client = get_openai_client()

    # 构建带榜单上下文的系统提示
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(ranking_context=build_ranking_context())

    # 拼接消息：始终把 system prompt 放最前面
    messages = [{"role": "system", "content": system_prompt}]
    for m in req.messages:
        if m.role in ("user", "assistant"):
            messages.append({"role": m.role, "content": m.content})

    async def event_generator():
        try:
            stream = await client.chat.completions.create(
                model=VOLCANO_MODEL_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    payload = {"type": "delta", "content": content}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            err = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
