import axios from 'axios'

// 优先读取构建期注入的 VITE_API_BASE；否则按环境推导：
//   - 本地开发：走 Vite 代理（vite.config.js 已把 /api 转发到 8001）
//   - 生产 Vercel：vercel.json 中 backend.routePrefix = "/_/backend"
//     所以真实地址是 https://<domain>/_/backend/api/...
const isProd = import.meta.env.PROD
const fallbackBase = isProd ? '/_/backend/api' : '/api'
const baseURL = import.meta.env.VITE_API_BASE || fallbackBase

const api = axios.create({
  baseURL,
  timeout: 30000
})

export const fetchMeta = () => api.get('/meta').then((r) => r.data)
export const fetchRanking = (params = {}) =>
  api.get('/ranking', { params }).then((r) => r.data)
export const fetchRegionStats = () => api.get('/stats/regions').then((r) => r.data)
export const fetchCompanyStats = () => api.get('/stats/companies').then((r) => r.data)
export const fetchTopStats = (n = 10) =>
  api.get('/stats/top', { params: { n } }).then((r) => r.data)

// ChatBot 用的流式接口路径，相对于当前页面的同源
export const CHAT_STREAM_URL = `${baseURL}/chat/stream`

export default api
