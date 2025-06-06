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
  const categoryList = ref(['Обувь', 'Одежда', 'Аксессуары'])
  const selectedCategory = ref('Обувь')

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

  // Флаг, который указывает, что корзина загружена из backend
  const cartLoaded = ref(false)

  // helper: true, если user.id можно преобразовать в int (строка из цифр)
  function isTelegramUserId(id) {
    // попытка превратить строку/число в целое
    const asNum = parseInt(id, 10)
    return (!Number.isNaN(asNum) && String(asNum) === String(id))
  }

  // Загрузка корзины из backend (GET /api/cart?user_id=…)
  async function loadCartFromServer() {
    // Только, если это Telegram-ID (целое число в строке/числе) — загружаем из Redis
    if (!user.value || !user.value.id || !isTelegramUserId(user.value.id)) {
      cartLoaded.value = true
      return
    }

    try {
      const resp = await fetch(`${url.value}/api/cart?user_id=${user.value.id}`)
      if (!resp.ok) {
        console.error('Cannot load cart:', resp.statusText)
        return
      }
      const data = await resp.json()
      // Ожидаем: data = { items: [...], count: <int>, total: <int> }
      if (data && Array.isArray(data.items)) {
        cart.value.items = data.items
        cart.value.count = data.count
        cart.value.total = data.total
        // А также восстанавливаем cartOrder – порядок по name:
        cartOrder.value = data.items.map(i => i.name) // упрощённо
      }
      cartLoaded.value = true
    } catch (e) {
      console.error('Error loading cart from server:', e)
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

  // Будем следить за тем, когда пользователь определится (инициализируется)
  watch(
    () => user.value && user.value.id,
    (newId) => {
      if (newId && isTelegramUserId(newId)) {
        loadCartFromServer()
      } else {
        // Если гость (UUID) или пустой, но user.value.id всё равно выставлен,
        // просто говорим, что корзина загружена (пуста) и не грузим ничего из Redis
        cartLoaded.value = true
      }
    }
  )

  // -------------------------------------------------

  const filteredProducts = computed(() => {
    let list = products.value.filter((p) => p.category === selectedCategory.value)
    if (filterPriceMin.value !== null) {
      list = list.filter((p) => p.price >= filterPriceMin.value)
    }
    if (filterPriceMax.value !== null) {
      list = list.filter((p) => p.price <= filterPriceMax.value)
    }
    if (filterColor.value && filterColor.value !== '') {
      list = list.filter((p) => p.color === filterColor.value)
    }
    const modifier = sortOrder.value === 'asc' ? 1 : -1
    return list
      .slice()
      .sort((a, b) => {
        if (sortBy.value === 'price') {
          return modifier * (a.price - b.price)
        } else {
          if (a.created_at < b.created_at) return -1 * modifier
          if (a.created_at > b.created_at) return 1 * modifier
          return 0
        }
      })
  })

  // Группируем товары в корзине по name, считаем количество и суммарную цену
  const groupedCartItems = computed(() => {
    const grouped = []
    for (const item of cart.value.items) {
      const exist = grouped.find((i) => i.name === item.name)
      if (exist) {
        exist.quantity++
        exist.totalPrice += item.price
      } else {
        grouped.push({ ...item, quantity: 1, totalPrice: item.price })
      }
    }
    grouped.sort(
      (a, b) =>
        cartOrder.value.indexOf(a.name) - cartOrder.value.indexOf(b.name)
    )
    return grouped
  })

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
    const exist = cart.value.items.find((i) => i.name === product.name)
    if (exist) {
      increaseQuantity(exist)
    } else {
      cart.value.count++
      cart.value.total += product.price
      const id = `${Date.now()}-${Math.random()}`
      cart.value.items.push({ ...product, id })
      cartOrder.value.push(product.name)
    }
    // Сохраняем сразу после операции
    saveCartToServer()
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
    const idx = cart.value.items.findIndex((i) => i.name === product.name)
    if (idx === -1) return
    const qty = cart.value.items.filter((i) => i.name === product.name).length
    cart.value.count--
    cart.value.total = Math.max(cart.value.total - product.price, 0)
    if (qty > 1) {
      cart.value.items.splice(idx, 1)
    } else {
      cart.value.items = cart.value.items.filter((i) => i.name !== product.name)
      cartOrder.value = cartOrder.value.filter((n) => n !== product.name)
    }
    saveCartToServer()
  }

  // Получить текущее количество единиц товара в корзине
  function getProductQuantity(product) {
    return cart.value.items.filter((i) => i.name === product.name).length
  }

  // Оформление заказа (тут просто чистим корзину и показываем alert)
  function checkout() {
    alert('Заказ оформлен!')
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
  }
})
