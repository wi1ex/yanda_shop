import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { getJwtIdentity } from '@/services/api'
import { API } from './apiRoutes'

export const useUserStore = defineStore('user', () => {
  // Authentication state
  const accessToken = ref(localStorage.getItem('accessToken') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const user = ref({
    id: null,
    first_name: '',
    last_name: '',
    username: '',
    role: 'visitor',
    photo_url: null
  })

  // Profile state
  const profile = ref(null)
  const profileLoading = ref(false)
  const profileError = ref('')
  const showAuth = ref(false)

  // Helpers
  function openAuth() {
    showAuth.value = true
  }

  function closeAuth() {
    showAuth.value = false
  }

  function setTokens({ access, refresh = '' }) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }

  function isAuthenticated(id = user.value.id) {
    const token = accessToken.value
    if (!token) return false
    // Попробуем получить user_id из JWT
    const jwtId = getJwtIdentity()    // строка или null
    if (!jwtId) return false
    // Ид из стора может быть числом или строкой — приведём к строке
    return String(id) === String(jwtId)
  }


  // Auth & initialization

  // запрос регистрации
  async function requestRegistrationCode(email, username, first_name, last_name) {
    return api.post(API.auth.requestRegistrationCode, { email, username, first_name, last_name })
  }

  // запрос кода для входа
  async function requestLoginCode(email) {
    return api.post(API.auth.requestLoginCode, { email })
  }

  // верификация регистрации/авторизации
  async function verifyCode(endpoint, email, code) {
    const { data } = await api.post(endpoint, { email, code })
    if (!data?.access_token || !data?.refresh_token) {
      console.error('No tokens returned', data)
      return null
    }
    setTokens({ access: data.access_token, refresh: data.refresh_token })

    const userId = parseInt(getJwtIdentity(), 10)
    if (!userId) {
      console.error('No user_id in token')
      return null
    }
    const pd = await fetchUserProfile(userId)
    if (!pd) return null
    return {
      id:         pd.user_id,
      first_name: pd.first_name,
      last_name:  pd.last_name,
      username:   pd.username,
      role:       pd.role,
      photo_url:  pd.photo_url
    }
  }

  // переписываем регистрации и логин через общую функцию
  async function verifyRegistrationCode(email, code) {
    const profile = await verifyCode(API.auth.verifyRegistrationCode, email, code)
    if (profile) user.value = profile
  }

  async function verifyLoginCode(email, code) {
    const profile = await verifyCode(API.auth.verifyLoginCode, email, code)
    if (profile) user.value = profile
  }

  async function verifyAdminAccess() {
    try {
      await api.get(API.admin.getSettings)
      return true
    } catch {
      return false
    }
  }

  async function saveUserToServer(payload) {
    if (!payload?.id) return null
    try {
      const { data } = await api.post(API.general.saveUser, payload)
      return data
    } catch (e) {
      console.error('Failed to save Telegram user:', e)
      return null
    }
  }

  async function fetchUserProfile(userId) {
    profileLoading.value = true
    profileError.value = ''

    try {
      const { data } = await api.get(API.general.getUserProfile, {
        params: { user_id: userId }
      })
      return data
    } catch (e) {
      profileError.value =
        e.response?.status === 404
          ? 'Пользователь не найден'
          : `Ошибка ${e.response?.status || e.message}`
    } finally {
      profileLoading.value = false
    }
  }

  async function initializeTelegramUser(tgUser) {
    const payload = {
      id: tgUser.id,
      first_name: tgUser.first_name,
      last_name: tgUser.last_name,
      username: tgUser.username,
      photo_url: tgUser.photo_url || null
    }

    try {
      const data = await saveUserToServer(payload)
      if (data && data.access_token && data.refresh_token) {
        setTokens({ access: data.access_token, refresh: data.refresh_token })
      } else {
        console.error('No tokens returned for Telegram user', data)
        return
      }

      const pd = await fetchUserProfile(tgUser.id)
      if (!pd) return
      user.value = {
        id: pd.user_id,
        first_name: pd.first_name,
        last_name: pd.last_name,
        username: pd.username,
        role: pd.role,
        photo_url: pd.photo_url
      }
    } catch (e) {
      console.error('Error initializing Telegram user:', e)
    }
  }

  async function initializeVisitorUser() {
    const stored = localStorage.getItem('visitorId')
    const id = stored || crypto.randomUUID()

    if (!stored) {
      localStorage.setItem('visitorId', id)
    }
    user.value.id = id
  }


  return {
    // state
    accessToken,
    refreshToken,
    user,
    profile,
    profileLoading,
    profileError,
    showAuth,

    // helpers
    openAuth,
    closeAuth,
    setTokens,
    isAuthenticated,

    // auth/init
    requestRegistrationCode,
    verifyRegistrationCode,
    requestLoginCode,
    verifyLoginCode,
    verifyAdminAccess,
    saveUserToServer,
    fetchUserProfile,
    initializeTelegramUser,
    initializeVisitorUser,
  }
})
