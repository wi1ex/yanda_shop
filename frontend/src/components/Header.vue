<template>
  <header class="header">
    <h1>YANDA SHOP</h1>
    <div class="user-info">
      <img :src="store.user.photo_url" alt="avatar" class="avatar" />
      <span class="username">
        {{ store.user.first_name }} <span class="status">@{{ store.user.username }}</span>
      </span>
    </div>
    <button class="cart-button" @click="toggleCart">
      🛒 {{ store.cart.count }} <span class="cart-total-price">({{ store.cart.total }}₽)</span>
    </button>
  </header>
</template>

<script setup>
import { store, toggleCart } from '@/store.js'
</script>

<style scoped lang="scss">
.header {
  @include flex-header;
  background: $background-color;
  padding: 16px 32px;
  margin: 10px;
  position: fixed;
  top: -10px;
  left: -2px;
  width: calc(100% - 80px);
  z-index: 1000;
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background: $background-color;
  padding: 8px;
  border-radius: 8px;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}
.username {
  font-size: 16px;
  font-weight: bold;
}
.status {
  font-size: 12px;
  color: #00ff88;
  background: rgba(0, 255, 136, 0.2);
  padding: 2px 6px;
  border-radius: 6px;
}
.cart-button {
  background: #007bff;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  border: none;
  transition: 0.3s ease;
}
.cart-total-price {
  font-size: 14px;
  font-weight: bold;
  margin-left: 6px;
}
</style>
