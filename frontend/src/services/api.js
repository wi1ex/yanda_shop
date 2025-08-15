import axios from 'axios';
import { useUserStore } from '@/store/user';

const BASE_URL = 'https://yandashop.ru';

// Основной инстанс для обычных запросов
const api = axios.create({ baseURL: BASE_URL });

// Отдельный инстанс БЕЗ интерсепторов — только для refresh
const authApi = axios.create({ baseURL: BASE_URL });

/** Декодирует JWT и возвращает payload или null */
function parseJwt(token) {
  try {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

/** Утилита: определяет, что конфиг относится к /api/auth/refresh */
function isRefreshRequest(config) {
  if (!config) return false;
  const refreshPath = '/api/auth/refresh';
  const url = config.url || '';
  // Учитываем абсолютные и относительные URL
  try {
    const u = new URL(url, BASE_URL);
    return u.pathname.endsWith(refreshPath);
  } catch {
    return url.endsWith(refreshPath);
  }
}

/** Silent refresh через отдельный инстанс без интерсепторов */
async function silentRefresh(refreshToken) {
  const { data } = await authApi.post(
    '/api/auth/refresh',
    null,
    { headers: { Authorization: `Bearer ${refreshToken}` } }
  );
  return data.access_token;
}

// Request interceptor: проактивный refresh за 5 минут до истечения
api.interceptors.request.use(
  async config => {
    if (isRefreshRequest(config)) {
      return config; // никогда не трогаем сам /refresh
    }
    const userStore = useUserStore();
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
          userStore.setTokens({ access, refresh });
        } catch (e) {
          // refresh не удался — чистим и не блокируем запрос
          await userStore.logout();
        }
      }
      // Всегда ставим актуальный access в заголовок
      if (access) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${access}`;
      }
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor: fallback-refresh при 401, КРОМЕ /refresh
api.interceptors.response.use(
  response => response,
  async err => {
    const status = err.response?.status;
    const original = err.config;

    // Если 401 не с /refresh и ещё не пробовали — пробуем один раз
    if (status === 401 && original && !original._retry && !isRefreshRequest(original)) {
      original._retry = true;
      const refresh = localStorage.getItem('refreshToken');
      if (!refresh) return Promise.reject(err);

      try {
        const newAccess = await silentRefresh(refresh);
        localStorage.setItem('accessToken', newAccess);
        const userStore = useUserStore();
        userStore.setTokens({ access: newAccess, refresh });
        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch (e) {
        const userStore = useUserStore();
        await userStore.logout();
        // Жёсткий редирект на главную
        window.location.href = '/';
        return Promise.reject(e);
      }
    }

    // 401 от /refresh или повторная ошибка — отдаём вверх
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
