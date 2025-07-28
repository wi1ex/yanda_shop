import {defineStore} from 'pinia'
import {computed, reactive, ref, watch} from 'vue'
import api from '@/services/api'

export const API = {
  general: {
    healthCheck:        '/api/general',                      // GET    - health check
    saveUser:           '/api/general/save_user',            // POST   - сохранить/обновить Telegram-пользователя
    getUserProfile:     '/api/general/get_user_profile',     // GET    - получить профиль
    getParameters:      '/api/general/get_parameters',       // GET    - получить публичные настройки
    listReviews:        '/api/general/list_reviews',         // GET    - получить список отзывов
    createRequest:      '/api/general/create_request',       // POST   - отправить заявку на поиск товара
  },
  product: {
    listProducts:       '/api/product/list_products',        // GET    - список товаров (фильтр по категории)
    getProduct:         '/api/product/get_product',          // GET    - детали одного товара
    getCart:            '/api/product/get_cart',             // GET    - получить корзину пользователя
    saveCart:           '/api/product/save_cart',            // POST   - сохранить корзину
    getFavorites:       '/api/product/get_favorites',        // GET    - получить избранное
    saveFavorites:      '/api/product/save_favorites',       // POST   - сохранить избранное
  },
  admin: {
    setUserRole:        '/api/admin/set_user_role',          // GET    - установить пользователю роль
    getDailyVisits:     '/api/admin/get_daily_visits',       // GET    - статистика визитов по часам
    getLogs:            '/api/admin/get_logs',               // GET    - журнал
    getSheetUrls:       '/api/admin/get_sheet_urls',         // GET    - URL Google Sheets
    updateSheetUrl:     '/api/admin/update_sheet_url',       // POST   - сохранить URL таблицы
    importSheet:        '/api/admin/import_sheet',           // POST   - импорт CSV из Sheets
    previewSheet:       '/api/admin/preview_sheet',          // POST   - проверка CSV из Sheets
    uploadImages:       '/api/admin/upload_images',          // POST   - загрузка ZIP с изображениями
    previewImages:      '/api/admin/preview_images',         // POST   - проверка ZIP с изображениями
    getSettings:        '/api/admin/get_settings',           // GET    - получить список настроек
    updateSetting:      '/api/admin/update_setting',         // POST   - изменить список настроек
    deleteSetting:      '/api/admin/delete_setting',         // DELETE - удалить параметр настроек
    createReview:       '/api/admin/create_review',          // POST   - загрузить новый отзыв
    deleteReview:       '/api/admin/delete_review',          // DELETE - удалить отзыв
    listRequests:       '/api/admin/list_requests',          // GET    - получить список заявок на поиск товара
    deleteRequest:      '/api/admin/delete_request',         // DELETE - удалить заявку на поиск товара
    listUsers:          '/api/admin/list_users',             // GET    - получить список пользователей
  }
}

export const useStore = defineStore('main', () => {
  // -------------------------------------------------
  // State
  // -------------------------------------------------
  const accessToken         = ref(localStorage.getItem('accessToken') || '')
  const refreshToken        = ref(localStorage.getItem('refreshToken') || '')
  const user                = ref({
    id: null,
    first_name: '',
    last_name: '',
    username: '',
    role: 'visitor',
    photo_url: null
  })

  // Категории
  const categoryList        = ref(['Одежда', 'Обувь', 'Аксессуары'])
  const selectedCategory    = ref('')

  // Подкатегории
  const showSubcats         = ref(false)
  const selectedSubcat      = ref('')
  const currentSubcatPage   = ref(0)

  // Сортировка
  const sortBy              = ref('date')
  const sortOrder           = ref('desc')

  // Фильтры
  const filterPriceMin      = ref(null)
  const filterPriceMax      = ref(null)
  const filterGender        = ref('')
  const filterSubcat        = ref('')
  const filterBrands        = ref([])
  const filterColors        = ref([])
  const filterSizes         = ref([])

  // Товары
  const products            = ref([])

  // Корзина
  const cartOrder           = ref([])
  const cart                = ref({ count: 0, total: 0, items: [] })
  const cartLoaded          = ref(false)
  const showCartDrawer      = ref(false)

  // Избранное
  const favorites           = ref({ items: [], count: 0 })
  const favoritesLoaded     = ref(false)

  // === AdminPage ===
  const sheetUrls           = ref({ shoes: '', clothing: '', accessories: '' })
  const sheetResult         = reactive({ shoes: '', clothing: '', accessories: '' })
  const sheetSaveLoading    = reactive({ shoes: false, clothing: false, accessories: false })
  const sheetImportLoading  = reactive({ shoes: false, clothing: false, accessories: false })
  const previewSheetResult  = reactive({ shoes: null, clothing: null, accessories: null });
  const previewSheetLoading = reactive({ shoes: false, clothing: false, accessories: false });

  const zipResult           = ref('')
  const zipLoading          = ref(false)
  const previewZipResult    = reactive({ shoes:null, clothing:null, accessories:null });
  const previewZipLoading   = reactive({ shoes:false, clothing:false, accessories:false });

  const logs                = ref([])
  const logsLoading         = ref(false)
  const totalLogs           = ref(0)

  const visitsData          = ref({ date: '', hours: [] })
  const visitsLoading       = ref(false)

  const requests            = ref([])

  // === ProductPage ===
  const detailData          = ref(null)
  const detailLoading       = ref(false)
  const variants            = ref([])

  // === ProfilePage ===
  const profile             = ref(null)
  const profileLoading      = ref(false)
  const profileError        = ref('')

  const parameters          = ref([])
  const settings            = ref([])
  const reviews             = ref([])
  const users               = ref([])

  // -------------------------------------------------
  // Watchers
  // -------------------------------------------------
  watch(() => user.value?.id, (newId) => {
    if (newId && isTelegramUserId(newId)) {
      loadCartFromServer()
      loadFavoritesFromServer()
    } else {
      cartLoaded.value = true
      favoritesLoaded.value = true
    }
  })

  watch(() => filterGender.value, () => {
    showSubcats.value      = false
    selectedSubcat.value   = ''
    currentSubcatPage.value = 0
    // при необходимости: selectedCategory.value = ''
  })

  // -------------------------------------------------
  // Helpers
  // -------------------------------------------------
  function isTelegramUserId(id) {
    const asNum = parseInt(id, 10)
    return (!Number.isNaN(asNum) && String(asNum) === String(id))
  }

  function setTokens({ access, refresh = '' }) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }

  // -------------------------------------------------
  // Auth / Init
  // -------------------------------------------------
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
      console.error('Не удалось сохранить TG пользователя:', e)
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
      console.error(e)
      profileError.value = e.response?.status === 404 ? 'Пользователь не найден' : `Ошибка ${e.response?.status || e.message}`
    } finally {
      profileLoading.value = false
    }
  }

  async function initializeTelegramUser(tgUser) {
    const payload = {
      id:         tgUser.id,
      first_name: tgUser.first_name,
      last_name:  tgUser.last_name,
      username:   tgUser.username,
      photo_url:  tgUser.photo_url || null
    }
    try {
      await saveUserToServer(payload)
      const profileData = await fetchUserProfile(tgUser.id)
      user.value = {
        id:         profileData.user_id,
        first_name: profileData.first_name,
        last_name:  profileData.last_name,
        username:   profileData.username,
        role:       profileData.role,
        photo_url:  profileData.photo_url,
      }
      if (profileData.access_token) {
        setTokens({
          access:  profileData.access_token,
          refresh: profileData.refresh_token || ''
        })
      }
    } catch (e) {
      console.error('Ошибка инициализации Telegram-пользователя:', e)
    }
  }

  async function initializeVisitorUser() {
    const stored = localStorage.getItem('visitorId')
    const id = stored || crypto.randomUUID()
    if (!stored) localStorage.setItem('visitorId', id)
    user.value.id = id
  }

  // -------------------------------------------------
  // General User Actions
  // -------------------------------------------------
  async function fetchParameters() {
    const { data } = await api.get(API.general.getParameters)
    parameters.value = data
  }

  // -------------------------------------------------
  // Product Actions
  // -------------------------------------------------
  async function fetchProducts(cat = null) {
    if (cat) selectedCategory.value = cat
    try {
      const { data } = await api.get(API.product.listProducts, {
        params: cat ? { category: cat } : {}
      })
      products.value = data
    } catch (e) {
      console.error('Не удалось загрузить товары:', e)
    }
  }

  async function fetchDetail(variantSku, category) {
    detailLoading.value = true
    try {
      const { data } = await api.get(API.product.getProduct, {
        params: { category, variant_sku: variantSku }
      })
      detailData.value = data
      await fetchProducts(category)
      variants.value = products.value.filter(p => p.sku === detailData.value.sku)
    } catch (e) {
      console.error(e)
    } finally {
      detailLoading.value = false
    }
  }

  // -------------------------------------------------
  // Cart Actions
  // -------------------------------------------------
  async function loadCartFromServer() {
    if (!user.value?.id || !isTelegramUserId(user.value.id)) {
      cartLoaded.value = true
      return
    }
    try {
      const { data } = await api.get(API.product.getCart, {
        params: { user_id: user.value.id }
      })
      if (data.items) {
        cart.value.items = data.items
        cart.value.count = data.count
        cart.value.total = data.total
        cartOrder.value = Array.from(new Set(data.items.map(i => i.variant_sku)))
      }
    } catch (e) {
      console.error('Cannot load cart:', e)
    } finally {
      cartLoaded.value = true
    }
  }

  async function saveCartToServer() {
    if (!user.value?.id || !isTelegramUserId(user.value.id)) return
    const payload = {
      user_id: user.value.id,
      items: cart.value.items.map(i => ({
        variant_sku:    i.variant_sku,
        delivery_label: i.delivery_option?.label || null
      }))
    }
    try {
      await api.post(API.product.saveCart, payload)
    } catch (e) {
      console.error('Error saving cart to server:', e)
    }
  }

  function openCartDrawer() {
    if (showCartDrawer.value === false) showCartDrawer.value = true
  }
  function closeCartDrawer() {
    if (showCartDrawer.value === true) showCartDrawer.value = false
  }

  // -------------------------------------------------
  // Favorites Actions
  // -------------------------------------------------
  async function loadFavoritesFromServer() {
    if (!user.value?.id || !isTelegramUserId(user.value.id)) {
      favoritesLoaded.value = true
      return
    }
    try {
      const { data } = await api.get(API.product.getFavorites, {
        params: { user_id: user.value.id }
      })
      favorites.value.items = data.items || []
      favorites.value.count = data.count || favorites.value.items.length
    } catch (e) {
      console.error('Cannot load favorites:', e)
    } finally {
      favoritesLoaded.value = true
    }
  }

  async function saveFavoritesToServer() {
    if (!user.value?.id || !isTelegramUserId(user.value.id)) return
    const payload = {
      user_id: user.value.id,
      items: favorites.value.items
    }
    try {
      await api.post(API.product.saveFavorites, payload)
    } catch (e) {
      console.error('Error saving favorites:', e)
    }
  }

  function addToFavorites(color_sku) {
    if (favorites.value.items.includes(color_sku)) return
    favorites.value.items.push(color_sku)
    favorites.value.count = favorites.value.items.length
    saveFavoritesToServer()
  }

  function removeFromFavorites(color_sku) {
    favorites.value.items = favorites.value.items.filter(cs => cs !== color_sku)
    favorites.value.count = favorites.value.items.length
    saveFavoritesToServer()
  }

  function isFavorite(color_sku) {
    return favorites.value.items.includes(color_sku)
  }

  // -------------------------------------------------
  // Utils: grouping & computed
  // -------------------------------------------------
  const subcatListMap = computed(() => {
    // Инициализируем пустые наборы для трёх корней
    const map = {
      'Одежда':     new Set(),
      'Обувь':      new Set(),
      'Аксессуары': new Set()
    };
    // Пробегаемся по всем товарам, фильтруя по полу (если надо)
    products.value.forEach(p => {
      // Если стоит фильтр пола — пропускаем неподходящие
      if (filterGender.value) {
        const g = filterGender.value;
        if (p.gender !== g && p.gender !== 'U') return;
      }
      // Категория товара должна быть одним из ключей
      if (!map[p.category]) return;
      // Собираем подкатегорию (должно быть поле p.subcategory с реальным названием)
      map[p.category].add(p.subcategory);
    });
    // Преобразуем Set → Array для каждой категории
    const result = {};
    Object.entries(map).forEach(([cat, set]) => {
      result[cat] = Array.from(set).sort();
    });
    return result;
  })

  const colorGroups = computed(() => {
    const map = {}
    products.value.forEach(p => {
      const key = p.color_sku
      if (!map[key]) map[key] = { color_sku: key, variants: [] }
      map[key].variants.push(p)
    })
    return Object.values(map).map(group => {
      const minPriceVariant = group.variants.reduce((prev, cur) => prev.price <= cur.price ? prev : cur)
      const minDateVariant = group.variants.reduce((prev, cur) => prev.created_at <= cur.created_at ? prev : cur)
      return {
        color_sku: group.color_sku,
        variants: group.variants,
        minPriceVariant,
        minDateVariant,
        minPrice: minPriceVariant.price,
        minDate: minDateVariant.created_at
      }
    })
  })

  const distinctColors = computed(() => {
    return Array
      .from(new Set(products.map(p => p.color).filter(Boolean)))
      .sort((a, b) => a.localeCompare(b, 'ru', { sensitivity: 'base' }));
  });

  const distinctBrands = computed(() => {
    return Array
      .from(new Set(products.map(p => p.brand).filter(Boolean)))
      .sort((a, b) => a.localeCompare(b, 'ru', { sensitivity: 'base' }));
  });

  const distinctSizes = computed(() => {
    const sizes = Array
      .from(new Set(products.map(p => p.size_label).filter(Boolean)));

    return sizes.sort((a, b) => {
      const na = parseFloat(a);
      const nb = parseFloat(b);
      const bothNum = !isNaN(na) && !isNaN(nb);

      if (bothNum) return na - nb;       // оба «числовые» — по значению
      if (!isNaN(na)) return -1;         // только a — числовой, будет раньше
      if (!isNaN(nb)) return 1;          // только b — числовой, будет раньше
      // оба не числа — по алфавиту (русская локаль)
      return a.localeCompare(b, 'ru', { sensitivity: 'base' });
    });
  });

  const displayedProducts = computed(() => {
    let list = colorGroups.value.slice()

    if (['M','F'].includes(filterGender.value)) {
      list = list.filter(g => g.variants.some(v => v.gender === filterGender.value || v.gender === 'U'))
    }
    if (filterColors.value.length) {
      list = list.filter(g => g.variants.some(p => filterColors.value.includes(p.color)) )
    }
    if (filterPriceMin.value != null) {
      list = list.filter(g => g.variants.some(v => v.price >= filterPriceMin.value))
    }
    if (filterPriceMax.value != null) {
      list = list.filter(g => g.variants.some(v => v.price <= filterPriceMax.value))
    }
    if (filterSubcat.value) {
      list = list.filter(g => g.variants.some(v => v.subcategory === filterSubcat.value))
    }
    if (filterBrands.value.length) {
      list = list.filter(g => g.variants.some(p => filterBrands.value.includes(p.brand)))
    }
    if (filterSizes.value.length) {
      list = list.filter(g => g.variants.some(p => filterSizes.value.includes(p.size_label)) )
    }

    list.forEach(g => {
      g.totalSales = g.variants.reduce((sum, v) => sum + (v.count_sales||0), 0)
    })

    const mod = (sortOrder.value === 'asc' ? 1 : -1)
    if (sortBy.value === 'price') {
      list.sort((a, b) => mod * (a.minPrice - b.minPrice))
    } else if (sortBy.value === 'sales') {
      list.sort((a, b) => mod * (a.totalSales - b.totalSales) || mod * (a.minPrice - b.minPrice))
    } else {
      list.sort((a, b) => mod * a.minDate.localeCompare(b.minDate))
    }

    return list
  })

  const groupedCartItems = computed(() => {
    const map = {}
    for (const item of cart.value.items) {
      const key = `${item.variant_sku}_${item.delivery_option?.label}`
      if (!map[key]) map[key] = { ...item, quantity: 0, totalPrice: 0 }
      map[key].quantity++
      map[key].totalPrice += item.price
    }
    return Object.values(map)
  })

  // Открыть подкатегории для данной категории
  function openSubcats() {
    selectedSubcat.value = ''
    currentSubcatPage.value = 0
    showSubcats.value = true
  }

  // Вернуться к выбору корневых категорий
  function backToCats() {
    showSubcats.value = false
    selectedSubcat.value = ''
    filterSubcat.value = ''
    currentSubcatPage.value = 0
    selectedCategory.value = ''
  }

  // Выбор подкатегории
  function pickSubcat(subcat) {
    if (selectedSubcat.value === subcat) {
      selectedSubcat.value = ''
      filterSubcat.value = ''
    } else {
      selectedSubcat.value = subcat
      filterSubcat.value = subcat
    }
  }

  function changeCategory(cat) {
    selectedCategory.value = cat
    // сортировка на дефолт
    sortBy.value    = 'date'
    sortOrder.value = 'desc'
    // сбросить фильтры
    clearFilters()
  }

  function addToCart(product) {
    const unitPrice = product.computed_price ?? product.price
    const exist = cart.value.items.find(i =>
      i.variant_sku === product.variant_sku
      && i.delivery_option?.label === product.delivery_option?.label
    )
    if (exist) {
      increaseQuantity(exist)
    } else {
      cart.value.count++
      cart.value.total += unitPrice
      const id = `${Date.now()}-${Math.random()}`
      cart.value.items.push({ ...product, id, unit_price: unitPrice })
      cartOrder.value.push(product.variant_sku)
    }
    saveCartToServer()
  }

  function increaseQuantity(item) {
    cart.value.count++
    cart.value.total += item.unit_price
    cart.value.items.push(item)
    saveCartToServer()
  }

  function decreaseQuantity(product) {
    const idx = cart.value.items.findIndex(i =>
      i.variant_sku === product.variant_sku
      && i.delivery_option?.label === product.delivery_option?.label
    )
    if (idx === -1) return
    const qty = cart.value.items.filter(i =>
      i.variant_sku === product.variant_sku
      && i.delivery_option?.label === product.delivery_option?.label
    ).length
    cart.value.count--
    const delta = product.unit_price ?? product.price
    cart.value.total = Math.max(cart.value.total - delta, 0)
    if (qty > 1) {
      cart.value.items.splice(idx, 1)
    } else {
      cart.value.items = cart.value.items.filter(i =>
        !(i.variant_sku === product.variant_sku
          && i.delivery_option?.label === product.delivery_option?.label)
      )
      cartOrder.value = cartOrder.value.filter(sku => sku !== product.variant_sku)
    }
    saveCartToServer()
  }

  function getProductQuantity(product) {
    return cart.value.items.filter(i =>
      i.variant_sku === product.variant_sku
      && i.delivery_option?.label === product.delivery_option?.label
    ).length
  }

  function checkout() {
    cart.value = { count: 0, total: 0, items: [] }
    cartOrder.value = []
    saveCartToServer()
  }

  function clearFilters() {
    filterPriceMin.value = null
    filterPriceMax.value = null
    filterSubcat.value   = ''
    filterGender.value   = ''
    filterBrands.value   = []
    filterColors.value   = []
    filterSizes.value    = []
  }

  // -------------------------------------------------
  // Admin / Reviews Actions
  // -------------------------------------------------
  async function fetchUsers() {
    const { data } = await api.get(API.admin.listUsers)
    users.value = data.users
  }

  async function fetchSettings() {
    const { data } = await api.get(API.admin.getSettings)
    settings.value = data.settings
  }

  async function saveSetting(key, value) {
    await api.post(API.admin.updateSetting, { key, value })
  }

  async function deleteSetting(key) {
    await api.delete(`${API.admin.deleteSetting}/${encodeURIComponent(key)}`)
  }

  async function fetchReviews() {
    const { data } = await api.get(API.general.listReviews)
    reviews.value = data.reviews
  }

  async function createReview(formData) {
    const { data } = await api.post(API.admin.createReview, formData)
    return data.message
  }

  async function deleteReview(id) {
    await api.delete(`${API.admin.deleteReview}/${id}`)
    await fetchReviews()
  }

  async function updateUserRole(userId, role) {
    await api.post(API.admin.setUserRole, {
      user_id: userId,
      role:    role,
    })
    await fetchUsers()
  }

  async function loadSheetUrls() {
    const { data } = await api.get(API.admin.getSheetUrls)
    Object.assign(sheetUrls.value, data)
  }

  async function saveSheetUrl(cat) {
    sheetSaveLoading[cat] = true
    sheetResult[cat] = ''
    try {
      await api.post(API.admin.updateSheetUrl, {
        category: cat,
        url: sheetUrls.value[cat]
      })
      sheetResult[cat] = 'Ссылка сохранена'
      return true
    } catch (e) {
      sheetResult[cat] = `Ошибка: ${e.response?.data?.error || e.message}`
      return false
    } finally {
      sheetSaveLoading[cat] = false
    }
  }

  async function importSheet(cat) {
    sheetImportLoading[cat] = true
    sheetResult[cat] = ''
    try {
      const { data } = await api.post(API.admin.importSheet, {
        category: cat,
      })
      if (data.status === 'ok') {
        // Форматируем warn_skus
        const warnSkus = Array.isArray(data.warn_skus) && data.warn_skus.length ? data.warn_skus.join(', ') : 'нет'
        sheetResult[cat] = `Добавлено: ${data.added}. Обновлено: ${data.updated}. Удалено: ${data.deleted}. Ошибки: ${data.warns}. Проблемные SKU: ${warnSkus}`
        await loadLogs()
        return true
      } else {
        sheetResult[cat] = `Ошибка: ${data.error || JSON.stringify(data)}`
        return false
      }
    } catch (e) {
      sheetResult[cat] = `Ошибка сети`
      return false
    } finally {
      sheetImportLoading[cat] = false
    }
  }

  async function previewSheet(cat) {
    previewSheetLoading[cat] = true;
    previewSheetResult[cat] = null;
    try {
      const { data } = await api.post(API.admin.previewSheet, { category: cat });
      previewSheetResult[cat] = data;
    } catch (e) {
      console.error('previewSheet error', e);
      previewSheetResult[cat] = { error: e.message };
    } finally {
      previewSheetLoading[cat] = false;
    }
  }

  async function previewAllSheets() {
    for (const cat of ['shoes','clothing','accessories']) {
      await previewSheet(cat);
    }
  }

  async function loadLogs(limit = 10, offset = 0) {
    logsLoading.value = true
    try {
      const { data } = await api.get(API.admin.getLogs, { params: { limit, offset } })
      logs.value = data.logs
      totalLogs.value  = data.total
    } catch {
      logs.value = []
      totalLogs.value  = 0
    } finally {
      logsLoading.value = false
    }
  }

  async function loadVisits(date) {
    visitsLoading.value = true
    try {
      const { data } = await api.get(API.admin.getDailyVisits, { params: { date } })
      visitsData.value = { date: data.date, hours: data.hours }
    } catch {
      visitsData.value = { date: '', hours: [] }
    } finally {
      visitsLoading.value = false
    }
  }

  async function uploadZip(file) {
    zipLoading.value = true
    zipResult.value = ''
    const form = new FormData()
    form.append('file', file)
    try {
      const { data } = await api.post(API.admin.uploadImages, form)
      zipResult.value = `Добавлено: ${data.added}. Обновлено: ${data.replaced}. Удалено: ${data.deleted}. Ошибки: ${data.warns}.`
      await loadLogs()
    } catch (e) {
      zipResult.value = `Ошибка: ${e.response?.data?.error || e.message}`
    } finally {
      zipLoading.value = false
    }
  }

  async function previewImages(filesMap) {
    Object.keys(previewZipResult).forEach(cat => {
      previewZipResult[cat]  = null;
      previewZipLoading[cat] = false;
    });

    const hasAny = Object.values(filesMap).some(f => f);
    if (!hasAny) {
      Object.keys(previewZipResult).forEach(cat => {
        previewZipResult[cat] = { error: "no archive selected" };
      });
      return;
    }

    const form = new FormData();
    Object.entries(filesMap).forEach(([cat, f]) => {
      if (f) form.append(`file_${cat}`, f);
    });
    Object.keys(previewZipLoading).forEach(cat => {
      previewZipLoading[cat] = true;
    });

    try {
      const { data } = await api.post(API.admin.previewImages, form);
      Object.assign(previewZipResult, data);
    } catch (e) {
      Object.keys(previewZipResult).forEach(cat => {
        previewZipResult[cat] = { error: e.response?.data?.error || e.message };
      });
    } finally {
      Object.keys(previewZipLoading).forEach(cat => {
        previewZipLoading[cat] = false;
      });
    }
  }

  async function previewEverything(filesMap) {
    // запустить оба типа превью параллельно или последовательно, если нужно:
    // 1) очистить предыдущие результаты
    Object.keys(previewSheetResult).forEach(cat => previewSheetResult[cat]=null);
    Object.keys(previewZipResult).forEach(cat  => previewZipResult[cat]  =null);

    // 2) поднять все лоадеры
    Object.keys(previewSheetLoading).forEach(cat=> previewSheetLoading[cat]=true);
    Object.keys(previewZipLoading).forEach(cat=> previewZipLoading[cat]=true);

    try {
      // сначала проверяем Sheets
      await previewAllSheets();
      // затем ZIP
      await previewImages(filesMap);
    } finally {
      // в любом случае выключаем все лоадеры
      Object.keys(previewSheetLoading).forEach(cat=> previewSheetLoading[cat]=false);
      Object.keys(previewZipLoading).forEach(cat=> previewZipLoading[cat]=false);
    }
  }

  async function fetchRequests() {
    const { data } = await api.get(API.admin.listRequests)
    requests.value = data.requests
  }

  async function createRequest(formData) {
    // formData — instance of FormData с полями name, email, sku, agree, file?
    await api.post(API.general.createRequest, formData)
  }

  async function deleteRequest(id) {
    await api.delete(`${API.admin.deleteRequest}/${id}`)
    await fetchRequests()
  }

  // -------------------------------------------------
  // Return state & actions
  // -------------------------------------------------
  return {
    // state
    accessToken, refreshToken, user,
    categoryList, selectedCategory,
    showSubcats, currentSubcatPage, selectedSubcat, subcatListMap,
    sortBy, sortOrder,
    filterPriceMin, filterPriceMax, filterColors, filterGender, filterSubcat, filterBrands, filterSizes,
    products,
    cartOrder, cart, cartLoaded, showCartDrawer,
    favorites, favoritesLoaded,
    sheetUrls, sheetSaveLoading, sheetImportLoading,
    sheetResult, previewSheetResult, previewSheetLoading,
    zipResult, zipLoading, previewZipResult, previewZipLoading,
    logs, logsLoading, totalLogs, requests,
    visitsData, visitsLoading,
    detailData, detailLoading, variants,
    profile, profileLoading, profileError,
    parameters, settings, reviews, users,

    // grouping/computed
    colorGroups, displayedProducts, groupedCartItems, distinctBrands, distinctSizes, distinctColors,

    // helpers
    isTelegramUserId,

    // init/auth
    initializeTelegramUser, initializeVisitorUser, verifyAdminAccess,

    // general
    fetchParameters,

    // product
    fetchProducts, fetchDetail,

    // cart
    openCartDrawer, closeCartDrawer,

    // favorites
    loadFavoritesFromServer,
    addToFavorites, removeFromFavorites, isFavorite,


    // filters/sorting
    changeCategory, openSubcats, backToCats, pickSubcat,

    // cart helpers
    addToCart, increaseQuantity, decreaseQuantity,
    getProductQuantity, checkout, clearFilters,

    // admin / users / settings
    fetchUsers, fetchSettings, saveSetting, deleteSetting, updateUserRole,

    // admin reviews
    fetchReviews, createReview, deleteReview,
    fetchRequests, createRequest, deleteRequest,

    // admin sheets & logs & visits & zip
    loadSheetUrls, saveSheetUrl, importSheet,
    loadLogs, loadVisits, uploadZip, previewEverything,
  }
})
