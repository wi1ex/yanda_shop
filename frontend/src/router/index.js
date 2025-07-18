import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import AboutPage from '@/views/AboutPage.vue'
import CatalogPage from '@/views/CatalogPage.vue'
import ProductPage from '@/views/ProductPage.vue'
import AdminPage from '@/views/AdminPage.vue'
import ProfilePage from '@/views/ProfilePage.vue'
import FavoritesPage from '@/views/FavoritesPage.vue'
import { useStore } from '@/store/index.js'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/catalog', name: 'Catalog', component: CatalogPage },
  { path: '/about', name: 'About', component: AboutPage },
  { path: '/catalog/product/:variant_sku', name: 'ProductDetail', component: ProductPage, props: true },
  { path: '/favorites', name: 'Favorites', component: FavoritesPage },
  { path: '/profile', name: 'Profile', component: ProfilePage },
  { path: '/admin', name: 'Admin', component: AdminPage },
  { path: '/:catchAll(.*)', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// глобальный guard вместо beforeEnter на одном маршруте
router.beforeEach(async (to, from, next) => {
  const store = useStore()
  if (to.name === 'Admin') {
    // если нет токенов или server-side проверка провалилась — домой
    const ok = store.accessToken && store.refreshToken && await store.verifyAdminAccess()
    if (!ok) return next({ name: 'Home' })
  }
  if (to.name === 'Home') {
    store.selectedCategory = ''
    store.clearFilters()
  }
  next()
})

export default router
