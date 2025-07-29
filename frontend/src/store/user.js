// src/store/user.js

import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
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

  // Helpers
  function isTelegramUserId(id) {
    const n = parseInt(id, 10)
    return !isNaN(n) && String(n) === String(id)
  }

  function setTokens({ access, refresh = '' }) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }

  // Auth & initialization
  async function verifyAdminAccess() {
    try {
      await api.get(API.admin.getSettings)
      return true
    } catch {
      return false
    }
  }

  async function saveUserToServer(payload) {
    if (!payload?.id) return
    try {
      await api.post(API.general.saveUser, payload)
    } catch (e) {
      console.error('Failed to save Telegram user:', e)
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
      await saveUserToServer(payload)
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

      if (pd.access_token) {
        setTokens({
          access: pd.access_token,
          refresh: pd.refresh_token || ''
        })
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

    // helpers
    isTelegramUserId,
    setTokens,

    // auth/init
    verifyAdminAccess,
    saveUserToServer,
    fetchUserProfile,
    initializeTelegramUser,
    initializeVisitorUser,
  }
})
