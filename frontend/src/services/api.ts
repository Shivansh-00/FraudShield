import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({ baseURL: API_BASE_URL })

export const fetchStats = async () => (await api.get('/fraud-stats')).data
export const fetchTransactions = async () => (await api.get('/transactions')).data
export const fetchAlerts = async () => (await api.get('/fraud-alerts')).data
export const getWsUrl = () => {
  const wsBase = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')
  return `${wsBase}/ws/live`
}

export default api
