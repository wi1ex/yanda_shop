import { reactive, computed } from 'vue'

export const store = reactive({
  // Telegram + пользователь
  url: 'https://shop.yanda.twc1.net',
  tg: null,
  user: null,

  // Категории
  categoryList: ['Обувь', 'Одежда', 'Аксессуары'],
  selectedCategory: 'Обувь',

  // Сортировка (фронтенд)
  sortBy: 'date',      // 'date' или 'price'
  sortOrder: 'desc',   // 'asc' или 'desc'

  // Фильтры (фронтенд)
  filterPriceMin: null,    // минимальная цена
  filterPriceMax: null,    // максимальная цена
  filterColor: '',         // выбранный цвет (строка) или '' = без фильтра

  // Список товаров (данные берутся из API один раз при смене категории)
  products: [],

  // Выбранный товар (null, если ничего не выбрано)
  selectedProduct: null,

  // Корзина
  cartOpen: false,
  cartOrder: [],
  cart: { count: 0, total: 0, items: [] },
})

// Фильтрация + сортировка товаров по категории + применённым фильтрам
export const filteredProducts = computed(() => {
  // 1) Оставляем только товары текущей категории
  let list = store.products.filter(
    p => p.category === store.selectedCategory
  )

  // 2) Фильтруем по цене (если указаны)
  if (store.filterPriceMin !== null) {
    list = list.filter(p => p.price >= store.filterPriceMin)
  }
  if (store.filterPriceMax !== null) {
    list = list.filter(p => p.price <= store.filterPriceMax)
  }

  // 3) Фильтруем по цвету (если задан)
  if (store.filterColor && store.filterColor !== '') {
    list = list.filter(p => p.color === store.filterColor)
  }

  // 4) Сортируем полученный массив
  const sorted_list = list.slice().sort((a, b) => {
    // Определяем множитель: для asc = 1, для desc = -1
    const modifier = store.sortOrder === 'asc' ? 1 : -1

    if (store.sortBy === 'price') {
      return modifier * (a.price - b.price)
    } else {
      // сортировка по дате (created_at)
      if (a.created_at < b.created_at) return -1 * modifier
      if (a.created_at > b.created_at) return 1 * modifier
      return 0
    }
  })

  return sorted_list
})

// Загружает товары из бэка по выбранной категории (однократно)
export async function fetchProducts() {
  try {
    const res = await fetch(
      `${store.url}/api/products?category=${encodeURIComponent(store.selectedCategory)}`
    )
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    store.products = await res.json()
  } catch (e) {
    console.error('Не удалось загрузить товары:', e)
  }
}

// Сгруппированные элементы корзины
export const groupedCartItems = computed(() => {
  const grouped = []
  for (const item of store.cart.items) {
    const exist = grouped.find(i => i.name === item.name)
    if (exist) {
      exist.quantity++
      exist.totalPrice += item.price
    } else {
      grouped.push({ ...item, quantity: 1, totalPrice: item.price })
    }
  }
  // Сортировка по порядку добавления
  grouped.sort((a, b) =>
    store.cartOrder.indexOf(a.name) - store.cartOrder.indexOf(b.name)
  )
  return grouped
})

// Изменить категорию
export function changeCategory(cat) {
  // Сбрасываем выбранный товар и фильтры/сортировку
  store.selectedProduct = null
  store.selectedCategory = cat
  // Сбрасываем сортировку на «по дате, убывание»
  store.sortBy = 'date'
  store.sortOrder = 'desc'
  store.filterPriceMin = null
  store.filterPriceMax = null
  store.filterColor = ''
}

// Добавить в корзину
export function addToCart(product) {
  const exist = store.cart.items.find(i => i.name === product.name)
  if (exist) {
    increaseQuantity(exist)
  } else {
    store.cart.count++
    store.cart.total += product.price
    const id = `${Date.now()}-${Math.random()}`
    store.cart.items.push({ ...product, id })
    store.cartOrder.push(product.name)
  }
}

// Переключить корзину
export function toggleCart() {
  // При открытии корзины сбрасываем выбранный товар (если открыт)
  store.selectedProduct = null
  store.cartOpen = !store.cartOpen
}

// Увеличить количество
export function increaseQuantity(item) {
  store.cart.count++
  store.cart.total += item.price
  store.cart.items.push(item)
}

// Уменьшить количество
export function decreaseQuantity(product) {
  const idx = store.cart.items.findIndex(i => i.name === product.name)
  if (idx === -1) return
  const qty = store.cart.items.filter(i => i.name === product.name).length
  store.cart.count--
  store.cart.total = Math.max(store.cart.total - product.price, 0)
  if (qty > 1) {
    store.cart.items.splice(idx, 1)
  } else {
    // последний — удаляем полностью
    store.cart.items = store.cart.items.filter(i => i.name !== product.name)
    store.cartOrder = store.cartOrder.filter(n => n !== product.name)
  }
}

// Получить кол-во товара в корзине
export function getProductQuantity(product) {
  return store.cart.items.filter(i => i.name === product.name).length
}

// Оформить заказ
export function checkout() {
  alert('Заказ оформлен!')
  store.cart = { count: 0, total: 0, items: [] }
  store.cartOrder = []
}

// Выбрать товар и открыть его карточку
export function selectProduct(product) {
  store.selectedProduct = product
  // Переключаем в состояние “открытой карточки” (Cart закрываем)
  store.cartOpen = false
}

// Закрыть карточку товара (вернуться в каталог)
export function clearSelectedProduct() {
  store.selectedProduct = null
}

// Сброс всех фильтров на фронтенде
export function clearFilters() {
  store.filterPriceMin = null
  store.filterPriceMax = null
  store.filterColor = ''
}
