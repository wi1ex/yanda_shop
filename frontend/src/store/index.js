import { defineStore } from 'pinia'
import { computed, ref, watch, reactive } from 'vue'

export const API = {
  baseUrl: ref('https://shop.yanda.twc1.net'),
  general: {
    healthCheck:        '/api/general',                      // GET  - health check
    saveUser:           '/api/general/save_user',            // POST - сохранить/обновить Telegram-пользователя
    getUserProfile:     '/api/general/get_user_profile',     // GET  - получить профиль
    getSocialUrls:      '/api/general/get_social_urls',      // GET  - получить соц. ссылки
  },
  product: {
    listProducts:       '/api/product/list_products',        // GET  - список товаров (фильтр по категории)
    getProduct:         '/api/product/get_product',          // GET  - детали одного товара
    getCart:            '/api/product/get_cart',             // GET  - получить корзину пользователя
    saveCart:           '/api/product/save_cart',            // POST - сохранить корзину
    getFavorites:       '/api/product/get_favorites',        // GET  - получить избранное
    saveFavorites:      '/api/product/save_favorites',       // POST - сохранить избранное
  },
  admin: {
    getAdminIds:        '/api/admin/get_admin_ids',          // GET  - список admin_id
    getDailyVisits:     '/api/admin/get_daily_visits',       // GET  - статистика визитов по часам
    getLogs:            '/api/admin/get_logs',               // GET  - журнал
    getSheetUrls:       '/api/admin/get_sheet_urls',         // GET  - URL Google Sheets
    updateSheetUrl:     '/api/admin/update_sheet_url',       // POST - сохранить URL таблицы
    importSheet:        '/api/admin/import_sheet',           // POST - импорт CSV из Sheets
    uploadImages:       '/api/admin/upload_images',          // POST - загрузка ZIP с изображениями
  }
}

export const useStore = defineStore('main', () => {
  const url = ref('https://shop.yanda.twc1.net')
  const admin_ids = ref([])
  const tg = ref(null)

  const user = ref({
    id: null,
    first_name: null,
    last_name: null,
    username: null,
    photo_url: null
  })

  // Категории
  const categoryList       = ref(['Одежда', 'Обувь', 'Аксессуары'])
  const selectedCategory   = ref('Одежда')

  // Параметры сортировки
  const sortBy             = ref('date')
  const sortOrder          = ref('desc')

  // Фильтры (цена, цвет)
  const filterPriceMin     = ref(null)
  const filterPriceMax     = ref(null)
  const filterColor        = ref('')

  // Список загруженных товаров (для выбранной категории)
  const products           = ref([])

  // Корзина
  const cartOrder          = ref([])
  const cart               = ref({ count: 0, total: 0, items: [] })

  // Список избранного
  const favorites          = ref({ items: [], count: 0 });
  const favoritesOrder     = ref([]);
  const favoritesLoaded    = ref(false);

  // Флаг, который указывает, что корзина открыта/загружена
  const cartLoaded         = ref(false)
  const showCartDrawer     = ref(false)

  // === AdminPage ===
  const sheetUrls          = ref({ shoes: '', clothing: '', accessories: '' })
  const sheetSaveLoading   = reactive({ shoes: false, clothing: false, accessories: false })
  const sheetImportLoading = reactive({ shoes: false, clothing: false, accessories: false })
  const sheetResult        = reactive({ shoes: '', clothing: '', accessories: '' })
  const logs               = ref([])
  const logsLoading        = ref(false)
  const visitsData         = ref({ date: '', hours: [] })
  const visitsLoading      = ref(false)
  const zipResult          = ref('')
  const zipLoading         = ref(false)

  // === ProductPage ===
  const detailData         = ref(null)
  const detailLoading      = ref(false)
  const variants           = ref([])

  // === ProfilePage ===
  const profile            = ref(null)
  const profileLoading     = ref(false)
  const profileError       = ref('')

  const socialUrls         = reactive({ url_telegram: '', url_instagram: '', url_email: '' })

  async function loadSocialUrls() {
    const r = await fetch(`${API.base_url}${API.general.getSocialUrls}`)
    Object.assign(socialUrls, await r.json())
  }

  function openCartDrawer() {
    showCartDrawer.value = true
  }

  function closeCartDrawer() {
    showCartDrawer.value = false
  }

  // helper: true, если user.id можно преобразовать в int (строка из цифр)
  function isTelegramUserId(id) {
    // попытка превратить строку/число в целое
    const asNum = parseInt(id, 10)
    return (!Number.isNaN(asNum) && String(asNum) === String(id))
  }

  async function fetchAdminIds() {
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.getAdminIds}`)
      if (res.ok) {
        const data = await res.json()
        admin_ids.value = data.admin_ids || []
      }
    } catch (e) {
      console.error('Не удалось загрузить admin_ids:', e)
    }
  }

  // Загрузка корзины из backend
  async function loadCartFromServer() {
    if (!user.value || !user.value.id || !isTelegramUserId(user.value.id)) {
      cartLoaded.value = true;
      return;
    }
    try {
      const resp = await fetch(`${API.baseUrl}${API.product.getCart}?user_id=${user.value.id}`);
      if (!resp.ok) {
        console.error('Cannot load cart:', resp.statusText);
        return;
      }
      const data = await resp.json();
      if (data && Array.isArray(data.items)) {
        cart.value.items = data.items;
        cart.value.count = data.count;
        cart.value.total = data.total;
        const vs = data.items.map(i => i.variant_sku);
        cartOrder.value = Array.from(new Set(vs));
      }
      cartLoaded.value = true;
    } catch (e) {
      console.error('Error loading cart from server:', e);
    }
  }

  // Сохранение корзины в backend
  async function saveCartToServer() {
    // Сохраняем только Telegram-пользователя
    if (!user.value?.id || !isTelegramUserId(user.value.id)) return
    const payload = {
      user_id: user.value.id,
      items: cart.value.items.map(i => ({
        variant_sku: i.variant_sku,
        delivery_label: i.delivery_option?.label || null
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

  // Загрузка избранного
  async function loadFavoritesFromServer() {
    if (!user.value?.id || !isTelegramUserId(user.value.id)) {
      favoritesLoaded.value = true;
      return;
    }
    try {
      const resp = await fetch(`${API.baseUrl}${API.product.getFavorites}?user_id=${user.value.id}`);
      if (!resp.ok) throw new Error(resp.statusText);
      const data = await resp.json();
      favorites.value.items = data.items || [];
      favorites.value.count = data.count || favorites.value.items.length;
    } catch (e) {
      console.error('Cannot load favorites:', e);
    } finally {
      favoritesLoaded.value = true;
    }
  }

  // Сохранение избранного
  async function saveFavoritesToServer() {
    if (!user.value?.id || !isTelegramUserId(user.value.id)) return;
    const payload = {
      user_id: user.value.id,
      items: favorites.value.items
    };
    try {
      const resp = await fetch(`${API.baseUrl}${API.product.saveFavorites}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) console.error('Cannot save favorites:', resp.statusText);
    } catch (e) {
      console.error('Error saving favorites:', e);
    }
  }

  // Добавить/удалить из избранного
  function addToFavorites(color_sku) {
    if (favorites.value.items.includes(color_sku)) return;
    favorites.value.items.push(color_sku);
    favorites.value.count = favorites.value.items.length;
    saveFavoritesToServer();
  }
  function removeFromFavorites(color_sku) {
    favorites.value.items = favorites.value.items.filter(cs => cs !== color_sku);
    favorites.value.count = favorites.value.items.length;
    saveFavoritesToServer();
  }
  function isFavorite(color_sku) {
    return favorites.value.items.includes(color_sku);
  }

  async function saveUserToServer() {
    if (!user.value?.id) return
    try {
      await fetch(`${API.baseUrl}${API.general.saveUser}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id:         user.value.id,
          first_name: user.value.first_name,
          last_name:  user.value.last_name,
          username:   user.value.username,
          photo_url:  user.value.photo_url,
        })
      })
    } catch (e) {
      console.error('Не удалось сохранить пользователя:', e)
    }
  }

  // Будем следить за тем, когда пользователь определится (инициализируется)
  watch(() => user.value?.id, (newId) => {
      if (newId) saveUserToServer()
      if (newId && isTelegramUserId(newId)) {
        fetchAdminIds();
        loadCartFromServer();
        loadFavoritesFromServer();
      } else {
        cartLoaded.value = true;
        favoritesLoaded.value = true;
      }
    }
  )

  // -------------------------------------------------

  // Группируем все варианты по color_sku
  const colorGroups = computed(() => {
    const map = {}
    products.value.forEach(p => {
      const key = p.color_sku
      if (!map[key]) map[key] = { color_sku: key, variants: [] }
      map[key].variants.push(p)
    })
    return Object.values(map).map(group => {
      // самый дешёвый вариант
      const minPriceVariant = group.variants.reduce((prev, cur) => prev.price <= cur.price ? prev : cur)
      // самая ранняя дата (строковое сравнение ISO учитывает микросекунды)
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

  // «Отображаемые» продукты: group → фильтрация по цвету, цене и сортировка
  const displayedProducts = computed(() => {
    let list = colorGroups.value.slice()

    // Фильтр по цвету (если задан)
    if (filterColor.value) {
      list = list.filter(g => g.variants[0].color === filterColor.value)
    }
    // Фильтр по цене диапазонам
    if (filterPriceMin.value != null) {
      list = list.filter(g =>
        g.variants.some(v => v.price >= filterPriceMin.value)
      )
    }
    if (filterPriceMax.value != null) {
      list = list.filter(g =>
        g.variants.some(v => v.price <= filterPriceMax.value)
      )
    }
    // Сортировка
    const mod = sortOrder.value === 'asc' ? 1 : -1
    if (sortBy.value === 'price') {
      list.sort((a, b) => mod * (a.minPrice - b.minPrice))
    } else {
      // по дате ISO-строку сравним напрямую, чтобы учесть все знаки
      list.sort((a, b) => mod * a.minDate.localeCompare(b.minDate))
    }
    return list
  })

  // Группируем товары в корзине по variant_sku, считаем количество и суммарную цену
  const groupedCartItems = computed(() => {
    const map = {};
    for (const item of cart.value.items) {
      const key = `${item.variant_sku}_${item.delivery_option?.label}`;
      if (!map[key]) {
        map[key] = { ...item, quantity: 0, totalPrice: 0 };
      }
      map[key].quantity++;
      map[key].totalPrice += item.price;
    }
    // Собираем в порядке cartOrder (по variant_sku)
    return Object.values(map);
  });

  // Меняем категорию (сбрасываем фильтры, сортировку)
  function changeCategory(cat) {
    selectedCategory.value = cat
    sortBy.value = 'date'
    sortOrder.value = 'desc'
    filterPriceMin.value = null
    filterPriceMax.value = null
    filterColor.value = ''
  }

  // Добавить товар в корзину
  function addToCart(product) {
    // рассчитываем цену с учётом выбранной опции доставки, если есть
    const unitPrice = product.computed_price ?? product.price;
    const exist = cart.value.items.find(i => i.variant_sku === product.variant_sku && i.delivery_option?.label === product.delivery_option?.label);
    if (exist) {
      increaseQuantity(exist);
    } else {
      cart.value.count++;
      cart.value.total += unitPrice;
      const id = `${Date.now()}-${Math.random()}`;
      // сохраняем delivery_option и итоговую цену в каждом элементе
      cart.value.items.push({
        ...product,
        id,
        unit_price: unitPrice,
      });
      cartOrder.value.push(product.variant_sku);
    }
    saveCartToServer();
  }

  // Увеличить количество выбранного товара в корзине
  function increaseQuantity(item) {
    cart.value.count++
    cart.value.total += item.unit_price
    cart.value.items.push(item)
    saveCartToServer()
  }

  // Уменьшить количество
  function decreaseQuantity(product) {
    const idx = cart.value.items.findIndex(i => i.variant_sku === product.variant_sku && i.delivery_option?.label === product.delivery_option?.label)
    if (idx === -1) return

    const qty = cart.value.items.filter(i => i.variant_sku === product.variant_sku && i.delivery_option?.label === product.delivery_option?.label).length
    cart.value.count--
    const delta = product.unit_price ?? product.price
    cart.value.total = Math.max(cart.value.total - delta, 0)

    if (qty > 1) {
      cart.value.items.splice(idx, 1)
    } else {
      cart.value.items = cart.value.items.filter(i => !(i.variant_sku === product.variant_sku && i.delivery_option?.label === product.delivery_option?.label))
      cartOrder.value = cartOrder.value.filter(variant_sku => variant_sku !== product.variant_sku)
    }
    saveCartToServer()
  }

  // Получить текущее количество единиц товара в корзине
  function getProductQuantity(product) {
    return cart.value.items.filter(i => i.variant_sku === product.variant_sku && i.delivery_option?.label === product.delivery_option?.label).length;
  }

  // Оформление заказа (тут просто чистим корзину и показываем alert)
  function checkout() {
    cart.value = { count: 0, total: 0, items: [] }
    cartOrder.value = []
    saveCartToServer()
  }

  // Очистить фильтры
  function clearFilters() {
    filterPriceMin.value = null
    filterPriceMax.value = null
    filterColor.value = ''
  }

  // Fetch: загрузка товаров по category
  async function fetchProducts(cat) {
    if (cat) selectedCategory.value = cat
    try {
      const res = await fetch(`${API.baseUrl}${API.product.listProducts}?category=${encodeURIComponent(selectedCategory.value)}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      products.value = await res.json()
    } catch (e) {
      console.error('Не удалось загрузить товары:', e)
    }
  }

  // Загрузка **всех** товаров (для страницы «Избранное»)
  async function fetchAllProducts() {
    try {
      const res = await fetch(`${API.baseUrl}${API.product.listProducts}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      products.value = await res.json()
    } catch (e) {
      console.error('Не удалось загрузить все товары:', e)
    }
  }

  // --- Экшен: загрузить URL таблиц ---
  async function loadSheetUrls() {
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.getSheetUrls}`)
      const data = await res.json()
      Object.assign(sheetUrls.value, data)
    } catch (e) { console.error(e) }
  }

  // --- Экшен: сохранить URL ---
  async function saveSheetUrl(cat) {
    sheetSaveLoading[cat] = true
    sheetResult[cat] = ''
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.updateSheetUrl}`, {
        method:'POST', headers:{'Content-Type':'application/json'},
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

  // --- Экшен: импорт данных из Google Sheets ---
  async function importSheet(cat, authorId, authorName) {
    sheetImportLoading[cat] = true
    sheetResult[cat] = ''
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.importSheet}`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ category: cat, author_id: authorId, author_name: authorName })
      })
      const j = await res.json()
      if (res.ok && j.status==='ok') {
        sheetResult[cat] = `Добавлено: ${j.added}. Обновлено: ${j.updated}. Удалено: ${j.deleted}. Ошибки: ${j.warns}.`
        await loadLogs()
      } else {
        sheetResult[cat] = `Ошибка: ${j.error||res.status}`
      }
    } catch (e) {
      sheetResult[cat] = `Ошибка сети`
    } finally {
      sheetImportLoading[cat] = false
    }
  }

  // --- Экшен: загрузить логи ---
  async function loadLogs(limit = 10) {
    logsLoading.value = true
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.getLogs}?limit=${limit}`)
      logs.value = res.ok ? (await res.json()).logs : []
    } catch (e) {
      console.error(e)
      logs.value = []
    } finally {
      logsLoading.value = false
    }
  }

  // --- Экшен: загрузить статистику посещений ---
  async function loadVisits(date) {
    visitsLoading.value = true
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.getDailyVisits}?date=${date}`)
      const j   = await res.json()
      visitsData.value = { date: j.date, hours: j.hours }
    } catch (e) {
      console.error(e)
      visitsData.value = { date:'', hours:[] }
    } finally {
      visitsLoading.value = false
    }
  }

  // --- Экшен: загрузить ZIP с изображениями ---
  async function uploadZip(file, authorId, authorName) {
    zipLoading.value = true; zipResult.value = ''
    const form = new FormData()
    form.append('file', file)
    form.append('author_id', authorId)
    form.append('author_name', authorName)
    try {
      const res = await fetch(`${API.baseUrl}${API.admin.uploadImages}`, { method:'POST', body: form })
      const j   = await res.json()
      if (res.status===201) {
        zipResult.value = `Добавлено: ${j.added}. Обновлено: ${j.replaced}. Удалено: ${j.deleted}. Ошибки: ${j.warns}.`
        await loadLogs()
      } else {
        zipResult.value = `Ошибка ${res.status}: ${j.error||res.message}`
      }
    } catch (e) {
      zipResult.value = `Ошибка сети`
    } finally {
      zipLoading.value = false
    }
  }

  // --- Экшен: получить детали продукта + варианты ---
  async function fetchDetail(variantSku, category) {
    detailLoading.value = true
    try {
      const pRes = await fetch(`${API.baseUrl}${API.product.getProduct}?category=${encodeURIComponent(category)}&variant_sku=${encodeURIComponent(variantSku)}`)
      detailData.value = await pRes.json()
      // подгружаем весь список и фильтруем по sku
      await fetchProducts(category)
      variants.value = products.value.filter(p => p.sku === detailData.value.sku)
    } catch (e) {
      console.error(e)
    } finally {
      detailLoading.value = false
    }
  }

  // --- Экшен: получить профиль пользователя ---
  async function fetchUserProfile(userId) {
    profileLoading.value = true; profileError.value = ''
    try {
      const res = await fetch(`${API.baseUrl}${API.general.getUserProfile}?user_id=${userId}`)
      if (!res.ok) {
        profileError.value = res.status===404 ? 'Пользователь не найден' : `Ошибка ${res.status}`
        return
      }
      profile.value = await res.json()
    } catch (e) {
      console.error(e)
      profileError.value = 'Ошибка сети'
    } finally {
      profileLoading.value = false
    }
  }

  return {
    url,
    admin_ids,
    tg,
    user,

    categoryList,
    selectedCategory,

    sortBy,
    sortOrder,

    filterPriceMin,
    filterPriceMax,
    filterColor,

    products,

    cartOrder,
    cart,

    favorites,
    favoritesOrder,
    favoritesLoaded,

    cartLoaded,
    showCartDrawer,

    colorGroups,
    displayedProducts,
    groupedCartItems,

    sheetUrls,
    sheetSaveLoading,
    sheetImportLoading,
    sheetResult,
    logs,
    logsLoading,
    visitsData,
    visitsLoading,
    zipResult,
    zipLoading,

    detailData,
    detailLoading,
    variants,

    profile,
    profileLoading,
    profileError,

    socialUrls,

    loadSocialUrls,
    isTelegramUserId,
    changeCategory,
    addToCart,
    increaseQuantity,
    decreaseQuantity,
    getProductQuantity,
    checkout,
    clearFilters,
    fetchProducts,
    fetchAllProducts,
    loadFavoritesFromServer,
    addToFavorites,
    removeFromFavorites,
    isFavorite,
    openCartDrawer,
    closeCartDrawer,
    loadSheetUrls,
    saveSheetUrl,
    importSheet,
    loadLogs,
    loadVisits,
    uploadZip,
    fetchDetail,
    fetchUserProfile,
  }
})
