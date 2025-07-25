import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import CatalogPage from '@/views/CatalogPage.vue'
import ProductPage from '@/views/ProductPage.vue'
import FavoritesPage from '@/views/FavoritesPage.vue'
import ProfilePage from '@/views/ProfilePage.vue'
import AboutPage from '@/views/AboutPage.vue'
import DeliveryPage from '@/views/DeliveryPage.vue'
import ContactsPage from '@/views/ContactsPage.vue'
import BrandsPage from '@/views/BrandsPage.vue'
import AdminPage from '@/views/AdminPage.vue'
import { useStore } from '@/store/index.js'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/catalog', name: 'Catalog', component: CatalogPage },
  { path: '/catalog/product/:variant_sku', name: 'ProductDetail', component: ProductPage, props: true },
  { path: '/favorites', name: 'Favorites', component: FavoritesPage },
  { path: '/profile', name: 'Profile', component: ProfilePage },
  { path: '/about', name: 'About', component: AboutPage },
  { path: '/delivery', name: 'Delivery', component: DeliveryPage },
  { path: '/contacts', name: 'Contacts', component: ContactsPage },
  { path: '/brands', name: 'Brands', component: BrandsPage },
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
