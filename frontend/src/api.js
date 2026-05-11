import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 8000
})

export const fetchMeta = () => api.get('/meta').then((r) => r.data)
export const fetchRanking = (params = {}) =>
  api.get('/ranking', { params }).then((r) => r.data)
export const fetchRegionStats = () => api.get('/stats/regions').then((r) => r.data)
export const fetchCompanyStats = () => api.get('/stats/companies').then((r) => r.data)
export const fetchTopStats = (n = 10) =>
  api.get('/stats/top', { params: { n } }).then((r) => r.data)

export default api
