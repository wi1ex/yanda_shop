import axios from 'axios'
import { useUserStore } from '@/store/user';

const api = axios.create({
  baseURL: 'https://yandashop.ru'
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// при 401 — пытаемся взять новый access по refresh и повторить запрос
api.interceptors.response.use(null, async err => {
  const status = err.response?.status
  const original = err.config
  // если уже пытались рефрешнуть — сломаем цепочку
  if (status === 401 && !original._retry) {
    original._retry = true
    const refresh = localStorage.getItem('refreshToken')
    if (!refresh) return Promise.reject(err)
    try {
      const { data } = await api.post('/api/auth/refresh', null, {
        headers: { Authorization: `Bearer ${refresh}` }
      })
      // сохраним новый access
      localStorage.setItem('accessToken', data.access_token)
      // подставим и повторим исходный запрос
      original.headers.Authorization = `Bearer ${data.access_token}`
      return api(original)
    } catch (_e) {
      // refresh тоже упал — вынудим разлогиниться
      const userStore = useUserStore();
      await userStore.logout()
      window.location.href = '/'
    }
  }
  return Promise.reject(err)
})

export function getJwtIdentity() {
  const token = localStorage.getItem('accessToken')
  if (!token) return null
  try {
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload))
    return decoded.sub
  } catch {
    console.error('Failed to decode JWT')
    return null
  }
}

export default api
