import axios from 'axios'
import { useStore, API } from '@/store'

const api = axios.create({
  baseURL: API.baseUrl
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
