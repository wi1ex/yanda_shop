<template>
  <div class="app-container" v-if="store.userStore.user">
    <Header/>
    <Cart/>
    <Search/>
    <router-view/>
    <Footer v-if="!isNoFooterRoute"/>
  </div>
</template>

<script setup>
import { onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '@/store/index.js'
import Header from '@/components/Header.vue'
import Cart from '@/components/Cart.vue'
import Search from '@/components/Search.vue'
import Footer from '@/components/Footer.vue'

const store = useStore()
const route = useRoute()
const isNoFooterRoute = computed(() => route.name === 'Admin')

let initialOverflow = ''
const anyOverlayOpen = computed(() =>
  store.globalStore.showMenu ||
  store.cartStore.showCartDrawer ||
  store.globalStore.showSearch
)

watch(anyOverlayOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : initialOverflow
})

onMounted(async () => {
  initialOverflow = document.body.style.overflow || ''
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
</script>

<style scoped lang="scss">

.app-container {
  position: absolute;
  top: 0;
  width: 100%;
}

</style>
