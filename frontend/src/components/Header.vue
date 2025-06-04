<template>
  <header class="header">
    <h1>YANDA SHOP</h1>
    <div class="user-info">
      <img :src="store.user.photo_url || img_bot" alt="avatar" class="avatar" />
      <span class="username">
        {{ store.user.id }}
      </span>
    </div>
    <button class="cart-button" @click="store.toggleCart">
      🛒 {{ store.cart.count }} <span class="cart-total-price">({{ store.cart.total }}₽)</span>
    </button>
  </header>
</template>

<script setup>
import { useStore } from '@/store/index.js'
import img_bot from '@/assets/images/bot.png'

const store = useStore()
</script>


<style scoped lang="scss">
.header {
  @include flex-header;
  background-color: $background-color;
  padding: 2vh 2vw;
  position: fixed;
  top: 0;
  width: calc(100% - 4vw);
  max-height: 10vh;
  z-index: 1000;
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1vh;
  background: $background-color;
}
.avatar {
  width: 4vh;
  height: 4vh;
  border-radius: 100%;
  object-fit: cover;
}
.username {
  font-size: 16px;
  font-weight: bold;
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
