<template>
  <div class="product-detail">
    <!-- Индикатор загрузки -->
    <div v-if="loading" class="loading">Загрузка...</div>

    <!-- Основная карточка -->
    <div v-else-if="detailData" class="detail-card">
      <!-- 1. Шапка: Назад + Наличие -->
      <div class="top-row">
        <button class="back-button" @click="goBack">← Назад</button>
        <div class="availability">
          <span v-if="detailData.count_in_stock > 0">
            В НАЛИЧИИ: {{ detailData.count_in_stock }}
          </span>
          <span v-else>ПОД ЗАКАЗ</span>
        </div>
      </div>

      <!-- 2. Бренд, название, артикул -->
      <div class="title-block">
        <p class="brand">{{ detailData.brand }}</p>
        <h1 class="name">{{ detailData.name }}</h1>
        <p class="sku">артикул: {{ detailData.variant_sku }}</p>
      </div>

      <!-- 3. Галерея: крупное изображение + прокручиваемые миниатюры -->
      <div class="carousel-container">
        <div class="main-image-wrapper">
          <img :src="detailData.images[currentIndex]" alt="product image" class="main-image"/>
        </div>
        <div class="thumbnails-wrapper" ref="thumbsRef">
          <img v-for="(img, idx) in detailData.images" :key="idx" :src="img" alt="" class="thumbnail"
               :class="{ active: idx === currentIndex }" @click="scrollToIndex(idx)"/>
        </div>
      </div>

      <!-- 4. Параметры: размер, цвет, материал -->
      <div class="options-block">
        <div class="option">
          <label>Размер</label>
          <span class="value">{{ detailData.size_label }}</span>
        </div>
        <div v-if="detailData.color" class="option">
          <label>Цвет</label>
          <div class="color-swatches">
            <span v-for="c in detailData.color.split(',')" :key="c" class="swatch" :style="{ backgroundColor: c.trim() }"/>
          </div>
        </div>
        <div v-if="detailData.material" class="option">
          <label>Материал</label>
          <span class="value">{{ detailData.material }}</span>
        </div>
      </div>

      <!-- 5. Доставка и цена -->
      <div class="delivery-price-block">
        <div class="delivery">
          <label>Доставка</label>
          <span>{{ detailData.delivery_time }}</span>
        </div>
        <div class="price-row">
          <label>Цена</label>
          <span class="price">{{ detailData.price }} ₽</span>
        </div>
      </div>

      <!-- 6. Кнопки действий -->
      <div class="actions-block">
        <button class="add-cart-button" @click="store.addToCart(detailData)">
          Добавить в корзину
        </button>
        <button v-if="!store.isFavorite(detailData)" class="add-fav-button" @click="store.addToFavorites(detailData)">
          Добавить в избранное
        </button>
        <button v-else class="remove-fav-button" @click="store.removeFromFavorites(detailData)">
          Убрать из избранного
        </button>
      </div>

      <!-- 7. Аккордеон: Описание -->
      <div class="section">
        <div class="section-header" @click="toggleDescription">
          <span>Описание</span>
          <span class="arrow">{{ showDescription ? '▼' : '▶' }}</span>
        </div>
        <div v-show="showDescription" class="section-body">
          <p>{{ detailData.description }}</p>
        </div>
      </div>

      <!-- 8. Аккордеон: Характеристики -->
      <div class="section">
        <div class="section-header" @click="toggleCharacteristics">
          <span>Характеристики</span>
          <span class="arrow">{{ showCharacteristics ? '▼' : '▶' }}</span>
        </div>
        <div v-show="showCharacteristics" class="section-body">
          <p v-for="(val, key) in detailData" :key="key"
            v-if="keyLabels[key] && val != null && !['images','name','price','description','brand','variant_sku','count_in_stock','delivery_time','size_label','color','material'].includes(key)">
            <strong>{{ keyLabels[key] }}:</strong> {{ val }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '@/store/index.js'

const route = useRoute()
const router = useRouter()
const store = useStore()

const category = route.query.category

const detailData = ref(null)
const loading = ref(true)
const currentIndex = ref(0)
const thumbsRef = ref(null)

const showDescription = ref(false)
const showCharacteristics = ref(false)

// Читаемые подписи для характеристик
const keyLabels = {
  gender: 'Пол',
  category: 'Категория',
  subcategory: 'Субкатегория',
  width_mm: 'Ширина (мм)',
  height_mm: 'Высота (мм)',
  depth_mm: 'Глубина (мм)',
  material: 'Материал',
  color: 'Цвет',
  size_label: 'Размер',
  count_in_stock: 'Наличие',
  delivery_time: 'Время доставки'
}

function toggleDescription() {
  showDescription.value = !showDescription.value
}
function toggleCharacteristics() {
  showCharacteristics.value = !showCharacteristics.value
}

function goBack() {
  router.push({ name: 'Catalog' })
}

function scrollToIndex(idx) {
  if (!detailData.value?.images) return
  currentIndex.value = idx
  nextTick(() => {
    const thumbs = thumbsRef.value
    const thumb = thumbs?.children[idx]
    if (thumb) {
      const offset = thumb.offsetLeft - thumbs.clientWidth / 2 + thumb.clientWidth / 2
      thumbs.scrollTo({ left: offset, behavior: 'smooth' })
    }
  })
}

async function fetchDetail() {
  loading.value = true
  detailData.value = null
  try {
    const vs = route.params.variant_sku
    const res = await fetch(
      `${store.url}/api/product?category=${encodeURIComponent(category)}&variant_sku=${encodeURIComponent(vs)}`
    )
    if (res.ok) {
      detailData.value = await res.json()
    } else {
      console.error('Ошибка при получении детализации товара:', res.statusText)
    }
  } catch (e) {
    console.error('Сетевая ошибка fetchDetail:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchDetail)

watch(
  () => [route.params.variant_sku, route.query.category],
  fetchDetail
)
</script>

<style scoped lang="scss">

.product-detail {
  margin-top: 12vh;
  padding: 2vh;
}

.loading {
  color: #bbb;
  font-size: 18px;
  text-align: center;
  margin-top: 40px;
}

.detail-card {
  background: $background-color;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* 1. Шапка */
.top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.back-button {
  background: none;
  border: none;
  font-size: 16px;
  color: #007bff;
  cursor: pointer;
}

.availability span {
  font-weight: bold;
}

/* 2. Заголовок */
.title-block {
  margin-bottom: 16px;
}

.title-block .brand {
  font-size: 14px;
  color: #777;
}

.title-block .name {
  font-size: 20px;
  margin: 4px 0;
}

.title-block .sku {
  font-size: 12px;
  color: #777;
}

/* 3. Галерея */
.carousel-container {
  margin-bottom: 16px;
}

.main-image-wrapper {
  text-align: center;
}

.main-image {
  max-width: 100%;
  border-radius: 8px;
}

.thumbnails-wrapper {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  margin-top: 8px;
}

.thumbnails-wrapper::-webkit-scrollbar {
  display: none;
}

.thumbnail {
  flex: 0 0 auto;
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.6;
  border: 2px solid transparent;
}

.thumbnail.active {
  opacity: 1;
  border-color: #007bff;
}

/* 4. Параметры */
.options-block {
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin: 16px 0;
}

.option {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
}

.option + .option {
  border-top: 1px solid #eee;
}

label {
  font-weight: bold;
  color: #333;
}

.value {
  color: #555;
}

.color-swatches {
  display: flex;
  gap: 8px;
}

.swatch {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #ccc;
}

/* 5. Доставка и цена */
.delivery-price-block {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.price-row .price {
  font-size: 18px;
  font-weight: bold;
}

/* 6. Кнопки действий */
.actions-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 16px 0;
}

.add-cart-button {
  background: #000;
  color: #fff;
  padding: 14px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
}

.add-fav-button {
  background: #fff;
  color: #000;
  border: 1px solid #000;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.remove-fav-button {
  background: #dc3545;
  color: #fff;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

/* 7–8. Аккордеоны */
.section {
  margin-top: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  cursor: pointer;
  padding: 12px 0;
  border-top: 1px solid #eee;
}

.section-body {
  padding: 8px 0 12px;
  color: #555;
}

.arrow {
  font-size: 14px;
}

</style>
