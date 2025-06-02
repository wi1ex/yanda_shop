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
      <span>Сортировать по:</span>
      <!-- Выбор поля сортировки -->
      <select v-model="store.sortBy" @change="onSortChange">
        <option value="price">Цене</option>
        <option value="date">Дате добавления</option>
      </select>
      <!-- Выбор порядка сортировки -->
      <select v-model="store.sortOrder" @change="onSortChange">
        <option value="asc">По возрастанию</option>
        <option value="desc">По убыванию</option>
      </select>
    </div>

    <!-- Сетка товаров -->
    <div class="products-grid">
      <div v-for="product in filteredProducts" :key="product.sku" class="product-card" @click="selectProduct(product)">
        <img :src="product.image" alt="product" class="product-image" />
        <div class="product-info">
          <p class="product-price">{{ product.price }} ₽</p>
          <p class="product-name">{{ product.name }}</p>
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
import { onMounted, watch } from 'vue'
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
} from '@/store.js'

// При монтировании — первый запрос к API (загрузка товаров выбранной категории)
onMounted(fetchProducts)

// При изменении выбранной категории — запрос к API, но сортировка на фронте
watch(
  () => store.selectedCategory,
  () => {
    fetchProducts()
  }
)

// При смене любого из select (sortBy или sortOrder) просто пересортировать уже загруженный массив
function onSortChange() {
  // так как filteredProducts — computed, оно автоматически пересчитает список
  // Нет необходимости заново вызывать fetchProducts(), потому что меняется только сортировка
  // Единственное, если при смене категории мы сбрасывали сортировку, обновится computed.
}
</script>

<style scoped lang="scss">
.catalog {
  margin-top: 190px;
  padding: 20px;
}

.sticky-nav {
  position: fixed;
  top: 132px;
  left: 8px;
  width: calc(100% - 48px);
  background: $background-color;
  z-index: 999;
  padding: 26px 16px;
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
  margin-top: 100px; /* Отступ, чтобы не перекрывался sticky-nav */
  text-align: center;
  margin-bottom: 16px;
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

.product-card:hover {
  transform: translateY(-4px);
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

.buy-button:hover {
  background: #0056b3;
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
