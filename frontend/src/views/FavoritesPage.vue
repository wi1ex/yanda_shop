<template>
  <div class="favorites-container">
    <h2 v-if="favoriteProducts.length">Избранное</h2>
    <div v-else class="empty">Список избранного пуст</div>

    <div v-if="favoriteProducts.length" class="products-grid">
      <router-link v-for="product in favoriteProducts" :key="product.color_sku" class="product-card"
                   :to="{ name: 'ProductDetail', params: { variant_sku: product.variant_sku }, query: { category: product.category }}">
        <button type="button" class="remove-fav-btn" @click.prevent.stop="store.removeFromFavorites(product.color_sku)" aria-label="Удалить из избранного">
          ×
        </button>

        <img :src="product.image" alt="product" class="product-image" />
        <div class="product-info">
          <p class="product-price">{{ product.price }} ₽</p>
          <p class="product-name">{{ product.name }}</p>
          <p v-if="product.color" class="product-color">Цвет: {{ product.color }}</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useStore } from '@/store/index.js'

const store = useStore()

// грузим массив color_sku
onMounted(async () => {
  await store.fetchAllProducts()
  await store.loadFavoritesFromServer()
})

// вычисляем реальный список products по каждому color_sku
const favoriteProducts = computed(() =>
  store.favorites.items
    .map(cs => store.colorGroups.find(g => g.color_sku === cs))
    .filter(Boolean)
    .map(g => g.minPriceVariant)
)
</script>

<style scoped lang="scss">

.favorites-container {
  margin-top: 12vh;
  padding: 2vh;
}

/* Грид как в каталоге */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(135px, 1fr));
  gap: 16px;
}

/* Карточка товара */
.product-card {
  background: $background-color;
  border-radius: 15px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  cursor: pointer;
  position: relative;
}

/* Изображение */
.product-image {
  width: 100%;
  border-radius: 10px;
  object-fit: cover;
}

/* Блок с информацией */
.product-info {
  margin-top: 8px;
}

.product-price {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.product-name {
  font-size: 14px;
  color: #555;
  margin-top: 4px;
}

.product-color {
  font-size: 12px;
  color: #777;
  margin-top: 2px;
}

/* Пустое состояние */
.empty {
  text-align: center;
  color: #bbb;
  margin-top: 20px;
}

.remove-fav-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(220, 53, 69, 0.8);
  border: none;
  color: #fff;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 16px;
  line-height: 24px;
  text-align: center;
  cursor: pointer;
  z-index: 10;
  transition: background 0.2s;
}

@media (max-width: 600px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  .favorites-container {
    margin-top: 8vh;
  }
}

</style>
