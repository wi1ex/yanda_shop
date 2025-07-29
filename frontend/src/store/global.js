// src/store/global.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { API } from './apiRoutes'

export const useGlobalStore = defineStore('global', () => {
  // Public settings & reviews
  const parameters = ref([])
  const reviews = ref([])

  // Public data
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

  // Contact form
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

    // public data
    fetchParameters,
    fetchReviews,

    // contact
    createRequest
  }
})
