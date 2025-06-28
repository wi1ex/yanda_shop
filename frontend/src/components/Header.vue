<template>
  <header class="header">
    <!-- Кнопка меню -->
    <div class="actions">
      <button class="icon-btn" ref="menuBtn" @click="toggleMenu">
        <img :src="icon_menu" alt="Меню" />
      </button>
    </div>

    <!-- Логотип (ссылка на главную) -->
    <router-link to="/">
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
      <button @click="store.openCartDrawer()" class="icon-btn" title="Корзина">
        <img :src="icon_cart" alt="Корзина" />
        <span v-if="store.cart.count" class="badge">{{ store.cart.count }}</span>
      </button>
    </div>

    <!-- Выпадающее меню -->
    <transition name="fade">
      <nav v-if="menuOpen" class="dropdown-menu" ref="menu">
        <router-link to="/catalog" class="dropdown-link" @click="toggleMenu">Каталог</router-link>
        <router-link to="/about" class="dropdown-link" @click="toggleMenu">О нас</router-link>
        <router-link v-if="isAdmin" to="/admin" class="dropdown-link" @click="toggleMenu">Админ-панель</router-link>
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
const menu = ref(null)
const menuBtn = ref(null)
const menuOpen = ref(false)
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

// Закрыть меню кликом вне
function onClickOutside(e) {
  if (!menuOpen.value) return
  const clickedInsideBtn = menuBtn.value?.contains(e.target)
  const clickedInsideMenu = menu.value?.contains(e.target)
  if (!clickedInsideBtn && !clickedInsideMenu) {
    menuOpen.value = false
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
  @include flex-c-sb;
  position: fixed;
  width: calc(100% - 20px);
  height: 30px;
  padding: 10px;
  z-index: 1000;
  .actions {
    @include flex-c-l;
    width: 114px;
    gap: 12px;
    .icon-btn {
      @include flex-c-c;
      margin: 0;
      padding: 0;
      background: none;
      border: none;
      cursor: pointer;
      .avatar {
        border-radius: 50%;
        object-fit: cover;
      }
      .badge {
        @include flex-c-c;
        position: absolute;
        top: 8px;
        right: 8px;
        width: 14px;
        height: 12px;
        border-radius: 1px;
        background-color: $grey-20;
        color: $white-100;
        font-size: 10px;
        line-height: 100%;
        letter-spacing: -0.2px;
      }
    }
    img {
      width: 30px;
      height: 30px;
    }
  }
  .logo-icon {
    width: 35px;
    height: 30px;
  }
}

/* маленькое выпадающее меню */
.dropdown-menu {
  display: flex;
  flex-direction: column;
  position: absolute;
  top: calc(1vh + 40px);
  left: 2vw;
  padding: 8px 0;
  width: 140px;
  background-color: $grey-20;
  border-radius: 4px;
  box-shadow: 0 2px 8px $black-25;
  z-index: 1100;
  .dropdown-link {
    padding: 8px 16px;
    color: $white-100;
    font-size: 14px;
    text-decoration: none;
  }
  .dropdown-link:hover {
    background-color: $white-10;
  }
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

//@media (max-width: 600px) {
//
//}

</style>
