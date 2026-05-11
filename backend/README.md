# Backend - 海外微短剧APP素材投放榜单 API

基于 FastAPI 提供榜单数据 RESTful 接口，数据存储在 `data/ranking.json`。

## 启动

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

启动后访问：

- API 根路径： http://localhost:8001/
- 自动生成的 Swagger 文档： http://localhost:8001/docs

## 接口列表

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 健康检查 |
| GET | `/api/meta` | 榜单元信息（来源、统计周期等） |
| GET | `/api/ranking` | 榜单列表，支持 `region` / `keyword` / `limit` 查询 |
| GET | `/api/ranking/{rank}` | 按排名查询单个产品 |
| GET | `/api/stats/regions` | 投放国家/地区出现频次 |
| GET | `/api/stats/companies` | 公司投放素材数汇总 |
| GET | `/api/stats/top?n=10` | 素材投放数 TOP N |
| POST | `/api/chat/stream` | 豆包流式对话（SSE） |

## 环境变量（.env）

```
VOLCANO_API_KEY=...                # 火山方舟（豆包）API Key
VOLCANO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VOLCANO_MODEL_NAME=doubao-seed-1-6-251015
```
| POST | `/api/chat/stream` | 豆包流式对话（SSE） |

## 环境变量（.env）

```
VOLCANO_API_KEY=...                # 火山方舟（豆包）API Key
VOLCANO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VOLCANO_MODEL_NAME=doubao-seed-1-6-251015
```
