import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import CatalogPage from '@/views/CatalogPage.vue'
import CartPage from '@/views/CartPage.vue'
import ProductPage from '@/views/ProductPage.vue'
import AdminPage from '@/views/AdminPage.vue'
import ProfilePage from '@/views/ProfilePage.vue'
import { useStore } from '@/store/index.js'  // <-- импортируем стор

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/catalog', name: 'Catalog', component: CatalogPage },
  { path: '/catalog/product/:variant_sku', name: 'ProductDetail', component: ProductPage, props: true },
  { path: '/cart', name: 'Cart', component: CartPage },

  // Маршрут /admin с защитой: beforeEnter
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPage,
    beforeEnter: (to, from, next) => {
      const store = useStore()
      // Если user не определён или его ID не совпадает с admin_id → редирект на Home
      if (!store.user || String(store.user.id) !== String(store.admin_id)) {
        next({ name: 'Home' })
      } else {
        next()
      }
    }
  },

  { path: '/profile', name: 'Profile', component: ProfilePage },
  { path: '/:catchAll(.*)', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
