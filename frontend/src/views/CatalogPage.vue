<template>
  <div class="catalog-page">
    <!-- Компонент со списком товаров -->
    <Catalog />

    <!-- Вложенный <router-view>, в который попадёт ProductPage.vue при переходе на /catalog/product/:sku -->
    <router-view />
  </div>
</template>

<script setup>
import Catalog from '@/components/Catalog.vue'
</script>

<style scoped lang="scss">
.catalog-page {
  margin-top: 12vh; /* чтобы не перекрывать Header */
}
</style>
