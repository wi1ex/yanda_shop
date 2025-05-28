<template>
  <div class="app-container" v-if="store.user">
    <Header />
    <Cart v-if="store.cartOpen" />
    <Catalog v-else />
    <Footer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { store } from '@/store.js'
import Header from '@/components/Header.vue'
import Catalog from '@/components/Catalog.vue'
import Cart from '@/components/Cart.vue'
import Footer from '@/components/Footer.vue'

// Telegram + сохранение пользователя
onMounted(() => {
  if (window.Telegram?.WebApp) {
    store.tg = window.Telegram.WebApp;
    const user = store.tg.initDataUnsafe?.user;
    if (user) {
      store.user = user;
      fetch('https://shop.yanda.twc1.net/api/save_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: store.user.id,
          first_name: store.user.first_name,
          last_name: store.user.last_name,
          username: store.user.username,
        }),
      }).catch(console.error)
    }
  }
  // if (!store.user) {
  //   store.user = {
  //     id: 0,
  //     first_name: 'Test',
  //     last_name: 'User',
  //     username: 'testuser',
  //   }
  // }
  // fetch('https://shop.yanda.twc1.net/api/save_user', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({
  //     id: store.user.id,
  //     first_name: store.user.first_name,
  //     last_name: store.user.last_name,
  //     username: store.user.username,
  //   }),
  // }).catch(console.error)
})
</script>

<style scoped lang="scss">
.app-container {
  background-color: #131722;
  color: white;
  min-height: 100vh;
  padding: 0 16px;
}
</style>
