<template>
  <div class="catalog">
    <!-- Верхнее меню с категориями -->
    <div class="sticky-nav">
      <div class="categories">
        <button v-for="cat in store.categoryList" :key="cat" :class="{ active: cat === store.selectedCategory }" @click="onCategoryClick(cat)">
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
      <button @click="store.clearFilters" class="clear-filters-button">
        Сбросить фильтры
      </button>
    </div>

    <!-- Сетка товаров -->
    <div class="products-grid">
      <div v-for="product in store.filteredProducts" :key="product.variant_sku" class="product-card">
        <!-- Нажатие на карточку — переходим на страницу ProductDetail -->
        <div @click="goToProductDetail(product)" class="clickable-area">
          <img :src="product.image" alt="product" class="product-image" />
          <div class="product-info">
            <p class="product-price">{{ product.price }} ₽</p>
            <p class="product-name">{{ product.name }}</p>
            <p v-if="product.color" class="product-color">
              Цвет: {{ product.color }}
            </p>
          </div>
        </div>

        <!-- Избранное -->
        <button class="favorite-button" v-if="!store.isFavorite(product)" @click.stop="store.addToFavorites(product)">
          В избранное
        </button>
        <button class="favorite-button remove" v-else @click.stop="store.removeFromFavorites(product)">
          Убрать из избранного
        </button>

        <!-- Контролы “+ / – количество” -->
        <div v-if="store.getProductQuantity(product) > 0" class="cart-item-controls">
          <button @click.stop="store.decreaseQuantity(product)">➖</button>
          <span class="item-quantity">
            {{ store.getProductQuantity(product) }}
          </span>
          <button @click.stop="store.increaseQuantity(product)">➕</button>
        </div>

        <!-- Если в корзине нет — показываем “Купить” -->
        <button v-else class="buy-button" @click.stop="store.addToCart(product)">
          В корзину
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch, computed } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

// При монтировании грузим товары
onMounted(store.fetchProducts)

// При изменении выбранной категории — заново грузим товары
watch(
  () => store.selectedCategory,
  () => {
    store.fetchProducts()
  }
)

// Двухсторонняя привязка sortBy и sortOrder
const sortOption = computed({
  get() {
    return `${store.sortBy}_${store.sortOrder}`
  },
  set(value) {
    const [by, order] = value.split('_')
    store.sortBy = by
    store.sortOrder = order
  }
})

// Получаем список уникальных цветов
const distinctColors = computed(() => {
  // берем цвета из всего массива store.products
  const set = new Set(store.products.map(p => p.color).filter(c => c))
  return Array.from(set)
})

function onCategoryClick(cat) {
  store.changeCategory(cat)
}

// Функция: открыть страницу "Карточка товара"
function goToProductDetail(product) {
  router.push({
    name: 'ProductDetail',
    params: { variant_sku: product.variant_sku },
    query: { category: product.category }
  })
}
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
  position: relative;
}

.clickable-area {
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

.favorite-button {
  margin-top: 8px;
  width: 100%;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: #ffc107;
  color: #000;
  cursor: pointer;
  transition: background 0.3s;
}

.favorite-button.remove {
  background: #dc3545;
  color: #fff;
}

</style>
