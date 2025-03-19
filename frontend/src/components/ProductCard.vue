<template>
    <div class="product-card">
        <img :src="product.image" :alt="product.name" class="product-image" />
        <div class="product-details">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-description">{{ product.description }}</p>
            <div class="product-footer">
                <span class="product-price">{{ product.price }} ₽</span>
                <button @click="addToCart" class="add-to-cart">В корзину</button>
            </div>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    product: {
        type: Object,
        required: true,
    }
})
const emit = defineEmits(['add-to-cart'])

function addToCart() {
    emit('add-to-cart', props.product)
}
</script>

<style lang="scss" scoped>
.product-card {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    .product-image {
        width: 100%;
        height: 150px;
        object-fit: cover;
    }
    .product-details {
        padding: 10px;
        display: flex;
        flex-direction: column;
        flex: 1;
        .product-name {
            font-size: 1.1em;
            margin: 0 0 5px;
        }
        .product-description {
            flex: 1;
            font-size: 0.9em;
            color: #666;
        }
        .product-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            .product-price {
                font-weight: bold;
                color: #333;
            }
            .add-to-cart {
                background-color: #0088cc;
                color: #fff;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
            }
            .add-to-cart:hover {
                opacity: 0.9;
            }
        }
    }
}
</style>
