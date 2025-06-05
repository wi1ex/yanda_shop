<template>
  <div class="product-page">
    <!-- Компонент, который подтягивает детали товара по props (sku, category) -->
    <ProductDetail :sku="sku" :category="category" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ProductDetail from '@/components/ProductDetail.vue'

const route = useRoute()

// Берём параметры из URL
const sku = ref(route.params.sku)
const category = ref(route.query.category || route.params.category || '')

// Если URL меняется (хотя с нашим роутером он жестко “:sku”), пересохраняем
watch(
  () => route.params.sku,
  (newSku) => {
    sku.value = newSku
  }
)
watch(
  () => route.query.category,
  (newCat) => {
    category.value = newCat
  }
)

// Здесь нет onMounted(fetch) – сам компонент ProductDetail.vue делает fetch при получении props
</script>

<style scoped lang="scss">
.product-page {
  margin-top: 12vh; /* не перекрывать Header */
  padding: 2vh;
  background-color: $background-color;
}
</style>
