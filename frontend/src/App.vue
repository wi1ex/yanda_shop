<template>
  <div class="app-container" v-if="store.user">
    <Header/>
    <CartPage/>
    <router-view/>
    <!-- Footer hidden on admin panel routes -->
    <Footer v-if="!isNoFooterRoute"/>
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
const isNoFooterRoute = computed(() => route.name === 'Admin' || route.name === 'Profile')
let prevOverflow

// следим за открытием/закрытием корзины/меню
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
watch(
  () => store.menuOpen,
  (isOpen) => {
    if (isOpen) {
      prevOverflow = document.body.style.overflow
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = prevOverflow || ''
    }
  }
)

onMounted(async () => {
  if (window.Telegram?.WebApp?.initDataUnsafe?.user) {
    const tgUser = window.Telegram.WebApp.initDataUnsafe.user
    await store.initializeTelegramUser(tgUser)
  } else {
    await store.initializeVisitorUser()
  }
  await store.fetchProducts()
  await store.fetchParameters()
  await store.fetchReviews()
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
  background-color: $grey-87;
  font-family: Manrope-Medium;

  /* Запрет выделения текста */
  -webkit-user-select: none; /* Chrome/Safari */
  -moz-user-select: none; /* Firefox */
  -ms-user-select: none; /* IE/Edge */
  user-select: none; /* Стандартный синтаксис */
}

@media (max-width: 600px) {
  .app-container {
    .fake-header {
      height: 66px;
    }
  }
}

</style>
