import axios from 'axios'
import { useStore } from '@/store'

const api = axios.create({
  baseURL: 'https://shop.yanda.twc1.net'
})

api.interceptors.request.use(config => {
  const store = useStore()
  const token = store.accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
