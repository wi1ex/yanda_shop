<template>
  <div class="app-container" v-if="store.user">
    <Header/>
    <CartPage/>
    <router-view/>
    <!-- Footer hidden on admin panel routes -->
    <Footer v-if="!isAdminRoute"/>
  </div>
</template>

<script setup>
import { onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '@/store/index.js'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import CartPage from '@/views/CartPage.vue'

const store = useStore()
const route = useRoute()
const isAdminRoute = computed(() => route.path.startsWith('/admin'))
let prevOverflow

// Генерация случайного ID для веб-посетителя, если нет Telegram WebApp
function generateVisitorId() {
  if (window.crypto && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return Math.random().toString(36).substring(2, 11)
}

// следим за открытием/закрытием корзины
watch(
  () => store.showCartDrawer,
  (isOpen) => {
    if (isOpen) {
      prevOverflow = document.body.style.overflow
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = prevOverflow || ''
    }
  }
)

onMounted(() => {
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
  if (!store.user?.id) {
    const stored = localStorage.getItem('visitorId')
    if (stored) {
      store.user.id = stored
    } else {
      store.user.id = generateVisitorId()
      localStorage.setItem('visitorId', store.user.id)
    }
  }
})

onBeforeUnmount(() => {
  document.body.style.overflow = prevOverflow || ''
})
</script>

<style scoped lang="scss">

.app-container {
  position: absolute;
  top: 0;
  width: 100%;
  background-color: #DEDEDE;
  font-family: Manrope-Medium;
}

</style>
