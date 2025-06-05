<template>
  <div class="catalog-page">
    <Catalog />
  </div>
</template>

<script setup>
import Catalog from '@/components/Catalog.vue'
</script>

<style scoped lang="scss">
.catalog-page {
  margin-top: 12vh; /* чтобы Header не заслонял */
}
</style>
