# 海外微短剧APP素材投放榜单 · 全栈展示项目

> 数据来源：**DataEye** · 海外微短剧APP素材投放（总榜）  
> 统计时间：2026-03-16 ~ 2026-03-22

将一份原本以图片形式发布的 TOP 30 榜单，重制为 **可交互、可筛选、可视化** 的前后端项目。

## 项目结构

```
.
├── backend/        # FastAPI 后端，提供榜单与统计接口
│   ├── data/ranking.json    # 榜单数据（30条）
│   ├── main.py              # API 入口
│   ├── requirements.txt
│   └── README.md
├── frontend/       # Vue 3 + Vite + ECharts 前端
│   ├── src/                 # App / 表格 / 图表组件
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
└── README.md       # 本文档
```

## 技术栈

| 层 | 技术 |
| --- | --- |
| 后端 | Python 3.9+ · FastAPI · Uvicorn · 文件存储（JSON） |
| 前端 | Vue 3 · Vite · ECharts (vue-echarts) · Axios |
| 接口 | RESTful，自动生成 Swagger 文档 (`/docs`) |

## 功能特性

- 📋 **完整榜单表格**：30 个产品的排名 / 公司 / 主要投放国家 / 素材数
- 🥇 **金银铜牌排名样式**，国家/地区标签化展示
- 🔍 **搜索 + 筛选**：按产品名/公司名搜索，按国家/地区过滤
- 📊 **TOP 10 横向柱状图**（ECharts）
- 🌍 **国家/地区分布饼图**：统计主要投放区域出现频次
- 🤖 **浮动 AI 助手（豆包驱动）**：右下角点击对话，**SSE 流式输出**，自带榜单上下文，可问"哪个 APP 投放最多"等
- 🎨 视觉风格还原原榜单粉橙渐变主题

## 快速启动

### 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 配置豆包 API Key（首次必做）
cp .env.example .env
# 然后编辑 .env，把 VOLCANO_API_KEY 替换为你的真实 key
# 申请地址：https://www.volcengine.com/product/ark

uvicorn main:app --reload --port 8001
```

> ⚠️ `.env` 已在 `.gitignore` 中，**真实 API Key 不会被提交到 GitHub**。
> 如需更换模型，修改 `.env` 中的 `VOLCANO_MODEL_NAME` 即可。

访问 http://localhost:8001/docs 可查看自动生成的 Swagger 文档。

### 2. 启动前端

新开一个终端：

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 即可看到完整页面。

> 前端通过 Vite Proxy 把 `/api/*` 自动转发到后端 `http://localhost:8001`，无需 CORS 额外配置。

## 后端接口一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/meta` | 榜单元信息（来源、统计周期、产品数） |
| GET | `/api/ranking` | 榜单列表，支持 `region` / `keyword` / `limit` |
| GET | `/api/ranking/{rank}` | 按排名查询单个产品 |
| GET | `/api/stats/regions` | 投放国家/地区出现频次 |
| GET | `/api/stats/companies` | 公司投放素材数汇总 |
| GET | `/api/stats/top?n=10` | 素材投放数 TOP N |
| POST | `/api/chat/stream` | 豆包流式对话（SSE），body: `{messages: [{role, content}]}` |
| POST | `/api/chat/stream` | 豆包流式对话（SSE），body: `{messages: [{role, content}]}` |

示例：

```bash
curl http://localhost:8001/api/ranking?region=美国&limit=5
curl http://localhost:8001/api/stats/top?n=10
```

## 数据来源说明

榜单原图来自 **DataEye · ADX 短剧海外版**，本项目仅用于技术演示与数据可视化练习，所有榜单内容、公司及产品名版权归原方所有。
