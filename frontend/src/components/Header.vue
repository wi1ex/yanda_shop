<template>
  <header class="header">
    <div class="top-row">
      <h1 class="logo" @click="goHome">YANDA SHOP</h1>
      <router-link to="/profile" class="user-info">
        <img :src="store.user.photo_url || img_bot" alt="avatar" class="avatar" />
        <span class="username">{{ store.user.username }}</span>
      </router-link>
    </div>

    <nav class="nav-links">
      <router-link to="/" class="nav-link" exact>Главная</router-link>
      <router-link to="/catalog" class="nav-link">Каталог</router-link>
      <router-link to="/cart" class="nav-link">Корзина ({{ store.cart.count }})</router-link>
      <router-link v-if="isAdmin" to="/admin" class="nav-link">Админ-панель</router-link>
    </nav>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'
import img_bot from '@/assets/images/bot.png'

const store = useStore()
const router = useRouter()

// Комьютед: true, если текущий user.id равен ADMIN_ID
const isAdmin = computed(() => {
  return store.user && String(store.user.id) === String(store.admin_id)
})

function goHome() {
  router.push({ name: 'Home' })
}
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

.logo {
  cursor: pointer;
  font-size: 24px;
  color: #fff;
}

.nav-links {
  display: flex;
  gap: 16px;
}

.nav-link {
  color: #fff;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.3s;
}
.nav-link.router-link-active {
  background: #007bff;
}
.nav-link:hover {
  background: #0056b3;
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1vh;
  text-decoration: none;
  color: inherit;
}
.user-info:hover .avatar {
  outline: 2px solid #007bff;
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
</style>
