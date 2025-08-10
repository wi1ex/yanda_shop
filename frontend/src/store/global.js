import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { API } from './apiRoutes'

export const useGlobalStore = defineStore('global', () => {
  const parameters      = ref([])
  const reviews         = ref([])
  const showMenu        = ref(false)
  const showSearch      = ref(false);
  const showSearchQuery = ref(false);
  const searchQuery     = ref('')
  const filesURL        = 'https://yandashop.ru/download'

  async function fetchParameters() {
    try {
      const { data } = await api.get(API.general.getParameters)
      parameters.value = data
    } catch (e) {
      console.error('Failed to load parameters:', e)
    }
  }

  async function fetchReviews() {
    try {
      const { data } = await api.get(API.general.listReviews)
      reviews.value = data.reviews
    } catch (e) {
      console.error('Failed to load reviews:', e)
    }
  }

  async function createRequest(formData) {
    try {
      await api.post(API.general.createRequest, formData)
    } catch (e) {
      console.error('Failed to send request:', e)
    }
  }

  return {
    parameters,
    reviews,
    showMenu,
    showSearch,
    showSearchQuery,
    searchQuery,
    filesURL,

    // public data
    fetchParameters,
    fetchReviews,

    // contact
    createRequest
  }
})
