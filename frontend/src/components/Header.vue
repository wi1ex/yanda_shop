<template>
  <header class="header">
    <!-- Логотип (ссылка на главную) -->
    <div class="actions">
      <div @click="goToPage('Home')" class="icon-btn" title="Лого">
        <img :src="icon_logo" alt="Главная" class="logo-icon" />
      </div>
    </div>

    <!-- Кнопка меню -->
    <div class="menu">
      <button class="menu-btn" @click="toggleMenu()">
        Меню
        <img :src="icon_menu_grey" alt="Меню" />
      </button>
    </div>

    <!-- Иконки действий -->
    <div class="actions">
      <div @click="goToPage('Profile')" class="icon-btn" title="Профиль">
        <img :src="store.user.photo_url || icon_default_avatar" alt="Профиль" class="avatar" />
      </div>
      <div @click="goToPage('Favorites')" class="icon-btn" title="Избранное">
        <img :src="icon_favorites" alt="Избранное" />
        <span v-if="store.favorites.count" class="badge badge-fav">
          {{ store.favorites.count < 10 ? store.favorites.count : "9+" }}
        </span>
      </div>
      <button @click="store.openCartDrawer()" class="icon-btn" title="Корзина">
        <img :src="icon_cart" alt="Корзина" />
        <span v-if="store.cart.count" class="badge badge-cart">
          {{ store.cart.count < 10 ? store.cart.count : "9+"}}
        </span>
      </button>
    </div>

    <!-- Выпадающее меню -->
    <transition name="fade">
      <nav v-if="menuOpen" class="dropdown-menu">
        <div class="dropdown-menu-top">
          <button class="dropdown-menu-btn" @click="toggleMenu()">
            Меню
            <img :src="icon_close" alt="Меню" />
          </button>
          <div @click="goToGender('M')" class="dropdown-link">Мужчинам</div>
          <div @click="goToGender('F')" class="dropdown-link">Женщинам</div>
          <div @click="goToPage('About')" class="dropdown-link">О нас</div>
          <div v-if="isAdmin" @click="goToPage('Admin')" class="dropdown-link">Админ-панель</div>
        </div>
        <div class="dropdown-menu-bottom">
          <a v-if="store.parameters.url_social_telegram" :href="store.parameters.url_social_telegram" target="_blank" rel="noopener">
            <img :src="icon_logo_telegram" alt="Telegram" />
          </a>
          <a v-if="store.parameters.url_social_whatsapp" :href="store.parameters.url_social_whatsapp" target="_blank" rel="noopener">
            <img :src="icon_logo_whatsapp" alt="WhatsApp" />
          </a>
          <a v-if="store.parameters.url_social_email" :href="`mailto:${store.parameters.url_social_email}`" rel="noopener">
            <img :src="icon_logo_mail" alt="Mail" />
          </a>
        </div>
      </nav>
    </transition>
  </header>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from '@/store/index.js'
import { useRoute, useRouter } from 'vue-router'
import icon_default_avatar_grey from '@/assets/images/default_avatar_grey.svg'
import icon_default_avatar_white from '@/assets/images/default_avatar_white.svg'
import icon_favorites_grey from '@/assets/images/favorites_grey.svg'
import icon_favorites_white from '@/assets/images/favorites_white.svg'
import icon_cart_grey from '@/assets/images/cart_grey.svg'
import icon_cart_white from '@/assets/images/cart_white.svg'
import icon_menu_grey from '@/assets/images/menu_grey.svg'
import icon_close from '@/assets/images/close.svg'
import icon_logo_orange from '@/assets/images/logo_orange.svg'
import icon_logo_white from '@/assets/images/logo_white.svg'
import icon_logo_telegram from '@/assets/images/logo_telegram.svg'
import icon_logo_whatsapp from '@/assets/images/logo_whatsapp.svg'
import icon_logo_mail from '@/assets/images/logo_mail.svg'

const store = useStore()
const route = useRoute()
const router = useRouter()
const menuOpen = ref(false)
let prevOverflowMenu
const isAdmin = computed(() => store.user?.role === 'admin')
const isIconWhite = computed(() => route.name === 'About' || route.name === 'Home')
const icon_default_avatar = computed(() => isIconWhite.value ? icon_default_avatar_white : icon_default_avatar_grey)
const icon_favorites = computed(() => isIconWhite.value ? icon_favorites_white : icon_favorites_grey)
const icon_cart = computed(() => isIconWhite.value ? icon_cart_white : icon_cart_grey)
const icon_logo = computed(() => isIconWhite.value ? icon_logo_white : icon_logo_orange)


function goToGender(gender) {
  toggleMenuClose()
  store.selectedCategory = ''
  store.filterGender = gender
  router.push({
    name:  'Catalog',
    query: { gender }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToPage(page) {
  toggleMenuClose()
  router.push({ name: page })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}
function toggleMenuClose() {
  if (menuOpen.value === true) menuOpen.value = false
}

watch(
  () => menuOpen.value,
  (isOpen) => {
    if (isOpen) {
      prevOverflowMenu = document.body.style.overflow
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = prevOverflowMenu || ''
    }
  }
)

</script>

<style scoped lang="scss">
.header {
  @include flex-c-sb;
  position: fixed;
  top: 0;
  width: calc(100% - 20px);
  height: 72px;
  padding: 10px;
  background-color: $black-25;
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
      .logo-icon {
        width: 35px;
        height: 30px;
      }
      .avatar {
        border-radius: 50%;
        object-fit: cover;
      }
      .badge {
        @include flex-c-c;
        position: absolute;
        top: 31px;
        width: 14px;
        height: 12px;
        border-radius: 1px;
        background-color: $grey-20;
        color: $white-100;
        font-family: NeueHaas-400;
        font-size: 10px;
        line-height: 100%;
        letter-spacing: -0.2px;
      }
      .badge-fav {
        right: 52px;
      }
      .badge-cart {
        right: 10px;
      }
    }
    img {
      width: 30px;
      height: 30px;
    }
  }
  .menu {
    @include flex-c-c;
    .menu-btn {
      @include flex-c-c;
      padding: 8px 16px;
      gap: 4px;
      background-color: white;
      border-radius: 999px;
      border: none;
      font-family: Manrope-Medium;
      font-size: 20px;
      line-height: 100%;
      letter-spacing: -0.8px;
      cursor: pointer;
      img {
        width: 30px;
        height: 30px;
      }
    }
  }
}

/* маленькое выпадающее меню */
.dropdown-menu {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: fixed;
  inset: 0;
  padding: 22px 0;
  background-color: $white-100;
  z-index: 2000;
  .dropdown-menu-top {
    display: flex;
    flex-direction: column;
    .dropdown-menu-btn {
      @include flex-c-c;
      align-self: center;
      margin: 8px 0 64px;
      width: 96px;
      gap: 4px;
      background: none;
      border: none;
      font-family: Manrope-Medium;
      font-size: 20px;
      line-height: 100%;
      letter-spacing: -.8px;
      cursor: pointer;
      img {
        width: 30px;
        height: 30px;
      }
    }
    .dropdown-link {
      display: flex;
      padding: 16px 8px;
      color: $grey-20;
      font-family: Bounded-350;
      font-size: 16px;
      line-height: 80%;
      letter-spacing: -0.8px;
      cursor: pointer;
      border-top: 1px solid $grey-87;
    }
    .dropdown-link:last-child {
      border-bottom: 1px solid $grey-87;
    }
  }
  .dropdown-menu-bottom {
    display: flex;
    justify-content: center;
    margin-bottom: 6px;
    height: 30px;
    gap: 24px;
    a {
      width: 30px;
      height: 30px;
      img {
        width: 30px;
        height: 30px;
        object-fit: cover;
      }
    }
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .header {
    height: 46px;
    .actions {
      width: 88px;
      gap: 8px;
      .icon-btn {
        .logo-icon {
          width: 27px;
          height: 24px;
        }
        .avatar {
        }
        .badge {
          top: 21px;
        }
        .badge-fav {
          right: 42px;
        }
        .badge-cart {
        }
      }
      img {
        width: 24px;
        height: 24px;
      }
    }
    .menu {
      .menu-btn {
        font-size: 16px;
        letter-spacing: -0.64px;
        img {
          width: 24px;
          height: 24px;
        }
      }
    }
  }

  .dropdown-menu {
    padding: 12px 0;
    .dropdown-menu-top {
      .dropdown-menu-btn {
        margin: 8px 0 32px;
        width: 80px;
        font-size: 16px;
        letter-spacing: -0.64px;
        img {
          width: 24px;
          height: 24px;
        }
      }
      .dropdown-link {
        padding: 12px 10px;
        font-size: 14px;
        letter-spacing: -0.7px;
      }
    }
  }
}

</style>
