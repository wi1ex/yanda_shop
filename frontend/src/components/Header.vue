<template>
  <header class="header">
    <!-- Кнопка меню -->
    <button class="menu-btn" ref="menuBtn" @click="toggleMenu">
      <img :src="icon_menu" alt="Меню" />
    </button>

    <!-- Логотип (ссылка на главную) -->
    <router-link to="/" class="logo-btn">
      <img :src="icon_logo" alt="Главная" class="logo-icon" />
    </router-link>

    <!-- Иконки действий -->
    <div class="actions">
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
    </div>

    <!-- Выпадающее меню -->
    <transition name="fade">
      <nav v-if="menuOpen" class="dropdown-menu" ref="menu">
        <router-link to="/catalog" class="dropdown-link" @click="closeMenu">Каталог</router-link>
        <router-link to="/about" class="dropdown-link" @click="closeMenu">О нас</router-link>
        <router-link v-if="isAdmin" to="/admin" class="dropdown-link" @click="closeMenu">Админ-панель</router-link>
      </nav>
    </transition>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from '@/store/index.js'
import { useRoute } from 'vue-router'
import icon_default_avatar_grey from '@/assets/images/default_avatar_grey.svg'
import icon_default_avatar_white from '@/assets/images/default_avatar_white.svg'
import icon_favorites_grey from '@/assets/images/favorites_grey.svg'
import icon_favorites_white from '@/assets/images/favorites_white.svg'
import icon_cart_grey from '@/assets/images/cart_grey.svg'
import icon_cart_white from '@/assets/images/cart_white.svg'
import icon_menu_grey from '@/assets/images/menu_grey.svg'
import icon_menu_white from '@/assets/images/menu_white.svg'
import icon_logo_orange from '@/assets/images/logo_orange.svg'
import icon_logo_white from '@/assets/images/logo_white.svg'

const store = useStore()
const route = useRoute()
const menuOpen = ref(false)
const menuBtn = ref(null)
const menu = ref(null)

const isAbout = computed(() => route.name === 'About')
const icon_default_avatar = computed(() => isAbout.value ? icon_default_avatar_white : icon_default_avatar_grey)
const icon_favorites = computed(() => isAbout.value ? icon_favorites_white : icon_favorites_grey)
const icon_cart = computed(() => isAbout.value ? icon_cart_white : icon_cart_grey)
const icon_menu = computed(() => isAbout.value ? icon_menu_white : icon_menu_grey)
const icon_logo = computed(() => isAbout.value ? icon_logo_white : icon_logo_orange)
const isAdmin = computed(() => store.user && store.admin_ids.includes(Number(store.user.id)))

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}
function closeMenu() {
  menuOpen.value = false
}

// Закрыть меню кликом вне
function onClickOutside(e) {
  if (!menuOpen.value) return
  const clickedInsideBtn = menuBtn.value?.contains(e.target)
  const clickedInsideMenu = menu.value?.contains(e.target)
  if (!clickedInsideBtn && !clickedInsideMenu) {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside)
})
</script>

<style scoped lang="scss">
.header {
  @include flex-header;
  position: fixed;
  width: 100%;
  height: 50px;
  z-index: 1000;
}

.menu-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
}

.actions {
  display: flex;
}

.actions img {
  width: 30px;
  height: 30px;
}

.logo-btn {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin: 0;
  padding: 0;
}
.logo-icon {
  height: 32px;
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

/* маленькое выпадающее меню */
.dropdown-menu {
  position: absolute;
  top: calc(1vh + 40px); /* чуть ниже кнопки меню */
  left: 2vw;
  background: $grey-87;
  padding: 8px 0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  min-width: 140px;
  z-index: 1100;
}

.dropdown-link {
  color: #fff;
  text-decoration: none;
  padding: 8px 16px;
  font-size: 14px;
}
.dropdown-link:hover {
  background: rgba(255,255,255,0.1);
}

/* плавное появление */
.fade-enter-active, .fade-leave-active {
  transition: opacity .2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .dropdown-menu {
    left: 1vw;
    min-width: 60%;
  }
}
</style>
