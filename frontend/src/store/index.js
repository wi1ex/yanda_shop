import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

export const useStore = defineStore('main', () => {
  const admin_id = ref(59404714)
  const url = ref('https://shop.yanda.twc1.net')
  const tg = ref(null)

  const user = ref({
    id: null,
    first_name: null,
    last_name: null,
    username: null,
    photo_url: null
})

  // Категории
  const categoryList = ref(['Одежда', 'Обувь', 'Аксессуары'])
  const selectedCategory = ref('Одежда')

  // Параметры сортировки
  const sortBy = ref('date')
  const sortOrder = ref('desc')

  // Фильтры (цена, цвет)
  const filterPriceMin = ref(null)
  const filterPriceMax = ref(null)
  const filterColor = ref('')

  // Список загруженных товаров (для выбранной категории)
  const products = ref([])

  // Корзина
  const cartOrder = ref([])
  const cart = ref({ count: 0, total: 0, items: [] })

  // Список избранного
  const favoritesOrder = ref([]);
  const favorites = ref({ items: [], count: 0 });
  const favoritesLoaded = ref(false);

  // Флаг, который указывает, что корзина открыта/загружена
  const cartLoaded = ref(false)
  const showCartDrawer = ref(false)

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

  // Загрузка корзины из backend (GET /api/cart?user_id=…)
  async function loadCartFromServer() {
    if (!user.value || !user.value.id || !isTelegramUserId(user.value.id)) {
      cartLoaded.value = true;
      return;
    }

    try {
      const resp = await fetch(`${url.value}/api/cart?user_id=${user.value.id}`);
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

  // Сохранение корзины в backend (POST /api/cart)
  async function saveCartToServer() {
    // Сохраняем только Telegram-пользователя
    if (!user.value || !user.value.id || !isTelegramUserId(user.value.id)) {
      return
    }

    const payload = {
      user_id: user.value.id,
      items: cart.value.items,
      count: cart.value.count,
      total: cart.value.total
    }
    try {
      const resp = await fetch(`${url.value}/api/cart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!resp.ok) {
        console.error('Cannot save cart:', resp.statusText)
      }
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
      const resp = await fetch(`${url.value}/api/favorites?user_id=${user.value.id}`);
      if (!resp.ok) throw new Error(resp.statusText);
      const data = await resp.json();
      favorites.value = data;
      // порядок variant_sku
      favoritesOrder.value = data.items.map(i => i.variant_sku);
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
      const resp = await fetch(`${url.value}/api/favorites`, {
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
  function addToFavorites(product) {
    if (favorites.value.items.find(i => i.variant_sku === product.variant_sku)) return;
    favorites.value.items.push(product);
    favorites.value.count = favorites.value.items.length;
    favoritesOrder.value.push(product.variant_sku);
    saveFavoritesToServer();
  }
  function removeFromFavorites(product) {
    favorites.value.items = favorites.value.items.filter(i => i.variant_sku !== product.variant_sku);
    favorites.value.count = favorites.value.items.length;
    favoritesOrder.value = favoritesOrder.value.filter(sku => sku !== product.variant_sku);
    saveFavoritesToServer();
  }
  function isFavorite(product) {
    return favorites.value.items.some(i => i.variant_sku === product.variant_sku);
  }

  // Будем следить за тем, когда пользователь определится (инициализируется)
  watch(() => user.value?.id, (newId) => {
      if (newId && isTelegramUserId(newId)) {
        loadCartFromServer();
        loadFavoritesFromServer();
      } else {
        cartLoaded.value = true;
        favoritesLoaded.value = true;
      }
    }
  )

  // -------------------------------------------------

  const filteredProducts = computed(() => {
    // работаем со всеми пришедшими товарами сразу
    let list = products.value.slice()
    // фильтр по цене
    if (filterPriceMin.value != null) {
      list = list.filter(p => p.price >= filterPriceMin.value)
    }
    if (filterPriceMax.value != null) {
      list = list.filter(p => p.price <= filterPriceMax.value)
    }
    // фильтр по цвету
    if (filterColor.value) {
      list = list.filter(p => p.color === filterColor.value)
    }
    // сортировка
    const modifier = sortOrder.value === 'asc' ? 1 : -1
    return list.slice().sort((a, b) => {
      if (sortBy.value === 'price') {
        return modifier * (a.price - b.price)
      } else {
        // сортируем по дате создания, ISO-строку парсим корректно
        return modifier * (new Date(a.created_at) - new Date(b.created_at))
      }
    })
  })

  // Группируем товары в корзине по variant_sku, считаем количество и суммарную цену
  const groupedCartItems = computed(() => {
    const map = {};
    for (const item of cart.value.items) {
      const key = item.variant_sku;
      if (!map[key]) {
        map[key] = { ...item, quantity: 0, totalPrice: 0 };
      }
      map[key].quantity++;
      map[key].totalPrice += item.price;
    }
    // Собираем в порядке cartOrder (по variant_sku)
    return cartOrder.value.map(variant_sku => map[variant_sku]).filter(Boolean);
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
    const exist = cart.value.items.find(i => i.variant_sku === product.variant_sku);
    if (exist) {
      increaseQuantity(exist);
    } else {
      cart.value.count++;
      cart.value.total += product.price;
      const id = `${Date.now()}-${Math.random()}`;
      cart.value.items.push({ ...product, id });
      cartOrder.value.push(product.variant_sku);
    }
    saveCartToServer();
  }

  // Увеличить количество выбранного товара в корзине
  function increaseQuantity(item) {
    cart.value.count++
    cart.value.total += item.price
    cart.value.items.push(item)
    saveCartToServer()
  }

  // Уменьшить количество
  function decreaseQuantity(product) {
    const idx = cart.value.items.findIndex(i => i.variant_sku === product.variant_sku)
    if (idx === -1) return

    const qty = cart.value.items.filter(i => i.variant_sku === product.variant_sku).length
    cart.value.count--
    cart.value.total = Math.max(cart.value.total - product.price, 0)

    if (qty > 1) {
      cart.value.items.splice(idx, 1)
    } else {
      cart.value.items = cart.value.items.filter(i => i.variant_sku !== product.variant_sku)
      cartOrder.value = cartOrder.value.filter(variant_sku => variant_sku !== product.variant_sku)
    }
    saveCartToServer()
  }

  // Получить текущее количество единиц товара в корзине
  function getProductQuantity(product) {
    return cart.value.items.filter(i => i.variant_sku === product.variant_sku).length;
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
  async function fetchProducts() {
    try {
      const res = await fetch(`${url.value}/api/products?category=${encodeURIComponent(selectedCategory.value)}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      products.value = await res.json()
    } catch (e) {
      console.error('Не удалось загрузить товары:', e)
    }
  }

  return {
    url,
    tg,
    user,
    admin_id,

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
    showCartDrawer,

    favorites,
    favoritesOrder,
    favoritesLoaded,

    filteredProducts,
    groupedCartItems,

    changeCategory,
    addToCart,
    increaseQuantity,
    decreaseQuantity,
    getProductQuantity,
    checkout,
    clearFilters,
    fetchProducts,
    loadFavoritesFromServer,
    addToFavorites,
    removeFromFavorites,
    isFavorite,
    openCartDrawer,
    closeCartDrawer,
  }
})
