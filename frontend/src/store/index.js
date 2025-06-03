import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

export const useStore = defineStore('main', () => {
  // state
  const url = ref('https://shop.yanda.twc1.net')
  const tg = ref(null)
  const user = ref(null)

  const categoryList = ref(['Обувь', 'Одежда', 'Аксессуары'])
  const selectedCategory = ref('Обувь')

  const sortBy = ref('date')
  const sortOrder = ref('desc')

  const filterPriceMin = ref(null)
  const filterPriceMax = ref(null)
  const filterColor = ref('')

  const products = ref([])

  const selectedProduct = ref(null)

  const cartOpen = ref(false)
  const cartOrder = ref([])
  const cart = ref({ count: 0, total: 0, items: [] })

  // getters
  const filteredProducts = computed(() => {
    let list = products.value.filter(p => p.category === selectedCategory.value)

    if (filterPriceMin.value !== null) {
      list = list.filter(p => p.price >= filterPriceMin.value)
    }
    if (filterPriceMax.value !== null) {
      list = list.filter(p => p.price <= filterPriceMax.value)
    }
    if (filterColor.value && filterColor.value !== '') {
      list = list.filter(p => p.color === filterColor.value)
    }

    const modifier = sortOrder.value === 'asc' ? 1 : -1

    return list.slice().sort((a, b) => {
      if (sortBy.value === 'price') {
        return modifier * (a.price - b.price)
      } else {
        if (a.created_at < b.created_at) return -1 * modifier
        if (a.created_at > b.created_at) return 1 * modifier
        return 0
      }
    })
  })

  const groupedCartItems = computed(() => {
    const grouped = []
    for (const item of cart.value.items) {
      const exist = grouped.find(i => i.name === item.name)
      if (exist) {
        exist.quantity++
        exist.totalPrice += item.price
      } else {
        grouped.push({ ...item, quantity: 1, totalPrice: item.price })
      }
    }
    grouped.sort((a, b) => cartOrder.value.indexOf(a.name) - cartOrder.value.indexOf(b.name))
    return grouped
  })

  // actions
  function changeCategory(cat) {
    selectedProduct.value = null
    selectedCategory.value = cat
    sortBy.value = 'date'
    sortOrder.value = 'desc'
    filterPriceMin.value = null
    filterPriceMax.value = null
    filterColor.value = ''
  }

  function addToCart(product) {
    const exist = cart.value.items.find(i => i.name === product.name)
    if (exist) {
      increaseQuantity(exist)
    } else {
      cart.value.count++
      cart.value.total += product.price
      const id = `${Date.now()}-${Math.random()}`
      cart.value.items.push({ ...product, id })
      cartOrder.value.push(product.name)
    }
  }

  function toggleCart() {
    selectedProduct.value = null
    cartOpen.value = !cartOpen.value
  }

  function increaseQuantity(item) {
    cart.value.count++
    cart.value.total += item.price
    cart.value.items.push(item)
  }

  function decreaseQuantity(product) {
    const idx = cart.value.items.findIndex(i => i.name === product.name)
    if (idx === -1) return
    const qty = cart.value.items.filter(i => i.name === product.name).length
    cart.value.count--
    cart.value.total = Math.max(cart.value.total - product.price, 0)
    if (qty > 1) {
      cart.value.items.splice(idx, 1)
    } else {
      cart.value.items = cart.value.items.filter(i => i.name !== product.name)
      cartOrder.value = cartOrder.value.filter(n => n !== product.name)
    }
  }

  function getProductQuantity(product) {
    return cart.value.items.filter(i => i.name === product.name).length
  }

  function checkout() {
    alert('Заказ оформлен!')
    cart.value = { count: 0, total: 0, items: [] }
    cartOrder.value = []
  }

  function selectProduct(product) {
    selectedProduct.value = product
    cartOpen.value = false
  }

  function clearSelectedProduct() {
    selectedProduct.value = null
  }

  function clearFilters() {
    filterPriceMin.value = null
    filterPriceMax.value = null
    filterColor.value = ''
  }

  async function fetchProducts() {
    try {
      const res = await fetch(
        `${url.value}/api/products?category=${encodeURIComponent(selectedCategory.value)}`
      )
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

    categoryList,
    selectedCategory,

    sortBy,
    sortOrder,

    filterPriceMin,
    filterPriceMax,
    filterColor,

    products,

    selectedProduct,

    cartOpen,
    cartOrder,
    cart,

    filteredProducts,
    groupedCartItems,

    changeCategory,
    addToCart,
    toggleCart,
    increaseQuantity,
    decreaseQuantity,
    getProductQuantity,
    checkout,
    selectProduct,
    clearSelectedProduct,
    clearFilters,
    fetchProducts,
  }
})
