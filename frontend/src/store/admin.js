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

  // Combined preview + import for Sheets
  async function validateAndImportSheet(category) {
    previewSheetLoading[category] = true;
    previewSheetResult[category] = null;
    try {
      await api.post(API.admin.importAndPreviewSheet, { category });
      await loadLogs();
      return true;
    } catch (e) {
      if (e.response?.status === 400 && e.response.data.status === 'validation_failed') {
        previewSheetResult[category] = {
          total_rows: e.response.data.total_rows,
          invalid_count: e.response.data.invalid_count,
          errors: e.response.data.errors,
        };
      }
      return false;
    }
  }

  // Combined preview + upload for ZIP images
  async function validateAndUploadImages(filesMap) {
    // очистим старые превью
    Object.keys(previewZipResult).forEach(cat => previewZipResult[cat] = null);

    // поставить loading-флаги
    Object.keys(previewZipLoading).forEach(cat => {
      previewZipLoading[cat] = !!filesMap[cat];
    });

    try {
      const form = new FormData();
      Object.entries(filesMap).forEach(([cat, file]) => {
        if (file) form.append(`file_${cat}`, file);
      });
      await api.post(API.admin.uploadAndPreviewImages, form);
      await loadLogs();
      return true;
    } catch (e) {
      if (e.response?.status === 400 && e.response.data.status === 'validation_failed') {
        const reports = e.response.data.reports || {};
        Object.entries(reports).forEach(([cat, report]) => {
          if (previewZipResult[cat] !== undefined) {
            previewZipResult[cat] = report;
          }
        });
      }
      return false;
    }
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

    loadSheetUrls,

    loadLogs,
    loadVisits,

    fetchRequests,
    deleteRequest,

    validateAndImportSheet,
    validateAndUploadImages,
  };
});
