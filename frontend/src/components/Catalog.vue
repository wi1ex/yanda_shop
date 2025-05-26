<template>
  <div class="catalog">
    <div class="sticky-nav">
      <div class="categories">
        <button
          v-for="cat in store.categoryList"
          :key="cat"
          :class="{ active: cat === store.selectedCategory }"
          @click="changeCategory(cat)"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <h2>{{ store.selectedCategory }}</h2>

    <div class="products-grid">
      <div
        v-for="product in filteredProducts"
        :key="product.name"
        class="product-card"
      >
        <img :src="product.image" alt="product" class="product-image" />
        <div class="product-info">
          <p class="product-price">{{ product.price }} ₽</p>
          <p class="product-name">{{ product.name }}</p>
        </div>

        <div
          v-if="getProductQuantity(product) > 0"
          class="cart-item-controls"
        >
          <button @click="decreaseQuantity(product)">➖</button>
          <span class="item-quantity">{{ getProductQuantity(product) }}</span>
          <button @click="increaseQuantity(product)">➕</button>
        </div>

        <button
          v-else
          class="buy-button"
          @click="addToCart(product)"
        >Купить</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  store,
  filteredProducts,
  changeCategory,
  addToCart,
  getProductQuantity,
  increaseQuantity,
  decreaseQuantity,
} from '@/store.js'
</script>

<style scoped lang="scss">
.catalog {
  margin-top: 170px;
  padding: 20px;
}
.sticky-nav {
  position: fixed;
  top: 116px;
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
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  transition: transform 0.3s ease;
}
.product-image {
  width: 100%;
  border-radius: 10px;
}
.buy-button {
  width: 100%;
  padding: 10px;
  background: #007bff;
  border-radius: 8px;
  margin-top: 8px;
  cursor: pointer;
  transition: 0.3s ease;
}
.cart-item-controls {
  display: flex;
  align-items: center;
  gap: 8px;
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
