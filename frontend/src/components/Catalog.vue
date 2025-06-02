<template>
  <div class="catalog">
    <!-- Верхнее меню с категориями -->
    <div class="sticky-nav">
      <div class="categories">
        <button v-for="cat in store.categoryList" :key="cat" :class="{ active: cat === store.selectedCategory }" @click="changeCategory(cat)">
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- Заголовок текущей категории -->
    <h2>{{ store.selectedCategory }}</h2>

    <!-- Блок управления сортировкой -->
    <div class="sorting-controls">
      <span>Сортировать:</span>
      <select v-model="sortOption">
        <option value="date_desc">Дата добавления: по убыванию</option>
        <option value="date_asc">Дата добавления: по возрастанию</option>
        <option value="price_asc">Цена: по возрастанию</option>
        <option value="price_desc">Цена: по убыванию</option>
      </select>
    </div>

    <!-- Блок фильтров -->
    <div class="filter-controls">
      <span>Фильтры:</span>

      <!-- Цена: Мин. -->
      <input type="number" v-model.number="store.filterPriceMin" placeholder="Мин. цена" class="filter-input"/>

      <!-- Цена: Макс. -->
      <input type="number" v-model.number="store.filterPriceMax" placeholder="Макс. цена" class="filter-input"/>

      <!-- Цвет -->
      <select v-model="store.filterColor" class="filter-select">
        <option value="">Все цвета</option>
        <option v-for="color in distinctColors" :key="color" :value="color">
          {{ color }}
        </option>
      </select>

      <!-- Кнопка сброса фильтров -->
      <button @click="clearFilters" class="clear-filters-button">Сбросить фильтры</button>
    </div>

    <!-- Сетка товаров -->
    <div class="products-grid">
      <div v-for="product in filteredProducts" :key="product.sku" class="product-card" @click="selectProduct(product)">
        <img :src="product.image" alt="product" class="product-image"/>
        <div class="product-info">
          <p class="product-price">{{ product.price }} ₽</p>
          <p class="product-name">{{ product.name }}</p>
          <p class="product-color" v-if="product.color">Цвет: {{ product.color }}</p>
        </div>

        <div v-if="getProductQuantity(product) > 0" class="cart-item-controls">
          <button @click.stop="decreaseQuantity(product)">➖</button>
          <span class="item-quantity">{{ getProductQuantity(product) }}</span>
          <button @click.stop="increaseQuantity(product)">➕</button>
        </div>

        <button v-else class="buy-button" @click.stop="addToCart(product)">Купить</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch, computed } from 'vue'
import {
  store,
  filteredProducts,
  changeCategory,
  addToCart,
  getProductQuantity,
  increaseQuantity,
  decreaseQuantity,
  fetchProducts,
  selectProduct,
  clearFilters,
} from '@/store.js'

// При монтировании — первый запрос к API (загрузка товаров выбранной категории)
onMounted(fetchProducts)

// При изменении выбранной категории — загрузка «сырых» данных (без фильтров/сортировки)
watch(
  () => store.selectedCategory,
  () => {
    fetchProducts()
  }
)

// Вычисляемое свойство для объединённого селекта
const sortOption = computed({
  get() {
    // Объединяем текущие значения sortBy и sortOrder в одну строку
    return `${store.sortBy}_${store.sortOrder}`
  },
  set(value) {
    // value будет что-то вроде "price_asc" или "date_desc"
    const [by, order] = value.split('_')
    store.sortBy = by       // либо 'date', либо 'price'
    store.sortOrder = order // либо 'asc', либо 'desc'
    // Возникает реактивная перестройка filteredProducts автоматически
  }
})

// Список всех цветов, которые есть у товаров в текущей категории
const distinctColors = computed(() => {
  const byCategory = store.products.filter(
    p => p.category === store.selectedCategory
  )
  // Собираем уникальные цвета
  const set = new Set(byCategory.map(p => p.color).filter(c => c))
  return Array.from(set)
})
</script>

<style scoped lang="scss">
.catalog {
  margin-top: 15vh;
  padding: 2vw;
}

.sticky-nav {
  position: fixed;
  top: 12vh;
  left: 0;
  padding: 2vh 2vw;
  width: calc(100% - 4vw);
  background-color: $background-color;
  z-index: 999;
}

.categories {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.categories button {
  padding: 10px;
  border-radius: 8px;
  background: #252a3b;
  color: white;
  transition: 0.3s ease;
}

.categories button.active {
  background: #007bff;
  color: #ffffff;
}

h2 {
  margin-top: 5vh;
  text-align: center;
}

/* Блок сортировки */
.sorting-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.sorting-controls select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: #ffffff;
  cursor: pointer;
}

/* Блок фильтров */
.filter-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-input {
  width: 100px;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.filter-select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: #ffffff;
  cursor: pointer;
}

.clear-filters-button {
  padding: 6px 12px;
  background: #dc3545;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.3s ease;
}

/* Сетка товаров */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(135px, 1fr));
  gap: 16px;
}

.product-card {
  background: $background-color;
  border-radius: 15px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  cursor: pointer;
}

.product-image {
  width: 100%;
  border-radius: 10px;
}

.product-info {
  margin-top: 8px;
}

.product-price {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.product-name {
  font-size: 14px;
  color: #555;
  margin-top: 4px;
}

.product-color {
  font-size: 12px;
  color: #777;
  margin-top: 2px;
}

.buy-button {
  width: 100%;
  padding: 10px;
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 8px;
  margin-top: 8px;
  cursor: pointer;
  transition: 0.3s ease;
}

.cart-item-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
}

.cart-item-controls button {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.item-quantity {
  font-size: 16px;
  font-weight: bold;
  padding: 4px 8px;
  background: #007bff;
  color: white;
  border-radius: 5px;
}
</style>
