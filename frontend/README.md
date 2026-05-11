# Frontend - 海外微短剧APP素材投放榜单

基于 **Vue 3 + Vite + ECharts** 的可视化前端，调用后端 FastAPI 接口展示榜单数据。

## 启动

```bash
cd frontend
npm install
npm run dev
```

启动后访问：http://localhost:5173

> 默认通过 Vite Proxy 把 `/api/*` 转发到 `http://localhost:8000`，请先启动后端。

## 功能

- 🥇 排行榜表格：金/银/铜牌排名样式、国家/地区标签、产品/公司搜索、地区筛选
- 📊 TOP 10 横向柱状图：直观对比头部产品素材投放量
- 🌍 国家/地区分布饼图：统计主要投放区域出现频次
- 🤖 浮动 AI 助手：右下角点击对话，SSE 流式输出，聊天历史持久化在 localStorage
- 🎨 视觉风格还原原榜单粉橙渐变主题

## 目录

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.js
    ├── App.vue
    ├── api.js
    ├── style.css
    └── components/
        ├── RankingTable.vue
        ├── TopChart.vue
        ├── RegionChart.vue
        └── ChatBot.vue        # 浮动机器人 + 流式对话
```
