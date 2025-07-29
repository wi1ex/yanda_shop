// src/store/admin.js

import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import api from '@/services/api';
import { API } from './apiRoutes';

export const useAdminStore = defineStore('admin', () => {
  // State

  // Sheets management
  const sheetUrls = ref({
    shoes: '',
    clothing: '',
    accessories: '',
  });
  const sheetResult = reactive({
    shoes: '',
    clothing: '',
    accessories: '',
  });
  const sheetSaveLoading = reactive({
    shoes: false,
    clothing: false,
    accessories: false,
  });
  const sheetImportLoading = reactive({
    shoes: false,
    clothing: false,
    accessories: false,
  });
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

  // Image ZIP uploads
  const zipResult = ref('');
  const zipLoading = ref(false);
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

  // Actions

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

  // Sheet operations
  async function loadSheetUrls() {
    const { data } = await api.get(API.admin.getSheetUrls);
    Object.assign(sheetUrls.value, data);
  }

  async function saveSheetUrl(category) {
    sheetSaveLoading[category] = true;
    sheetResult[category] = '';
    try {
      await api.post(API.admin.updateSheetUrl, {
        category,
        url: sheetUrls.value[category],
      });
      sheetResult[category] = 'Ссылка сохранена';
      return true;
    } catch (e) {
      sheetResult[category] = `Ошибка: ${e.response?.data?.error || e.message}`;
      return false;
    } finally {
      sheetSaveLoading[category] = false;
    }
  }

  async function importSheet(category) {
    sheetImportLoading[category] = true;
    sheetResult[category] = '';
    try {
      const { data } = await api.post(API.admin.importSheet, { category });
      if (data.status === 'ok') {
        const warnSkus = Array.isArray(data.warn_skus) && data.warn_skus.length
          ? data.warn_skus.join(', ')
          : 'нет';
        sheetResult[category] = `
          Добавлено: ${data.added}.
          Обновлено: ${data.updated}.
          Удалено: ${data.deleted}.
          Ошибки: ${data.warns}.
          SKU: ${warnSkus}
        `.trim();
        await loadLogs();
        return true;
      } else {
        sheetResult[category] = `Ошибка: ${data.error || JSON.stringify(data)}`;
        return false;
      }
    } catch {
      sheetResult[category] = 'Ошибка сети';
      return false;
    } finally {
      sheetImportLoading[category] = false;
    }
  }

  async function previewSheet(category) {
    previewSheetLoading[category] = true;
    previewSheetResult[category] = null;
    try {
      const { data } = await api.post(API.admin.previewSheet, { category });
      previewSheetResult[category] = data;
    } catch (e) {
      console.error('previewSheet error', e);
      previewSheetResult[category] = { error: e.message };
    } finally {
      previewSheetLoading[category] = false;
    }
  }

  async function previewAllSheets() {
    for (const category of ['shoes', 'clothing', 'accessories']) {
      await previewSheet(category);
    }
  }

  // Logs & visits
  async function loadLogs(limit = 10, offset = 0) {
    logsLoading.value = true;
    try {
      const { data } = await api.get(API.admin.getLogs, { params: { limit, offset } });
      logs.value = data.logs;
      totalLogs.value = data.total;
    } catch {
      logs.value = [];
      totalLogs.value = 0;
    } finally {
      logsLoading.value = false;
    }
  }

  async function loadVisits(date) {
    visitsLoading.value = true;
    try {
      const { data } = await api.get(API.admin.getDailyVisits, { params: { date } });
      visitsData.value = { date: data.date, hours: data.hours };
    } catch {
      visitsData.value = { date: '', hours: [] };
    } finally {
      visitsLoading.value = false;
    }
  }

  // ZIP image uploads
  async function uploadZip(file) {
    zipLoading.value = true;
    zipResult.value = '';
    const form = new FormData();
    form.append('file', file);

    try {
      const { data } = await api.post(API.admin.uploadImages, form);
      zipResult.value = `
        Добавлено: ${data.added}.
        Заменено: ${data.replaced}.
        Удалено: ${data.deleted}.
        Ошибки: ${data.warns}.
      `.trim();
      await loadLogs();
    } catch (e) {
      zipResult.value = `Ошибка: ${e.response?.data?.error || e.message}`;
    } finally {
      zipLoading.value = false;
    }
  }

  async function previewImages(filesMap) {
    Object.keys(previewZipResult).forEach(key => {
      previewZipResult[key] = null;
      previewZipLoading[key] = false;
    });

    const hasAny = Object.values(filesMap).some(f => f);
    if (!hasAny) {
      Object.keys(previewZipResult).forEach(key => {
        previewZipResult[key] = { error: 'no archive selected' };
      });
      return;
    }

    const form = new FormData();
    Object.entries(filesMap).forEach(([key, file]) => {
      if (file) form.append(`file_${key}`, file);
    });
    Object.keys(previewZipLoading).forEach(key => {
      previewZipLoading[key] = true;
    });

    try {
      const { data } = await api.post(API.admin.previewImages, form);
      Object.assign(previewZipResult, data);
    } catch (e) {
      Object.keys(previewZipResult).forEach(key => {
        previewZipResult[key] = { error: e.response?.data?.error || e.message };
      });
    } finally {
      Object.keys(previewZipLoading).forEach(key => {
        previewZipLoading[key] = false;
      });
    }
  }

  async function previewEverything(filesMap) {
    Object.keys(previewSheetResult).forEach(key => previewSheetResult[key] = null);
    Object.keys(previewZipResult).forEach(key => previewZipResult[key] = null);
    Object.keys(previewSheetLoading).forEach(key => previewSheetLoading[key] = true);
    Object.keys(previewZipLoading).forEach(key => previewZipLoading[key] = true);

    try {
      await previewAllSheets();
      await previewImages(filesMap);
    } finally {
      Object.keys(previewSheetLoading).forEach(key => previewSheetLoading[key] = false);
      Object.keys(previewZipLoading).forEach(key => previewZipLoading[key] = false);
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

  return {
    // State
    sheetUrls,
    sheetResult,
    sheetSaveLoading,
    sheetImportLoading,
    previewSheetResult,
    previewSheetLoading,
    zipResult,
    zipLoading,
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
    saveSheetUrl,
    importSheet,
    previewSheet,
    previewAllSheets,

    loadLogs,
    loadVisits,

    uploadZip,
    previewImages,
    previewEverything,

    fetchRequests,
    deleteRequest,
  };
});
