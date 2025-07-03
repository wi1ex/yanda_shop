import axios from 'axios'
import { useStore } from '@/store'

const api = axios.create({
  baseURL: 'https://shop.yanda.twc1.net'
})

api.interceptors.request.use(config => {
  const store = useStore()
  alert(`[API] -> ${config.method} ${config.url}. Auth:${config.headers.Authorization}`)
  const token = store.accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
