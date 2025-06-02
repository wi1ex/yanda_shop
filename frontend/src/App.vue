<template>
  <div class="app-container" v-if="store.user">
    <Header />

    <!-- Если корзина открыта — показываем Cart -->
    <Cart v-if="store.cartOpen" />
    <!-- Если карточка товара выбрана (и корзина не открыта) — показываем ProductDetail -->
    <ProductDetail v-else-if="store.selectedProduct" />
    <!-- В остальных случаях — показываем каталог -->
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
import ProductDetail from '@/components/ProductDetail.vue'

// Telegram + сохранение пользователя
onMounted(() => {
  if (window.Telegram?.WebApp) {
    store.tg = window.Telegram.WebApp
    const user = store.tg.initDataUnsafe?.user
    if (user) {
      store.user = user
    } else {
      store.user = {
        id: 1,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser',
      }
    }
  }
  fetch(`${store.url}/api/save_user`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id: store.user.id,
      first_name: store.user.first_name,
      last_name: store.user.last_name,
      username: store.user.username,
    }),
  }).catch(console.error)
})
</script>

<style scoped lang="scss">
.app-container {
  position: absolute;
  top: 0;
  width: 100%;
  background-color: #131722;
  color: white;
}
</style>
