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
import { useStore } from '@/store/index.js'
import Header from '@/components/Header.vue'
import Catalog from '@/components/Catalog.vue'
import Cart from '@/components/Cart.vue'
import Footer from '@/components/Footer.vue'
import ProductDetail from '@/components/ProductDetail.vue'

const store = useStore()

// Функция для генерации простого случайного ID
function generateVisitorId() {
  if (window.crypto && crypto.randomUUID) {
    return crypto.randomUUID()  // современный способ, если поддерживается
  }
  // fallback: короткая строка
  return Math.random().toString(36).substring(2, 11)
}

onMounted(() => {
  let userId

  if (window.Telegram?.WebApp) {
    store.tg = window.Telegram.WebApp
    const tgUser = store.tg.initDataUnsafe?.user
    if (tgUser) {
      // Пользователь из Telegram: используем tgUser.id
      userId = tgUser.id
      store.user = {
        id: userId,
        first_name: tgUser.first_name,
        last_name: tgUser.last_name,
        username: tgUser.username
      }
    } else {
      // Защитная «заглушка», редко понадобится
      store.user = {
        id: 1,
        first_name: null,
        last_name: null,
        username: null
      }
    }
  } else {
    // Обычный веб-посетитель: смотрим localStorage.visitorId
    const stored = localStorage.getItem('visitorId')
    if (stored) {
      userId = stored
    } else {
      userId = generateVisitorId()
      localStorage.setItem('visitorId', userId)
    }
    // Сохраняем в сторе (по желанию, для отладки можно оставить поля пустыми)
    store.user = {
      id: userId,
      first_name: null,
      last_name: null,
      username: null
    }
  }

  // Отправляем на бэкенд
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
