<template>
  <div class="cart-page">
    <!-- Здесь рендерится “сырое” отображение корзины -->
    <Cart />
  </div>
</template>

<script setup>
import Cart from '@/components/Cart.vue'
</script>

<style scoped lang="scss">
.cart-page {
  margin-top: 12vh; /* чтобы не перекрывать Header */
  padding: 2vh;
  background-color: $background-color;
}
</style>
