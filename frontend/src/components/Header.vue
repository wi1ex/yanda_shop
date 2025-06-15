<template>
  <header class="header">
    <!-- Hamburger menu -->
    <button class="menu-btn" @click="toggleMenu">
      <img :src="icon_menu" alt="Меню" />
    </button>

    <!-- Logo (home) -->
    <router-link to="/" class="logo-btn">
      <img :src="icon_logo_orange" alt="Главная" class="logo-icon" />
    </router-link>

    <div class="spacer"></div>

    <!-- Action icons -->
    <router-link to="/profile" class="icon-btn" title="Профиль">
      <img :src="store.user.photo_url || icon_default_avatar" alt="Профиль" class="avatar" />
    </router-link>

    <router-link to="/favorites" class="icon-btn" title="Избранное">
      <img :src="icon_favorites" alt="Избранное" />
      <span v-if="store.favorites.count" class="badge">{{ store.favorites.count }}</span>
    </router-link>

    <button class="icon-btn" title="Корзина" @click="store.openCartDrawer()">
      <img :src="icon_cart" alt="Корзина" />
      <span v-if="store.cart.count" class="badge">{{ store.cart.count }}</span>
    </button>

    <!-- Slide-out menu -->
    <transition name="slide">
      <nav v-if="menuOpen" class="side-menu">
        <router-link to="/catalog" class="side-link" @click="toggleMenu">Каталог</router-link>
        <router-link to="/about" class="side-link" @click="toggleMenu">О нас</router-link>
        <router-link v-if="isAdmin" to="/admin" class="side-link" @click="toggleMenu">Админ-панель</router-link>
      </nav>
    </transition>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store/index.js'
import icon_default_avatar from '@/assets/images/default_avatar.svg'
import icon_favorites from '@/assets/images/favorites.svg'
import icon_cart from '@/assets/images/cart.svg'
import icon_menu from '@/assets/images/menu.svg'
import icon_logo_orange from '@/assets/images/logo_orange.svg'

const store = useStore()
const router = useRouter()
const menuOpen = ref(false)
const isAdmin = computed(() => store.user && String(store.user.id) === String(store.admin_id))

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}
</script>

<style scoped lang="scss">

.header {
  @include flex-header;
  position: fixed;
  top: 0;
  width: 100%;
  background-color: $background-color;
  padding: 1vh 2vw;
  z-index: 1000;
}

.menu-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
}

.logo-btn {
  margin: 0 16px;
}
.logo-icon {
  height: 32px;
}

.spacer {
  flex: 1;
}

.icon-btn {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  margin-left: 12px;
  padding: 8px;
  display: flex;
  align-items: center;
}

.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #dc3545;
  color: #fff;
  font-size: 10px;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.side-menu {
  position: fixed;
  top: 0;
  left: 0;
  width: 200px;
  height: 100vh;
  background-color: $background-color;
  padding: 2vh 1vw;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 2px 0 8px rgba(0,0,0,0.2);
}

.side-link {
  color: #fff;
  text-decoration: none;
  font-size: 16px;
  padding: 8px 0;
}

/* slide animation */
.slide-enter-from {
  transform: translateX(-100%);
}
.slide-enter-active {
  transition: transform 0.3s ease;
}
.slide-leave-to {
  transform: translateX(-100%);
}
.slide-leave-active {
  transition: transform 0.3s ease;
}

/* Responsive tweaks */
@media (max-width: 600px) {
  .side-menu {
    width: 70%;
  }
}

</style>
