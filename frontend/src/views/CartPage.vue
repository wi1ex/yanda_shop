<template>
  <div class="cart-container">
    <h2 v-if="store.cart.items.length">Корзина</h2>
    <div v-else class="empty-cart">Корзина пуста</div>

    <ul v-if="store.cart.items.length" class="cart-list">
      <li v-for="item in store.groupedCartItems" :key="item.variant_sku" class="cart-item">
        <img :src="item.image" alt="" class="cart-item-image" />
        <div class="cart-item-details">
          <p class="cart-item-name">{{ item.name }}</p>
          <p class="cart-item-price">{{ item.totalPrice }}₽</p>
          <div class="cart-item-controls">
            <button @click="store.decreaseQuantity(item)">➖</button>
            <span class="item-quantity">{{ item.quantity }}</span>
            <button @click="store.increaseQuantity(item)">➕</button>
          </div>
        </div>
      </li>
    </ul>

    <p v-if="store.cart.items.length" class="cart-total">
      Итого: {{ store.cart.total }}₽
    </p>

    <div v-if="store.cart.items.length" class="cart-buttons">
      <button class="checkout-button" @click="store.checkout">
        Оформить заказ
      </button>
      <router-link to="/catalog" class="close-cart">
        Вернуться к покупкам
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useStore } from '@/store/index.js'
const store = useStore()
</script>

<style scoped lang="scss">
.cart-container {
  margin-top: 12vh;
  padding: 2vh;
  width: calc(100% - 4vh);
  background-color: $background-color;
}
.empty-cart {
  text-align: center;
  font-size: 16px;
  color: #bbb;
  margin: 20px 0;
}
.cart-list {
  list-style: none;
  padding: 0;
}
.cart-item {
  display: flex;
  align-items: center;
  background: #252a3b;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
}
.cart-item-image {
  width: 50px;
  height: 50px;
  border-radius: 5px;
  object-fit: cover;
}
.cart-item-details {
  flex-grow: 1;
  margin-left: 10px;
}
.cart-item-name {
  font-size: 14px;
  font-weight: bold;
  margin: 0;
}
.cart-item-price {
  font-size: 14px;
  margin: 5px 0;
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
.cart-total {
  font-size: 16px;
  font-weight: bold;
  margin-top: 10px;
}
.cart-buttons {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 16px;
}
.checkout-button {
  background: #28a745;
  color: white;
  padding: 10px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: 0.3s ease;
}
.close-cart {
  background: #dc3545;
  color: white;
  padding: 10px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: 0.3s ease;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
