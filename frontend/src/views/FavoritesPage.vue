<template>
  <div class="favorites-container">
    <div class="header-logo">
      <span class="logo-title">ИЗБРАННОЕ</span>
      <sup class="logo-count">{{ favoriteProducts.length }}</sup>
    </div>

    <button class="back-button" @click="goBack">
      <img :src="icon_arrow_back" alt="arrow back" />
      Назад
    </button>

    <div v-if="favoriteProducts.length" class="products-grid" :class="{ blurred: favoritesLoading }">
      <div v-for="product in favoriteProducts" :key="product.color_sku" @click="goToProduct(product)" class="product-card">
        <button type="button" class="remove-fav-btn" @click.prevent.stop="store.removeFromFavorites(product.color_sku)" aria-label="Удалить из избранного">
          <img :src="icon_product_in_favorites" alt="product" />
        </button>

        <img :src="product.image" alt="product" class="product-image" />

        <div class="product-info">
          <p class="product-brand">{{ product.brand }}</p>
          <p class="product-name">{{ product.name }}</p>
          <p class="product-price">от {{ formatPrice(product.price) }} ₽</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref, nextTick } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'
import icon_arrow_back from '@/assets/images/arrow_back.svg'
import icon_product_in_favorites from '@/assets/images/product_in_favorites.svg'

const store = useStore()
const router = useRouter()

const favoritesLoading = ref(false)

// вычисляем реальный список products по каждому color_sku
const favoriteProducts = computed(() =>
  store.favorites.items
      .slice().reverse()
      .map(cs => store.colorGroups.find(g => g.color_sku === cs))
      .filter(Boolean)
      .map(g => g.minPriceVariant)
)

function formatPrice(val) {
  return String(val).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.replace({ name: 'Home' })
  }
}

// Переход на страницу товара
function goToProduct(p) {
  router.push({
    name: 'ProductDetail',
    params: { variant_sku: p.variant_sku },
    query: { category: p.category }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// при монтировании: плавно показываем, грузим ВСЕ товары + избранное, убираем эффект
onMounted(async () => {
  favoritesLoading.value = true
  await store.fetchProducts()
  await store.loadFavoritesFromServer()
  await nextTick()
  setTimeout(() => {
    favoritesLoading.value = false
  }, 200)
})
</script>

<style scoped lang="scss">

.favorites-container {
  display: flex;
  flex-direction: column;
  margin-top: 60px;
  .header-logo {
    display: flex;
    justify-self: center;
    margin: 40px;
    .logo-title {
      color: $black-100;
      font-family: Bounded-400;
      font-size: 64px;
      line-height: 90%;
      letter-spacing: -5.12px;
    }
    .logo-count  {
      color: $red-active;
      margin-left: 8px;
      margin-top: 2px;
      font-size: 16px;
      line-height: 110%;
      letter-spacing: -0.64px;
    }
  }
  .back-button {
    display: flex;
    align-items: center;
    margin-left: 10px;
    margin-bottom: 50px;
    padding: 0;
    width: fit-content;
    gap: 4px;
    background: none;
    border: none;
    color: $black-100;
    font-size: 16px;
    line-height: 100%;
    letter-spacing: -0.64px;
    cursor: pointer;
    img {
      width: 24px;
      height: 24px;
      object-fit: cover;
    }
  }
  .blurred {
    filter: blur(4px);
  }
  .products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(187px, 1fr));
    gap: 16px;
    transition: filter 0.25s ease-in-out;
    .product-card {
      display: flex;
      flex-direction: column;
      position: relative;
      padding: 10px 10px 16px;
      background-color: $grey-89;
      cursor: pointer;
      transition: transform 0.25s ease-in-out;
      .remove-fav-btn {
        display: flex;
        position: absolute;
        padding: 0;
        top: 10px;
        right: 10px;
        background: none;
        border: none;
        width: 24px;
        height: 24px;
        cursor: pointer;
        img {
          width: 24px;
          height: 24px;
          object-fit: cover;
        }
      }
      .product-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .product-info {
        display: flex;
        flex-direction: column;
        background-color: $grey-87;
        .product-brand {
          margin: 0;
          font-size: 12px;
          line-height: 100%;
          letter-spacing: -0.48px;
          color: $black-100;
        }
        .product-name {
          margin: 4px 0 12px;
          font-family: Manrope-SemiBold;
          font-size: 15px;
          line-height: 100%;
          letter-spacing: -0.6px;
          color: $black-100;
        }
        .product-price {
          margin: 0;
          font-size: 15px;
          line-height: 80%;
          letter-spacing: -0.6px;
          color: $grey-20;
        }
      }
    }
  }
}

@media (max-width: 600px) {
  .favorites-container {
    .header-logo {
      .logo-title {
        font-size: 32px;
        letter-spacing: -2.24px;
      }
      .logo-count  {
        margin-left: 4px;
        margin-top: 0;
        font-size: 15px;
        letter-spacing: -0.6px;
      }
    }
    .products-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }
  }
}

</style>
