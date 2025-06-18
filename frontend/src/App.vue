<template>
  <div class="app-container" v-if="store.user">
    <Header />
    <CartPage v-if="store.showCartDrawer" />
    <router-view />
    <Footer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useStore } from '@/store/index.js'
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
  background-color: #DEDEDE;
}

</style>
