import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import api from '@/services/api';
import { API } from './apiRoutes';

export const useAdminStore = defineStore('admin', () => {
  // === 1. Статистика по таблицам ===
  const sheetStats = reactive({
    shoes: {
      added:   0,
      updated: 0,
      deleted: 0
    },
    clothing: {
      added:   0,
      updated: 0,
      deleted: 0
    },
    accessories: {
      added:   0,
      updated: 0,
      deleted: 0
    }
  });

  // === 2. Результаты превью таблиц ===
  const previewSheetResult = reactive({
    shoes:      null,
    clothing:   null,
    accessories:null,
  });
  const previewSheetLoading = reactive({
    shoes:      false,
    clothing:   false,
    accessories:false,
  });

  // === 3. Статистика по картинкам ===
  const imageStats = reactive({
    shoes: {
      added:    0,
      replaced: 0,
      deleted:  0,
      warns:    0
    },
    clothing: {
      added:    0,
      replaced: 0,
      deleted:  0,
      warns:    0
    },
    accessories: {
      added:    0,
      replaced: 0,
      deleted:  0,
      warns:    0
    }
  });

  // === 4. Результаты превью зипов ===
  const previewZipResult = reactive({
    shoes:      null,
    clothing:   null,
    accessories:null,
  });
  const previewZipLoading = reactive({
    shoes:      false,
    clothing:   false,
    accessories:false,
  });

  // === Orders ===
  const orders = ref([])
  const orderDetail = ref(null)

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

  // === Orders ===
  async function fetchAllOrders() {
    const { data } = await api.get(API.admin.listAllOrders)
    orders.value = data.orders
  }

  async function fetchOrderDetailAdmin(orderId) {
    const { data } = await api.get(`${API.admin.getOrder}/${orderId}`)
    orderDetail.value = data.order
  }

  async function setNextOrderStatus(orderId) {
    const { data } = await api.post(`${API.admin.nextOrderStatus}/${orderId}`)
    const i = orders.value.findIndex(o => o.id === orderId)
    if (i >= 0) orders.value[i].status = data.status
    if (orderDetail.value?.id === orderId) {
      await fetchOrderDetailAdmin(orderId)
    }
    return data
  }

  async function cancelOrder(orderId) {
    const { data } = await api.post(`${API.admin.cancelOrder}/${orderId}`)
    const i = orders.value.findIndex(o => o.id === orderId)
    if (i >= 0) orders.value[i].status = data.status
    if (orderDetail.value?.id === orderId) {
      await fetchOrderDetailAdmin(orderId)
    }
    return data
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
    const { data } = await api.post(API.admin.syncAll, form);
    // сохраняем статистику
    sheetStats.shoes     = data.sheet_stats.shoes;
    sheetStats.clothing  = data.sheet_stats.clothing;
    sheetStats.accessories = data.sheet_stats.accessories;
    imageStats.shoes     = data.image_stats.shoes;
    imageStats.clothing  = data.image_stats.clothing;
    imageStats.accessories = data.image_stats.accessories;
    return data;
  }

  return {
    // State
    sheetStats,
    previewSheetResult,
    previewSheetLoading,

    imageStats,
    previewZipResult,
    previewZipLoading,

    orders,
    orderDetail,

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

    fetchAllOrders,
    fetchOrderDetailAdmin,
    setNextOrderStatus,
    cancelOrder,

    createReview,
    deleteReview,

    loadLogs,
    loadVisits,

    fetchRequests,
    deleteRequest,

    syncAll,
  };
});
