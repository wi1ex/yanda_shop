<template>
  <div class="cart-container">
    <h2 v-if="store.cart.items.length">Корзина</h2>
    <div v-else class="empty-cart">Корзина пуста</div>

    <ul v-if="store.cart.items.length" class="cart-list">
      <li v-for="item in store.groupedCartItems" :key="item.variant_sku" class="cart-item">
        <img :src="item.image" alt="" class="cart-item-image"/>
        <div class="cart-item-details">
          <p class="cart-item-name">
            {{ item.name }}
          </p>
          <p class="cart-item-variant">
            Артикул: {{ item.variant_sku }}
          </p>
          <p class="cart-item-color">
            Цвет: {{ item.color }}
          </p>
          <p v-if="item.size_label" class="cart-item-size">
            Размер: {{ item.size_label }}
          </p>
          <p class="cart-item-price">
            {{ item.quantity }} шт × {{ item.price }}₽ = {{ item.quantity * item.price }}₽
          </p>
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
      <button class="checkout-button">
        Оформить заказ
      </button>
      <button class="clear-cart-button" @click="store.checkout">
        Очистить корзину
      </button>
    </div>
  </div>
</template>

<script setup>
import { useStore } from '@/store/index.js'
const store = useStore()
</script>

<style scoped lang="scss">

.cart-container {
  padding: 2vh 4vw;
  width: 100%;
  box-sizing: border-box;
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

.cart-item-variant,
.cart-item-color,
.cart-item-size {
  font-size: 12px;
  color: #aaa;
  margin: 2px 0;
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

.clear-cart-button {
  background: #dc3545;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  margin-bottom: 12px;
  cursor: pointer;
}

/* адаптив */
@media (max-width: 600px) {
  .cart-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .cart-item-image {
    height: auto;
    margin-bottom: 8px;
  }
  .cart-item-controls {
    width: 100%;
    justify-content: space-between;
    margin-top: 12px;
  }
  .cart-buttons {
    flex-direction: column;
    gap: 8px;
  }
  .checkout-button,
  .clear-cart-button {
    width: 100%;
    padding: 14px;
  }
}

</style>
