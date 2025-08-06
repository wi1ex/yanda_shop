import axios from 'axios';
import { useUserStore } from '@/store/user';

const api = axios.create({
  baseURL: 'https://yandashop.ru'
});

/**
 * Декодирует JWT и возвращает payload или null
 */
function parseJwt(token) {
  try {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

/**
 * Silent refresh: получает новый access_token по refreshToken
 */
async function silentRefresh(refreshToken) {
  const { data } = await api.post(
    '/api/auth/refresh',
    null,
    { headers: { Authorization: `Bearer ${refreshToken}` } }
  );
  return data.access_token;
}

// Request interceptor: proactive refresh перед каждым запросом, кроме самого refresh
api.interceptors.request.use(
  async config => {
    const url = config.url || '';
    const base = config.baseURL || '';
    const refreshPath = '/api/auth/refresh';
    const isRefreshCall =
      url.endsWith(refreshPath) ||
      `${base}${refreshPath}` === url;
    if (isRefreshCall) {
      return config;
    }
    const store = useUserStore();
    let access = localStorage.getItem('accessToken');
    const refresh = localStorage.getItem('refreshToken');
    if (access && refresh) {
      const payload = parseJwt(access);
      const now = Date.now() / 1000;
      const threshold = 5 * 60; // 5 минут
      if (payload?.exp && now >= payload.exp - threshold) {
        try {
          access = await silentRefresh(refresh);
          localStorage.setItem('accessToken', access);
          store.setTokens({ access, refresh });
        } catch (e) {
          console.error('Silent refresh failed:', e);
        }
      }
      config.headers.Authorization = `Bearer ${access}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor: fallback-refresh при 401
api.interceptors.response.use(
  null,
  async err => {
    const status = err.response?.status;
    const original = err.config;
    if (status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refreshToken');
      if (!refresh) return Promise.reject(err);
      try {
        const newAccess = await silentRefresh(refresh);
        localStorage.setItem('accessToken', newAccess);
        const store = useUserStore();
        store.setTokens({ access: newAccess, refresh });
        original.headers.Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch {
        const store = useUserStore();
        await store.logout();
        window.location.href = '/';
      }
    }
    return Promise.reject(err);
  }
);

// Вспомогательная функция для получения user_id из токена
export function getJwtIdentity() {
  const token = localStorage.getItem('accessToken');
  if (!token) return null;
  try {
    return JSON.parse(atob(token.split('.')[1])).sub;
  } catch {
    console.error('Failed to decode JWT');
    return null;
  }
}

export default api;
