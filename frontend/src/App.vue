<template>
  <div class="app-container" v-if="store.userStore.user">
    <Header/>
    <Cart/>
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
import Cart from '@/components/Cart.vue'

const store = useStore()
const route = useRoute()
const isNoFooterRoute = computed(() => route.name === 'Admin')
let prevOverflowCart

// следим за открытием/закрытием корзины/меню
watch(
  () => store.cartStore.showCartDrawer,
  (isOpen) => {
    if (isOpen) {
      prevOverflowCart = document.body.style.overflow
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = prevOverflowCart || ''
    }
  }
)

onMounted(async () => {
  if (window.Telegram?.WebApp?.initDataUnsafe?.user) {
    const tgUser = window.Telegram.WebApp.initDataUnsafe.user
    await store.userStore.initializeTelegramUser(tgUser)
  } else {
    await store.userStore.initializeVisitorUser()
  }
  await store.productStore.fetchProducts()
  await store.globalStore.fetchParameters()
  await store.globalStore.fetchReviews()
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
}

</style>
