<template>
    <main class="product-grid">
        <div class="products">
          <ProductCard v-for="product in products" :key="product.id" :product="product" @add-to-cart="handleAddToCart" />
        </div>
    </main>
</template>

<script setup>
import { ref } from 'vue';
import ProductCard from './ProductCard.vue';

// Пример списка товаров; в реальном проекте данные можно получать с сервера
const products = ref([
    { id: 1, name: 'Товар 1', price: 100, image: 'https://via.placeholder.com/200', description: 'Описание товара 1' },
    { id: 2, name: 'Товар 2', price: 200, image: 'https://via.placeholder.com/200', description: 'Описание товара 2' },
    { id: 3, name: 'Товар 3', price: 150, image: 'https://via.placeholder.com/200', description: 'Описание товара 3' },
    // можно добавить больше товаров
])

const emit = defineEmits(['update-cart']);

function handleAddToCart(product) {
    // В данном примере при добавлении одного товара увеличиваем счетчик на 1
    emit('update-cart', 1);
    alert(product.name + ' добавлен в корзину!');
}
</script>

<style lang="scss" scoped>
.product-grid {
    flex: 1;
    padding: 20px;
    background-color: #f9f9f9;
    .products {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 20px;
    }
}
</style>
