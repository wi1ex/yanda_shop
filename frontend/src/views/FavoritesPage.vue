<template>
  <div class="favorites-container">
    <div class="line-vert"></div>
    <div class="header-logo">
      <span class="logo-title">ИЗБРАННОЕ</span>
      <sup class="logo-count">{{ favoriteProducts.length }}</sup>
    </div>

    <button type="button" class="back-button" @click="goBack">
      <img :src="icon_arrow_grey" alt="arrow back" />
      Назад
    </button>

    <div class="line-hor"></div>

    <div v-if="favoriteProducts.length === 0" class="empty-cart">
      Ты еще не добавлял товары в избранное.
      <button type="button" class="action-button" @click="goToCatalog">
        Перейти в каталог
      </button>
    </div>

    <div v-else class="products-grid" :class="{ blurred: favoritesLoading }">
      <div v-for="product in favoriteProducts" :key="product.color_sku" @click="goToProduct(product)" class="product-card">
        <button type="button" class="remove-fav-btn" @click.prevent.stop="store.cartStore.removeFromFavorites(product.color_sku)" aria-label="Удалить из избранного">
          <img :src="icon_favorites_black" alt="product" />
        </button>
        <img class="product-image" :src="product.image" alt="product" />
        <div class="product-info">
          <p class="product-brand">{{ product.brand }}</p>
          <p class="product-name">{{ product.name }}</p>
          <p class="product-price">от {{ formatPrice(product.price) }} ₽</p>
        </div>
      </div>
    </div>
  </div>
  <div class="line-hor"></div>
</template>

<script setup>
import { onMounted, computed, ref, nextTick } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'
import icon_arrow_grey from '@/assets/images/arrow_grey.svg'
import icon_favorites_black from '@/assets/images/favorites_black.svg'

const store = useStore()
const router = useRouter()

const favoritesLoading = ref(false)

// вычисляем реальный список products по каждому color_sku
const favoriteProducts = computed(() =>
  store.cartStore.favorites.items
    .slice().reverse()
    .map(cs => store.productStore.colorGroups.find(g => g.color_sku === cs))
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
    router.push({ name: 'Home' })
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToCatalog() {
  store.productStore.selectedCategory = ''
  router.push({ name: 'Catalog' })
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
  await store.productStore.fetchProducts()
  await store.cartStore.loadFavoritesFromServer()
  await nextTick()
  setTimeout(() => {
    favoritesLoading.value = false
  }, 200)
})
</script>

<style scoped lang="scss">

.line-vert {
  position: absolute;
  top: 0;
  left: calc(50% - 0.5px);
  width: 1px;
  height: 100%;
  background-color: $white-100;
  z-index: 10;
}
.line-hor {
  width: 100%;
  height: 1px;
  background-color: $white-100;
  z-index: 100;
}
.favorites-container {
  display: flex;
  flex-direction: column;
  margin: 60px 0 96px;
  .empty-cart {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
    gap: 40px;
    color: $grey-20;
    font-size: 16px;
    line-height: 110%;
    letter-spacing: -0.64px;
    z-index: 20;
    .action-button {
      width: fit-content;
      height: 72px;
      padding: 0 24px;
      font-size: 16px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      background-color: $grey-20;
      color: $white-100;
      line-height: 100%;
      letter-spacing: -0.64px;
    }
  }
  .header-logo {
    display: flex;
    justify-content: center;
    margin: 40px;
    z-index: 20;
    .logo-title {
      color: $black-100;
      font-family: Bounded;
      font-weight: 400;
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
    margin: 0 10px 10px;
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
    margin-top: 40px;
    transition: filter 0.25s ease-in-out;
    .product-card {
      display: flex;
      flex-direction: column;
      position: relative;
      min-width: 0;
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
        padding: 10px 10px 16px;
        background-color: $grey-87;
        .product-brand {
          margin: 0;
          font-size: 12px;
          line-height: 100%;
          letter-spacing: -0.48px;
          color: $black-60;
        }
        .product-name {
          margin: 4px 0 12px;
          font-family: Manrope-SemiBold;
          font-size: 15px;
          line-height: 100%;
          letter-spacing: -0.6px;
          color: $black-100;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
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
    .empty-cart {
      .action-button {
        height: 56px;
      }
    }
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
    }
  }
}

</style>
