import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import CatalogPage from '@/views/CatalogPage.vue'
import CartPage from '@/views/CartPage.vue'
import ProductPage from '@/views/ProductPage.vue'
import AdminPage from '@/views/AdminPage.vue'
import ProfilePage from '@/views/ProfilePage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/catalog',
    name: 'Catalog',
    component: CatalogPage
  },
  {
    path: '/catalog/product/:sku',
    name: 'ProductDetail',
    component: ProductPage,
    props: true
  },
  {
    path: '/cart',
    name: 'Cart',
    component: CartPage
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPage
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage
  },
  {
    path: '/:catchAll(.*)',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
