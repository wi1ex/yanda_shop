import { reactive, computed } from 'vue'

export const store = reactive({
  // Telegram + пользователь
  url: 'https://shop.yanda.twc1.net',
  tg: null,
  user: null,
  // Категории
  categoryList: ['Кроссовки', 'Одежда', 'Аксессуары'],
  selectedCategory: 'Кроссовки',
  // Список товаров
  products: [],
  // Корзина
  cartOpen: false,
  cartOrder: [],
  cart: { count: 0, total: 0, items: [] },
})

// Выбор товаров по категории
export const filteredProducts = computed(() =>
  store.products
    .filter(p => p.category === store.selectedCategory)
)

// Загружает товары из бэка по выбранной категории
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
  store.selectedCategory = cat
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

// Получить кол-во в корзине
export function getProductQuantity(product) {
  return store.cart.items.filter(i => i.name === product.name).length
}

// Оформить заказ
export function checkout() {
  alert('Заказ оформлен!')
  store.cart = { count: 0, total: 0, items: [] }
  store.cartOrder = []
}
