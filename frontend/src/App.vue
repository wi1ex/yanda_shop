<template>
  <div class="app-container" v-if="store.user">
    <Header />

    <transition name="fade">
      <div v-if="store.showCartDrawer" class="cart-drawer-overlay" @click.self="store.closeCartDrawer()">
        <div class="cart-drawer">
          <button class="close-btn" @click="store.closeCartDrawer()">×</button>
          <CartPage />
        </div>
      </div>
    </transition>

    <router-view />
    <Footer />
  </div>
</template>

<script setup>
import {onMounted} from 'vue'
import {useStore} from '@/store/index.js'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import CartPage from '@/views/CartPage.vue'

const store = useStore()

// Генерация случайного ID для веб-посетителя, если нет Telegram WebApp
function generateVisitorId() {
  if (window.crypto && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return Math.random().toString(36).substring(2, 11)
}

onMounted(() => {
  let userId

  const stored = localStorage.getItem('visitorId')
  if (stored) {
    userId = stored
  } else {
    userId = generateVisitorId()
    localStorage.setItem('visitorId', userId)
  }

  // Инициализируем user со всеми полями, включая photo_url
  store.user = {
    id: userId,
    first_name: null,
    last_name: null,
    username: null,
    photo_url: null
  }

  if (window.Telegram?.WebApp) {
    store.tg = window.Telegram.WebApp
    const tgUser = store.tg.initDataUnsafe?.user
    if (tgUser) {
      store.user = {
        id: tgUser.id,
        first_name: tgUser.first_name,
        last_name: tgUser.last_name,
        username: tgUser.username,
        photo_url: tgUser.photo_url || null
      }
    }
  }

  // Отправляем на бэкенд
  fetch(`${store.url}/api/save_user`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      id: store.user.id,
      first_name: store.user.first_name,
      last_name: store.user.last_name,
      username: store.user.username,
      photo_url: store.user.photo_url
    }),
  }).catch(console.error)
})
</script>

<style scoped lang="scss">

.app-container {
  position: absolute;
  top: 0;
  width: 100%;
  background-color: #596380;
  color: white;
}

.cart-drawer-overlay {
  position: fixed;
  top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: flex-end;
  z-index: 2000;
}

.cart-drawer {
  background: #131722;
  height: 100%;
  position: relative;
  overflow-y: auto;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 12px;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

/* появление/исчезание */
.fade-enter-active, .fade-leave-active {
  transition: opacity .2s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* мобильная — на весь экран */
@media (max-width: 600px) {
  .cart-drawer { width: 100%; }
}

/* десктоп — 400px справа */
@media (min-width: 601px) {
  .cart-drawer { width: 400px; }
}

</style>
