import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import api from '@/services/api';
import { API } from './apiRoutes';

export const useAdminStore = defineStore('admin', () => {
  const previewSheetResult = reactive({
    shoes: null,
    clothing: null,
    accessories: null,
  });
  const previewSheetLoading = reactive({
    shoes: false,
    clothing: false,
    accessories: false,
  });
  const previewZipResult = reactive({
    shoes: null,
    clothing: null,
    accessories: null,
  });
  const previewZipLoading = reactive({
    shoes: false,
    clothing: false,
    accessories: false,
  });

  // Logs & visits
  const logs = ref([]);
  const logsLoading = ref(false);
  const totalLogs = ref(0);
  const visitsData = ref({ date: '', hours: [] });
  const visitsLoading = ref(false);

  // Requests, users, settings
  const requests = ref([]);
  const users = ref([]);
  const settings = ref([]);

  // Users and settings
  async function fetchUsers() {
    const { data } = await api.get(API.admin.listUsers);
    users.value = data.users;
  }

  async function fetchSettings() {
    const { data } = await api.get(API.admin.getSettings);
    settings.value = data.settings;
  }

  async function saveSetting(key, value) {
    await api.post(API.admin.updateSetting, { key, value });
  }

  async function deleteSetting(key) {
    await api.delete(`${API.admin.deleteSetting}/${encodeURIComponent(key)}`);
  }

  async function updateUserRole(userId, role) {
    await api.post(API.admin.setUserRole, { user_id: userId, role });
    await fetchUsers();
  }

  // Reviews management
  async function createReview(formData) {
    const { data } = await api.post(API.admin.createReview, formData);
    return data.message;
  }

  async function deleteReview(id) {
    await api.delete(`${API.admin.deleteReview}/${id}`);
  }

  // Logs & visits
  async function loadLogs(limit = 10, offset = 0) {
    logsLoading.value = true;
    try {
      const { data } = await api.get(API.admin.getLogs, { params: { limit, offset } });
      logs.value = data.logs;
      totalLogs.value = data.total;
    } finally {
      logsLoading.value = false;
    }
  }

  async function loadVisits(date) {
    visitsLoading.value = true;
    try {
      const { data } = await api.get(API.admin.getDailyVisits, { params: { date } });
      visitsData.value = { date: data.date, hours: data.hours };
    } finally {
      visitsLoading.value = false;
    }
  }

  // Requests management
  async function fetchRequests() {
    const { data } = await api.get(API.admin.listRequests);
    requests.value = data.requests;
  }

  async function deleteRequest(id) {
    await api.delete(`${API.admin.deleteRequest}/${id}`);
  }

  async function syncAll(filesMap) {
    const form = new FormData();
    Object.entries(filesMap).forEach(([cat, file]) => {
      if (file) form.append(`file_${cat}`, file);
    });
    return api.post(API.admin.syncAll, form);
  }

  return {
    // State
    previewSheetResult,
    previewSheetLoading,

    previewZipResult,
    previewZipLoading,

    logs,
    logsLoading,
    totalLogs,
    visitsData,
    visitsLoading,

    requests,
    users,
    settings,

    // Actions
    fetchUsers,
    fetchSettings,
    saveSetting,
    deleteSetting,
    updateUserRole,

    createReview,
    deleteReview,

    loadLogs,
    loadVisits,

    fetchRequests,
    deleteRequest,

    syncAll,
  };
});
