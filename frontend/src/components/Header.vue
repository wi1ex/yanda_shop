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
      <button type="button" class="menu-btn" @click="toggleMenu()">
        Меню
        <img :src="icon_menu_grey" alt="Меню" />
      </button>
    </div>

    <!-- Иконки действий -->
    <div class="actions">
<!--      <div @click="goToPage('Profile')" class="icon-btn" title="Профиль">-->
      <div class="icon-btn" title="Профиль">
        <img :src="store.userStore.user.photo_url || icon_default_avatar" alt="Профиль" class="avatar" />
      </div>
      <div @click="goToPage('Favorites')" class="icon-btn" title="Избранное">
        <img :src="icon_favorites" alt="Избранное" />
        <span v-if="store.cartStore.favorites.count" class="badge badge-fav">
          {{ store.cartStore.favorites.count < 10 ? store.cartStore.favorites.count : "9+" }}
        </span>
      </div>
      <button type="button" @click="store.cartStore.openCartDrawer()" class="icon-btn" title="Корзина">
        <img :src="icon_cart" alt="Корзина" />
        <span v-if="store.cartStore.cart.count" class="badge badge-cart">
          {{ store.cartStore.cart.count < 10 ? store.cartStore.cart.count : "9+"}}
        </span>
      </button>
    </div>

    <!-- Выпадающее меню -->
    <transition name="fade">
      <nav v-if="menuOpen" class="dropdown-menu">
        <div class="dropdown-menu-top">
          <button type="button" class="dropdown-menu-btn" @click="toggleMenuClose()">
            Меню
            <img :src="icon_close" alt="Меню" />
          </button>

          <div @click="goToPage('Brands')" class="dropdown-link">Бренды</div>

          <div class="dropdown-link" :class="{ open: openSubmenu.M }" @click="toggleSubmenu('M')" :aria-expanded="openSubmenu.M">
            Мужчинам
            <img :src="icon_arrow_up" alt="" :style="{ transform: openSubmenu.M ? 'none' : 'rotate(180deg)'}"/>
          </div>
          <transition name="submenu">
            <div v-if="openSubmenu.M" class="dropdown-sublinks">
              <div v-for="cat in store.productStore.categoryList" :key="`M-${cat}`" class="dropdown-sublink" @click="goToCategory('M', cat)">
                {{ cat }}
              </div>
            </div>
          </transition>

          <div class="dropdown-link" :class="{ open: openSubmenu.F }" @click="toggleSubmenu('F')" :aria-expanded="openSubmenu.F">
            Женщинам
            <img :src="icon_arrow_up" alt="" :style="{ transform: openSubmenu.F ? 'none' : 'rotate(180deg)'}"/>
          </div>
          <transition name="submenu">
            <div v-if="openSubmenu.F" class="dropdown-sublinks">
              <div v-for="cat in store.productStore.categoryList" :key="`F-${cat}`" class="dropdown-sublink" @click="goToCategory('F', cat)">
                {{ cat }}
              </div>
            </div>
          </transition>

          <div @click="goToPage('About')" class="dropdown-link">О нас</div>

          <div v-if="isAdmin" @click="goToPage('Admin')" class="dropdown-link">Админ-панель</div>
        </div>
        <div class="dropdown-menu-bottom">
          <div class="dropdown-menu-urls">
            <a v-if="store.globalStore.parameters.url_social_email" :href="`mailto:${store.globalStore.parameters.url_social_email}`" rel="noopener">
              <img :src="icon_logo_mail" alt="Mail" />
            </a>
            <a v-if="store.globalStore.parameters.url_social_telegram" :href="store.globalStore.parameters.url_social_telegram" target="_blank" rel="noopener">
              <img :src="icon_logo_telegram" alt="Telegram" />
            </a>
            <a v-if="store.globalStore.parameters.url_social_whatsapp" :href="store.globalStore.parameters.url_social_whatsapp" target="_blank" rel="noopener">
              <img :src="icon_logo_whatsapp" alt="WhatsApp" />
              <p class="dropdown-menu-symb">*</p>
            </a>
            <a v-if="store.globalStore.parameters.url_social_instagram" :href="store.globalStore.parameters.url_social_instagram" target="_blank" rel="noopener">
              <img :src="icon_logo_instagram" alt="Instagram" />
              <p class="dropdown-menu-symb">*</p>
            </a>
          </div>
          <div class="dropdown-menu-text">*принадлежит компании Meta, признанной экстремистской и запрещенной на территории РФ</div>
        </div>
      </nav>
    </transition>
  </header>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
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
import icon_logo_instagram from '@/assets/images/logo_instagram.svg'
import icon_arrow_up from "@/assets/images/arrow_up.svg";

let prevOverflowMenu
const store = useStore()
const route = useRoute()
const router = useRouter()
const menuOpen = ref(false)
const openSubmenu = reactive({ M: false, F: false })
const isAdmin = computed(() => store.userStore.user?.role === 'admin')
const isIconWhite = computed(() => route.name === 'About' || route.name === 'Home')
const icon_default_avatar = computed(() => isIconWhite.value ? icon_default_avatar_white : icon_default_avatar_grey)
const icon_favorites = computed(() => isIconWhite.value ? icon_favorites_white : icon_favorites_grey)
const icon_cart = computed(() => isIconWhite.value ? icon_cart_white : icon_cart_grey)
const icon_logo = computed(() => isIconWhite.value ? icon_logo_white : icon_logo_orange)

// переключить видимость подменю по полу
function toggleSubmenu(gender) {
  openSubmenu[gender] = !openSubmenu[gender]
}

function goToCategory(gender, category) {
  // закрываем меню и оба подменю
  toggleMenuClose()
  // сбрасываем стор
  store.productStore.selectedCategory = category
  store.productStore.filterGender = gender
  store.productStore.filterSubcat = ''
  // навигация в каталог с двумя фильтрами
  router.push({
    name: 'Catalog',
    query: { gender, category }
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
  if (menuOpen.value) {
    menuOpen.value = false
    openSubmenu.M = openSubmenu.F = false
  }
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
        font-size: 10px;
        line-height: 80%;
        letter-spacing: -0.4px;
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
      align-items: center;
      justify-content: space-between;
      position: relative;
      padding: 12px 10px;
      color: $grey-20;
      font-family: Bounded;
      font-weight: 350;
      font-size: 14px;
      line-height: 80%;
      letter-spacing: -0.7px;
      cursor: pointer;
      border-top: 1px solid $grey-87;
      img {
        width: 16px;
        height: 16px;
      }
      &.open {
        background-color: $grey-90;
      }
    }
    .dropdown-link:last-child {
      border-bottom: 1px solid $grey-87;
    }
    .dropdown-sublinks {
      display: flex;
      flex-direction: column;
      background-color: $grey-95;
      .dropdown-sublink {
        padding: 12px 10px;
        border-top: 1px solid $white-100;
        background-color: $grey-90;
        color: $grey-20;
        font-size: 16px;
        line-height: 110%;
        letter-spacing: -0.6px;
        cursor: pointer;
      }
    }
    .submenu-enter-active,
    .submenu-leave-active {
      transition: max-height 0.25s ease-in-out, opacity 0.25s ease-in-out, padding 0.25s ease-in-out;
      overflow: hidden;
    }
    .submenu-enter-from,
    .submenu-leave-to {
      max-height: 0;
      opacity: 0;
      padding-top: 0;
      padding-bottom: 0;
    }
    .submenu-enter-to,
    .submenu-leave-from {
      max-height: 500px;
      opacity: 1;
    }
  }
  .dropdown-menu-bottom {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 6px;
    gap: 4px;
    .dropdown-menu-urls {
      display: flex;
      justify-content: center;
      height: 30px;
      gap: 24px;
      a {
        width: 30px;
        height: 30px;
        text-decoration: none;
        img {
          width: 30px;
          height: 30px;
          object-fit: cover;
        }
        .dropdown-menu-symb {
          display: flex;
          position: relative;
          margin: 0;
          top: -38px;
          left: 27px;
          color: $black-100;
          cursor: default;
        }
      }
    }
    .dropdown-menu-text {
      width: 60%;
      text-align: center;
      color: $black-40;
      font-size: 10px;
      line-height: 100%;
      letter-spacing: -0.4px;
    }
  }
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease-in-out;
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
    }
  }
}

</style>
