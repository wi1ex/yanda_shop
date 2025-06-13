<template>
  <div class="product-detail">
    <!-- 1. Загрузка -->
    <div v-if="loading" class="loading">Загрузка...</div>

    <!-- 2. Основная карточка -->
    <div v-else-if="detailData" class="detail-card">
      <!-- Шапка: назад + наличие -->
      <div class="top-row">
        <button class="back-button" @click="goBack">← Назад</button>
        <div class="availability">
          <span v-if="detailData.count_in_stock > 0">
            В НАЛИЧИИ: {{ detailData.count_in_stock }}
          </span>
          <span v-else>ПОД ЗАКАЗ</span>
        </div>
      </div>

      <!-- Бренд, имя, артикул -->
      <div class="title-block">
        <p class="brand">{{ detailData.brand }}</p>
        <h1 class="name">{{ detailData.name }}</h1>
        <p class="sku">артикул: {{ detailData.variant_sku }}</p>
      </div>

      <!-- Галерея: главное + миниатюры с кликом + свайп -->
      <div class="carousel-container">
        <div class="main-image-wrapper" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
          <img :src="detailData.images[currentIndex]" alt="product image" class="main-image"/>
        </div>
        <div class="thumbnails-wrapper" ref="thumbsRef">
          <img v-for="(img, idx) in detailData.images" :key="idx" :src="img" alt="" class="thumbnail"
               :class="{ active: idx === currentIndex }" @click="scrollToIndex(idx)"/>
        </div>
      </div>

      <!-- Параметры: ВСЕ варианты размеров и цветов -->
      <div class="options-block">
        <!-- Размер -->
        <div class="option">
          <label>Размер</label>
          <div class="options-list">
            <button v-for="opt in sizeOptions" :key="opt" class="option-btn"
                    :class="{ active: opt === detailData.size_label }" @click="selectVariantByOpt('size', opt)">
              {{ opt }}
            </button>
          </div>
        </div>
        <!-- Цвет -->
        <div class="option">
          <label>Цвет</label>
          <div class="options-list">
            <button v-for="opt in colorOptions" :key="opt" class="option-btn color-btn"
                    :class="{ active: opt === detailData.color }" @click="selectVariantByOpt('color', opt)">
              {{ opt }}
            </button>
          </div>
        </div>
      </div>

      <!-- Доставка и цена -->
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

      <!-- Кнопки: корзина + избранное -->
      <div class="actions-block">
        <div v-if="currentQuantity > 0" class="quantity-controls">
          <button @click="onDecrease(detailData)">➖</button>
          <span class="quantity">{{ currentQuantity }}</span>
          <button @click="onIncrease(detailData)">➕</button>
        </div>
        <button v-else type="button" class="add-cart-button" @click="store.addToCart(detailData)">
          Добавить в корзину
        </button>

        <button v-if="!store.isFavorite(detailData)" type="button" class="add-fav-button" @click="store.addToFavorites(detailData)">
          Добавить в избранное
        </button>
        <button v-else type="button" class="remove-fav-button" @click="store.removeFromFavorites(detailData)">
          Убрать из избранного
        </button>
      </div>

      <!-- Описание (аккордеон) -->
      <div class="section">
        <div class="section-header" @click="toggleDescription">
          <span>Описание</span>
          <span class="arrow">{{ showDescription ? '▼' : '▶' }}</span>
        </div>
        <div v-show="showDescription" class="section-body">
          <p>{{ detailData.description }}</p>
        </div>
      </div>

      <!-- Характеристики (аккордеон) -->
      <div class="section">
        <div class="section-header" @click="toggleCharacteristics">
          <span>Характеристики</span>
          <span class="arrow">{{ showCharacteristics ? '▼' : '▶' }}</span>
        </div>
        <div v-show="showCharacteristics" class="section-body">
          <div v-for="(val, key) in detailData" :key="key" v-if="isCharacteristic(key, val)" class="char-row">
            <strong>{{ keyLabels[key] || key }}:</strong> {{ val }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '@/store/index.js'

const store = useStore()
const router = useRouter()
const route = useRoute()

const category = route.query.category
const detailData = ref(null)
const loading = ref(true)
const currentIndex = ref(0)
const thumbsRef = ref(null)

const variants = ref([])         // все варианты по общему sku
const showDescription = ref(false)
const showCharacteristics = ref(false)

// Настройка читаемых лейблов
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
  delivery_time: 'Доставка'
}

// Доступные опции
const sizeOptions = computed(() =>
  Array.from(new Set(variants.value.map(v => v.size_label)))
)
const colorOptions = computed(() =>
  Array.from(new Set(variants.value.map(v => v.color)))
)

// Текущее кол-во в корзине
const currentQuantity = ref(0)

// Функция загрузки деталей
async function fetchDetail() {
  loading.value = true
  detailData.value = null
  try {
    const vs = route.params.variant_sku
    const res = await fetch(`${store.url}/api/product?category=${encodeURIComponent(category)}&variant_sku=${encodeURIComponent(vs)}`)
    if (res.ok) {
      detailData.value = await res.json()
      currentQuantity.value = store.getProductQuantity(detailData.value)
      await loadVariants()              // загружаем варианты
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// Загрузка всех товаров категории и фильтр по sku
async function loadVariants() {
  try {
    const res = await fetch(`${store.url}/api/products?category=${encodeURIComponent(category)}`)
    if (res.ok && detailData.value) {
      const all = await res.json()
      variants.value = all.filter(p => p.sku === detailData.value.sku)
    }
  } catch (e) {
    console.error(e)
  }
}

// Переход на другой variant по опции
function selectVariantByOpt(type, opt) {
  const variant = variants.value.find(v => type === 'size' ? v.size_label === opt : v.color === opt)
  if (variant) {
    router.push({
      name: 'ProductDetail',
      params: { variant_sku: variant.variant_sku },
      query: { category }
    })
  }
}

// Свайп-обработчики
let touchStartX = 0, touchDeltaX = 0, isSwiping = false

function onTouchStart(e) {
  isSwiping = true
  touchStartX = e.touches[0].clientX
  touchDeltaX = 0
}
function onTouchMove(e) {
  if (!isSwiping) return
  touchDeltaX = e.touches[0].clientX - touchStartX
}
function onTouchEnd() {
  if (!isSwiping) return
  isSwiping = false
  if (touchDeltaX > 50) scrollToIndex(currentIndex.value - 1)
  else if (touchDeltaX < -50) scrollToIndex(currentIndex.value + 1)
}

// Переключение по клику/свайпу
function scrollToIndex(idx) {
  if (!detailData.value?.images) return
  const cnt = detailData.value.images.length
  currentIndex.value = ((idx % cnt) + cnt) % cnt
  nextTick(() => {
    const thumb = thumbsRef.value?.children[currentIndex.value]
    if (thumb) {
      const offset = thumb.offsetLeft - thumbsRef.value.clientWidth/2 + thumb.clientWidth/2
      thumbsRef.value.scrollTo({ left: offset, behavior: 'smooth' })
    }
  })
}

// Корзина + избранное контролы
function onIncrease(item) { store.increaseQuantity(item) }
function onDecrease(item) { store.decreaseQuantity(item) }

// Аккордеон
function toggleDescription() { showDescription.value = !showDescription.value }
function toggleCharacteristics() { showCharacteristics.value = !showCharacteristics.value }

// Определяем, что это характеристика
function isCharacteristic(key, val) {
  if (val == null) return false
  const excluded = [ 'images', 'name', 'brand', 'variant_sku', 'sku', 'count_in_stock', 'delivery_time', 'price', 'description']
  return !excluded.includes(key)
}

// Кнопка назад
function goBack() { router.back() }

// Следим за route
watch(
  () => [route.params.variant_sku, route.query.category],
  () => fetchDetail()
)

// Инициализация
onMounted(fetchDetail)
</script>

<style scoped lang="scss">

.product-detail {
  margin-top: 12vh;
  padding: 2vh;
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
}

/* 1. Загрузка */
.loading {
  text-align: center;
  color: #bbb;
  font-size: 18px;
  margin-top: 40px;
}

/* 2. Карточка */
.detail-card {
  background: $background-color;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

/* Шапка */
.top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.back-button {
  background: none;
  border: none;
  color: #007bff;
  font-size: 16px;
  cursor: pointer;
}
.availability span {
  font-weight: bold;
  font-size: 14px;
}

/* Заголовок */
.title-block {
  margin-bottom: 12px;
}
.brand { font-size: 14px; color: #777; }
.name  { font-size: 20px; margin: 4px 0; }
.sku   { font-size: 12px; color: #777; }

/* Галерея */
.carousel-container { margin-bottom: 16px; }
.main-image-wrapper {
  overflow: hidden;
  border-radius: 8px;
}
.main-image {
  width: 100%;
  display: block;
}
.thumbnails-wrapper {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  margin-top: 8px;
}
.thumbnails-wrapper::-webkit-scrollbar { display: none; }
.thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  opacity: 0.6;
  cursor: pointer;
  flex: 0 0 auto;
  border: 2px solid transparent;
}
.thumbnail.active {
  opacity: 1;
  border-color: #007bff;
}

/* Опции */
.options-block {
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin: 16px 0;
}
.option {
  display: flex;
  align-items: center;
  padding: 8px 0;
}
.option + .option { border-top: 1px solid #eee; }
label { flex: 0 0 80px; font-weight: bold; color: #333; }
.options-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.option-btn {
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
}
.option-btn.active {
  background: #007bff;
  color: #fff;
  border-color: #007bff;
}
.color-btn { min-width: 40px; text-align: center; }

/* Доставка + цена */
.delivery-price-block {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}
.price-row .price {
  font-size: 18px;
  font-weight: bold;
}

/* Действия */
.actions-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 16px 0;
}
.add-cart-button {
  background: #000;
  color: #fff;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
}
.quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}
.quantity-controls button {
  background: #007bff;
  color: #fff;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.quantity { font-size: 16px; }

/* Избранное */
.add-fav-button {
  background: #fff;
  color: #000;
  border: 1px solid #000;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
}
.remove-fav-button {
  background: #dc3545;
  color: #fff;
  border: none;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
}

/* Секции */
.section {
  margin-top: 16px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  cursor: pointer;
  padding: 8px 0;
  border-top: 1px solid #eee;
}
.section-body {
  padding: 8px 0;
  color: #555;
}
.arrow { font-size: 14px; }

/* Карточка характеристик */
.char-row {
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

/* Mobile tweaks */
@media (max-width: 600px) {
  .thumbnail { width: 48px; height: 48px; }
  .add-cart-button { padding: 10px; font-size: 14px; }
  .option-btn { padding: 4px 8px; font-size: 14px; }
}

</style>
