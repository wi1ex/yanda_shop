import { defineStore } from 'pinia'
import { computed, reactive, ref, watch } from 'vue'

export const API = {
  baseUrl: 'https://shop.yanda.twc1.net',
  general: {
    healthCheck:        '/api/general',                      // GET    - health check
    saveUser:           '/api/general/save_user',            // POST   - сохранить/обновить Telegram-пользователя
    getUserProfile:     '/api/general/get_user_profile',     // GET    - получить профиль
    getParameters:      '/api/general/get_parameters',       // GET    - получить публичные настройки
    listReviews:        '/api/general/list_reviews',         // GET    - получить список отзывов
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
    uploadImages:       '/api/admin/upload_images',          // POST   - загрузка ZIP с изображениями
    getSettings:        '/api/admin/get_settings',           // GET    - получить список настроек
    updateSetting:      '/api/admin/update_setting',         // POST   - изменить список настроек
    createReview:       '/api/admin/create_review',          // POST   - загрузить новый отзыв
    deleteReview:       '/api/admin/delete_review',          // DELETE - удалить отзыв
    listUsers:          '/api/admin/list_users',             // GET    - получить список пользователей
  }
}

export const useStore = defineStore('main', () => {
  // -------------------------------------------------
  // State
  // -------------------------------------------------
  const adminToken         = ref(localStorage.getItem('adminToken') || '')
  const user               = ref({
    id: null,
    first_name: '',
    last_name: '',
    username: '',
    role: 'visitor',
    photo_url: null
  })

  // Категории
  const categoryList       = ref(['Одежда', 'Обувь', 'Аксессуары'])
  const selectedCategory   = ref('Одежда')

  // Сортировка
  const sortBy             = ref('date')
  const sortOrder          = ref('desc')

  // Фильтры
  const filterPriceMin     = ref(null)
  const filterPriceMax     = ref(null)
  const filterColor        = ref('')

  // Товары
  const products           = ref([])

  // Корзина
  const cartOrder          = ref([])
  const cart               = ref({ count: 0, total: 0, items: [] })
  const cartLoaded         = ref(false)
  const showCartDrawer     = ref(false)

  // Избранное
  const favorites          = ref({ items: [], count: 0 })
  const favoritesLoaded    = ref(false)

  // === AdminPage ===
  const sheetUrls          = ref({ shoes: '', clothing: '', accessories: '' })
  const sheetResult        = reactive({ shoes: '', clothing: '', accessories: '' })
  const sheetSaveLoading   = reactive({ shoes: false, clothing: false, accessories: false })
  const sheetImportLoading = reactive({ shoes: false, clothing: false, accessories: false })

  const zipResult          = ref('')
  const zipLoading         = ref(false)

  const logs               = ref([])
  const logsLoading        = ref(false)
  const totalLogs          = ref(0)

  const visitsData         = ref({ date: '', hours: [] })
  const visitsLoading      = ref(false)

  // === ProductPage ===
  const detailData         = ref(null)
  const detailLoading      = ref(false)
  const variants           = ref([])

  // === ProfilePage ===
  const profile            = ref(null)
  const profileLoading     = ref(false)
  const profileError       = ref('')

  const parameters         = reactive({})

  const settings           = ref([])
  const reviews            = ref([])
  const users              = ref([])

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

  // -------------------------------------------------
  // Helpers
  // -------------------------------------------------
  function isTelegramUserId(id) {
    const asNum = parseInt(id, 10)
    return (!Number.isNaN(asNum) && String(asNum) === String(id))
  }

  function setAdminToken(token) {
    adminToken.value = token
    localStorage.setItem('adminToken', token)
  }

  // -------------------------------------------------
  // Auth / Init
  // -------------------------------------------------
  async function saveUserToServer(payload) {
    if (!payload?.id) return
    try {
      await fetch(`${API.baseUrl}${API.general.saveUser}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
    } catch (e) {
      console.error('Не удалось сохранить TG пользователя:', e)
    }
  }

  async function fetchUserProfile(userId) {
    profileLoading.value = true
    profileError.value   = ''
    try {
      const res = await fetch(`${API.baseUrl}${API.general.getUserProfile}?user_id=${userId}`)
      if (!res.ok) {
        profileError.value = res.status === 404 ? 'Пользователь не найден' : `Ошибка ${res.status}`
        return
      }
      return await res.json()
    } catch (e) {
      console.error(e)
      profileError.value = 'Ошибка сети'
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
        setAdminToken(profileData.access_token)
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
    const res = await fetch(`${API.baseUrl}${API.general.getParameters}`)
    Object.assign(parameters, await res.json())
  }

  // -------------------------------------------------
  // Product Actions
  // -------------------------------------------------
  async function fetchProducts(cat = null) {
    if (cat) selectedCategory.value = cat
    try {
      const url = cat ? `?category=${encodeURIComponent(cat)}` : ''
      const res = await fetch(`${API.baseUrl}${API.product.listProducts}${url}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      products.value = await res.json()
    } catch (e) {
      console.error('Не удалось загрузить товары:', e)
    }
  }

  async function fetchDetail(variantSku, category) {
    detailLoading.value = true
    try {
      const pRes = await fetch(
        `${API.baseUrl}${API.product.getProduct}?category=${encodeURIComponent(category)}&variant_sku=${encodeURIComponent(variantSku)}`
      )
      detailData.value = await pRes.json()
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
      const resp = await fetch(`${API.baseUrl}${API.product.getCart}?user_id=${user.value.id}`)
      if (!resp.ok) {
        console.error('Cannot load cart:', resp.statusText)
        return
      }
      const data = await resp.json()
      if (data.items) {
        cart.value.items = data.items
        cart.value.count = data.count
        cart.value.total = data.total
        cartOrder.value = Array.from(new Set(data.items.map(i => i.variant_sku)))
      }
      cartLoaded.value = true
    } catch (e) {
      console.error('Error loading cart from server:', e)
    }
  }

  async function saveCartToServer() {
    if (!user.value?.id || !isTelegramUserId(user.value.id)) return
    const payload = {
      user_id: user.value.id,
      items: cart.value.items.map(i => ({
        variant_sku:     i.variant_sku,
        delivery_label:  i.delivery_option?.label || null
      }))
    }
    try {
      await fetch(`${API.baseUrl}${API.product.saveCart}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
    } catch (e) {
      console.error('Error saving cart to server:', e)
    }
  }

  function openCartDrawer() {
    showCartDrawer.value = true
  }
  function closeCartDrawer() {
    showCartDrawer.value = false
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
      const resp = await fetch(`${API.baseUrl}${API.product.getFavorites}?user_id=${user.value.id}`)
      if (!resp.ok) throw new Error(resp.statusText)
      const data = await resp.json()
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
    const payload = { user_id: user.value.id, items: favorites.value.items }
    try {
      const resp = await fetch(`${API.baseUrl}${API.product.saveFavorites}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!resp.ok) console.error('Cannot save favorites:', resp.statusText)
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
  const colorGroups = computed(() => {
    const map = {}
    products.value.forEach(p => {
      const key = p.color_sku
      if (!map[key]) map[key] = { color_sku: key, variants: [] }
      map[key].variants.push(p)
    })
    return Object.values(map).map(group => {
      const minPriceVariant = group.variants.reduce((prev, cur) => prev.price <= cur.price ? prev : cur)
      const minDateVariant  = group.variants.reduce((prev, cur) => prev.created_at <= cur.created_at ? prev : cur)
      return {
        color_sku:      group.color_sku,
        variants:       group.variants,
        minPriceVariant,
        minDateVariant,
        minPrice:       minPriceVariant.price,
        minDate:        minDateVariant.created_at
      }
    })
  })

  const displayedProducts = computed(() => {
    let list = colorGroups.value.slice()
    if (filterColor.value) {
      list = list.filter(g => g.variants[0].color === filterColor.value)
    }
    if (filterPriceMin.value != null) {
      list = list.filter(g => g.variants.some(v => v.price >= filterPriceMin.value))
    }
    if (filterPriceMax.value != null) {
      list = list.filter(g => g.variants.some(v => v.price <= filterPriceMax.value))
    }
    const mod = (sortOrder.value === 'asc' ? 1 : -1)
    if (sortBy.value === 'price') {
      list.sort((a, b) => mod * (a.minPrice - b.minPrice))
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

  function changeCategory(cat) {
    selectedCategory.value = cat
    sortBy.value = 'date'
    sortOrder.value = 'desc'
    filterPriceMin.value = null
    filterPriceMax.value = null
    filterColor.value = ''
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
    filterColor.value = ''
  }

  // -------------------------------------------------
  // Admin / Reviews Actions
  // -------------------------------------------------
  async function fetchUsers() {
    const res = await fetch(`${API.baseUrl}${API.admin.listUsers}`, {
      headers: { 'Authorization': `Bearer ${adminToken.value}` }
    })
    if (res.ok) {
      const j = await res.json()
      users.value = j.users
    }
  }

  async function fetchSettings() {
    const res = await fetch(`${API.baseUrl}${API.admin.getSettings}`, {
      headers: { 'Authorization': `Bearer ${adminToken.value}` }
    })
    if (res.ok) settings.value = (await res.json()).settings
  }

  async function saveSetting(key, value) {
    await fetch(`${API.baseUrl}${API.admin.updateSetting}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken.value}`
      },
      body: JSON.stringify({ key, value })
    })
  }

  async function fetchReviews() {
    const res = await fetch(`${API.baseUrl}${API.general.listReviews}`)
    if (res.ok) {
      const j = await res.json()
      reviews.value = j.reviews.map(r => ({ ...r, }))
    }
  }

  async function createReview(formData) {
    const res = await fetch(`${API.baseUrl}${API.admin.createReview}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${adminToken.value}` },
      body: formData
    })
    const j = await res.json()
    if (!res.ok) {
      throw new Error(j.error || 'Неизвестная ошибка')
    }
    return j.message
  }

  async function deleteReview(id) {
    const res = await fetch(`${API.baseUrl}${API.admin.deleteReview}/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${adminToken.value}` }
    })
    if (!res.ok) {
      const j = await res.json()
      throw new Error(j.error || res.status)
    }
    await fetchReviews()
  }

  async function updateUserRole(userId, role) {
    const res = await fetch(`${API.baseUrl}${API.admin.setUserRole}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken.value}`
      },
      body: JSON.stringify({ user_id: userId, role: role, author_id: user.value.id, author_name: user.value.username })
    })
    if (!res.ok) {
      const j = await res.json()
      throw new Error(j.error || 'Ошибка смены роли')
    }
    await fetchUsers()
  }

  async function loadSheetUrls() {
    const res = await fetch(`${API.baseUrl}${API.admin.getSheetUrls}`, {
      headers: { 'Authorization': `Bearer ${adminToken.value}` }
    })
    const data = await res.json()
    Object.assign(sheetUrls.value, data)
  }

  async function saveSheetUrl(cat) {
    sheetSaveLoading[cat] = true
    sheetResult[cat] = ''
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.updateSheetUrl}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken.value}`
        },
        body: JSON.stringify({ category: cat, url: sheetUrls.value[cat] })
      })
      const j = await res.json()
      if (res.ok) {
        sheetResult[cat] = 'Ссылка сохранена'
        return true
      } else {
        sheetResult[cat] = `Ошибка: ${j.error || res.status}`
        return false
      }
    } catch (e) {
      sheetResult[cat] = `Ошибка сети`
      return false
    } finally {
      sheetSaveLoading[cat] = false
    }
  }

  async function importSheet(cat) {
    sheetImportLoading[cat] = true
    sheetResult[cat] = ''
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.importSheet}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken.value}`
        },
        body: JSON.stringify({ category: cat, author_id: user.value.id, author_name: user.value.username })
      })
      const j = await res.json()
      if (res.ok && j.status === 'ok') {
        sheetResult[cat] = `Добавлено: ${j.added}. Обновлено: ${j.updated}. Удалено: ${j.deleted}. Ошибки: ${j.warns}.`
        await loadLogs()
      } else {
        sheetResult[cat] = `Ошибка: ${j.error || res.status}`
      }
    } catch (e) {
      sheetResult[cat] = `Ошибка сети`
    } finally {
      sheetImportLoading[cat] = false
    }
  }

  async function loadLogs(limit = 25, offset = 0) {
    logsLoading.value = true
    try {
      const url = new URL(`${API.baseUrl}${API.admin.getLogs}`, window.location.origin)
      url.searchParams.set('limit',  limit)
      url.searchParams.set('offset', offset)
      const res = await fetch(url.toString(), {
        headers: { 'Authorization': `Bearer ${adminToken.value}` }
      })
      if (!res.ok) throw new Error(res.statusText)
      const data = await res.json()
      logs.value      = data.logs
      totalLogs.value = data.total
    } catch (e) {
      console.error('loadLogs:', e)
      logs.value      = []
      totalLogs.value = 0
    } finally {
      logsLoading.value = false
    }
  }

  async function loadVisits(date) {
    visitsLoading.value = true
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.getDailyVisits}?date=${date}`, {
        headers: { 'Authorization': `Bearer ${adminToken.value}` }
      })
      const j = await res.json()
      visitsData.value = { date: j.date, hours: j.hours }
    } catch (e) {
      console.error(e)
      visitsData.value = { date: '', hours: [] }
    } finally {
      visitsLoading.value = false
    }
  }

  async function uploadZip(file) {
    zipLoading.value = true
    zipResult.value  = ''
    const form = new FormData()
    form.append('file', file)
    form.append('author_id', user.value.id)
    form.append('author_name', user.value.username)
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.uploadImages}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${adminToken.value}` },
        body: form
      })
      const j = await res.json()
      if (res.status === 201) {
        zipResult.value = `Добавлено: ${j.added}. Обновлено: ${j.replaced}. Удалено: ${j.deleted}. Ошибки: ${j.warns}.`
        await loadLogs()
      } else {
        zipResult.value = `Ошибка ${res.status}: ${j.error || j.message}`
      }
    } catch (e) {
      zipResult.value = `Ошибка сети`
    } finally {
      zipLoading.value = false
    }
  }

  // -------------------------------------------------
  // Return state & actions
  // -------------------------------------------------
  return {
    // state
    adminToken, user,
    categoryList, selectedCategory,
    sortBy, sortOrder,
    filterPriceMin, filterPriceMax, filterColor,
    products,
    cartOrder, cart, cartLoaded, showCartDrawer,
    favorites, favoritesLoaded,
    sheetUrls, sheetSaveLoading, sheetImportLoading, sheetResult,
    zipResult, zipLoading,
    logs, logsLoading, totalLogs,
    visitsData, visitsLoading,
    detailData, detailLoading, variants,
    profile, profileLoading, profileError, parameters,
    settings, reviews, users,

    // helpers
    isTelegramUserId, setAdminToken,

    // init/auth
    saveUserToServer, fetchUserProfile,
    initializeTelegramUser, initializeVisitorUser,

    // general
    fetchParameters,

    // product
    fetchProducts, fetchDetail,

    // cart
    loadCartFromServer, saveCartToServer,
    openCartDrawer, closeCartDrawer,

    // favorites
    loadFavoritesFromServer, saveFavoritesToServer,
    addToFavorites, removeFromFavorites, isFavorite,

    // grouping/computed
    colorGroups, displayedProducts, groupedCartItems,

    // filters/sorting
    changeCategory,

    // cart helpers
    addToCart, increaseQuantity, decreaseQuantity,
    getProductQuantity, checkout, clearFilters,

    // admin / users / settings
    fetchUsers, fetchSettings, saveSetting, updateUserRole,

    // admin reviews
    fetchReviews, createReview, deleteReview,

    // admin sheets & logs & visits & zip
    loadSheetUrls, saveSheetUrl, importSheet,
    loadLogs, loadVisits, uploadZip,
  }
})
