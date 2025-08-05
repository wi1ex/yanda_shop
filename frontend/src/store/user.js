import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { getJwtIdentity } from '@/services/api'
import { API } from './apiRoutes'

export const useUserStore = defineStore('user', () => {
  // Authentication state
  const accessToken = ref(localStorage.getItem('accessToken') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const user = ref({
    id:             null,
    first_name:     '',
    last_name:      '',
    middle_name:    '',
    role:           'visitor',
    phone:          '',
    email:          '',
    date_of_birth:  '',
    gender:         '',
    photo_url:      null,
  })

  // Profile state
  const isTelegramWebApp = ref(false)
  const profileLoaded    = ref(false)
  const showAuth         = ref(false)

  // Добавляем заказы и адреса
  const orders       = ref([])
  const orderDetail  = ref(null)
  const addresses    = ref([])

  // ORDERS
  async function fetchOrders() {
    const { data } = await api.get(API.general.getUserOrders)
    orders.value = data.orders
    return orders.value
  }

  async function fetchOrder(id) {
    const { data } = await api.get(`${API.general.getUserOrder}/${id}`)
    orderDetail.value = data.order
    return orderDetail.value
  }

  // ADDRESSES
  async function fetchAddresses() {
    const { data } = await api.get(API.general.listAddresses)
    addresses.value = data.addresses
    return addresses.value
  }

  async function addAddress(payload) {
    await api.post(API.general.createAddress, payload)
  }

  async function updateAddress(id, payload) {
    await api.put(`${API.general.updateAddress}/${id}`, payload)
  }

  async function deleteAddress(id) {
    await api.delete(`${API.general.deleteAddress}/${id}`)
  }

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

  async function logout() {
    accessToken.value  = ''
    refreshToken.value = ''
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    // сбросим user
    user.value = {
      id:             null,
      first_name:     '',
      last_name:      '',
      middle_name:    '',
      role:           'visitor',
      phone:          '',
      email:          '',
      date_of_birth:  '',
      gender:         '',
      photo_url:      null,
    }
  }

  // запрос регистрации
  async function requestRegistrationCode(email, first_name, last_name) {
    return api.post(API.auth.requestRegistrationCode, { email, first_name, last_name })
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
    await initializeWebUser()
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
    const { data } = await api.get(API.general.getUserProfile, {
      params: { user_id: userId }
    })
    user.value = {
      id:             data.user_id,
      first_name:     data.first_name,
      last_name:      data.last_name,
      middle_name:    data.middle_name,
      role:           data.role,
      phone:          data.phone,
      email:          data.email,
      date_of_birth:  data.date_of_birth,
      gender:         data.gender,
      photo_url:      data.photo_url
    }
  }

  async function updateProfile(formData) {
    await api.put(API.general.updateProfile, formData)
    const userId = parseInt(getJwtIdentity(), 10)
    await fetchUserProfile(userId)
  }

  async function uploadAvatar(file) {
    const fd = new FormData()
    fd.append('photo', file)
    const { data } = await api.post(API.general.uploadAvatar, fd)
    user.value.photo_url = data.photo_url
  }

  async function deleteAvatar() {
    await api.delete(API.general.deleteAvatar)
    user.value.photo_url = null
  }

  async function initializeTelegramUser(tgUser) {
    const payload = {
      id: tgUser.id,
      first_name: tgUser.first_name,
      last_name: tgUser.last_name,
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
      await fetchUserProfile(tgUser.id)
    } catch (e) {
      console.error('Error initializing Telegram user:', e)
    }
  }

  async function initializeWebUser() {
    const userId = parseInt(getJwtIdentity(), 10)
    if (userId) {
      await fetchUserProfile(userId)
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
    isTelegramWebApp,
    profileLoaded,
    showAuth,
    orders,
    orderDetail,
    addresses,

    // orders/addresses
    fetchOrders,
    fetchOrder,
    fetchAddresses,
    addAddress,
    updateAddress,
    deleteAddress,

    // helpers
    openAuth,
    closeAuth,
    setTokens,
    isAuthenticated,

    // auth/init
    logout,
    requestRegistrationCode,
    verifyRegistrationCode,
    requestLoginCode,
    verifyLoginCode,
    verifyAdminAccess,
    saveUserToServer,
    fetchUserProfile,
    updateProfile,
    uploadAvatar,
    deleteAvatar,
    initializeTelegramUser,
    initializeWebUser,
    initializeVisitorUser,
  }
})
