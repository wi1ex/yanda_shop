<template>
  <div class="product-detail">
    <!-- Кнопка “Назад к каталогу” -->
    <button class="back-button" @click="goBack">← Назад в каталог</button>

    <!-- Индикатор загрузки -->
    <div v-if="loading" class="loading">Загрузка...</div>

    <!-- Когда detailData загружены -->
    <div v-else-if="detailData" class="detail-card">
      <!-- Карусель изображений -->
      <div v-if="detailData.images && detailData.images.length" class="carousel" ref="carouselRef"
           @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
        <div class="images-wrapper">
          <img v-for="(imgSrc, idx) in detailData.images" :key="idx" :src="imgSrc" alt="product image"
               class="detail-image" :class="{ active: idx === currentIndex }"/>
        </div>

        <!-- Кнопка «Вперёд» -->
        <button v-if="detailData.images.length > 1" class="nav-button left" @click="scrollToIndex(currentIndex - 1)">
          ◀
        </button>

        <!-- Кнопка «Назад» -->
        <button v-if="detailData.images.length > 1" class="nav-button right" @click="scrollToIndex(currentIndex + 1)">
          ▶
        </button>
      </div>

      <!-- Если изображений вообще нет -->
      <div v-else class="no-image">Нет изображений</div>

      <div class="detail-info">
        <!-- Название -->
        <h2 class="detail-name">{{ detailData.name }}</h2>

        <!-- Цена -->
        <p class="detail-price">{{ detailData.price }} ₽</p>

        <!-- Выводим все доступные поля из detailData -->
        <p v-if="detailData.sku" class="detail-field">
          <strong>SKU:</strong> {{ detailData.sku }}
        </p>
        <p v-if="detailData.gender" class="detail-field">
          <strong>Пол:</strong> {{ detailData.gender }}
        </p>
        <p v-if="detailData.category" class="detail-field">
          <strong>Категория:</strong> {{ detailData.category }}
        </p>
        <p v-if="detailData.subcategory" class="detail-field">
          <strong>Субкатегория:</strong> {{ detailData.subcategory }}
        </p>
        <p v-if="detailData.brand" class="detail-field">
          <strong>Бренд:</strong> {{ detailData.brand }}
        </p>
        <p v-if="detailData.description" class="detail-field">
          <strong>Описание:</strong> {{ detailData.description }}
        </p>
        <p v-if="detailData.material" class="detail-field">
          <strong>Материал:</strong> {{ detailData.material }}
        </p>
        <p v-if="detailData.color" class="detail-field">
          <strong>Цвет:</strong> {{ detailData.color }}
        </p>
        <p v-if="detailData.size_label" class="detail-field">
          <strong>Размер:</strong> {{ detailData.size_label }}
        </p>
        <p v-if="detailData.width_mm" class="detail-field">
          <strong>Ширина (мм):</strong> {{ detailData.width_mm }}
        </p>
        <p v-if="detailData.height_mm" class="detail-field">
          <strong>Высота (мм):</strong> {{ detailData.height_mm }}
        </p>
        <p v-if="detailData.depth_mm" class="detail-field">
          <strong>Глубина (мм):</strong> {{ detailData.depth_mm }}
        </p>
        <p v-if="detailData.size_guide_url" class="detail-field">
          <strong>Size Guide:</strong>
          <a :href="detailData.size_guide_url" target="_blank">ссылка</a>
        </p>
        <p v-if="detailData.delivery_time" class="detail-field">
          <strong>Время доставки:</strong> {{ detailData.delivery_time }}
        </p>

        <!-- Кнопки управления количеством в корзине -->
        <div class="detail-cart-controls">
          <div v-if="currentQuantity > 0" class="quantity-controls">
            <button @click="onDecrease(detailData)">➖</button>
            <span class="quantity">{{ currentQuantity }}</span>
            <button @click="onIncrease(detailData)">➕</button>
          </div>
          <button v-else class="add-button" @click="store.addToCart(detailData)">
            Купить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '@/store/index.js'

const route = useRoute()
const router = useRouter()
const store = useStore()

// Берём sku из route.params и category из route.query
const sku = route.params.sku
const category = route.query.category

const detailData = ref(null)

// Индикатор загрузки
const loading = ref(true)
// Текущий индекс (номер картинки)
const currentIndex = ref(0)
// Ссылка на DOM-узел .carousel (обёртка скролла)
const carouselRef = ref(null)

// Для свайпов
let touchStartX = 0
let touchDeltaX = 0
let isSwiping = false

function onTouchStart(evt) {
  if (!carouselRef.value) return
  isSwiping = true
  touchStartX = evt.touches[0].clientX
  touchDeltaX = 0
}

function onTouchMove(evt) {
  if (!isSwiping) return
  const currentX = evt.touches[0].clientX
  touchDeltaX = currentX - touchStartX
}

function onTouchEnd() {
  if (!isSwiping) return
  isSwiping = false
  if (touchDeltaX > 50) {
    scrollToIndex(currentIndex.value - 1)
  } else if (touchDeltaX < -50) {
    scrollToIndex(currentIndex.value + 1)
  } else {
    scrollToIndex(currentIndex.value)
  }
  touchDeltaX = 0
}

function scrollToIndex(num, smooth = true) {
  if (!detailData.value || !detailData.value.images) return
  const count = detailData.value.images.length
  let idx = ((num % count) + count) % count
  currentIndex.value = idx
  const wrapper = carouselRef.value?.querySelector('.images-wrapper')
  if (!wrapper) return
  const width = wrapper.clientWidth
  const targetScrollLeft = idx * width
  wrapper.scrollTo({
    left: targetScrollLeft,
    behavior: smooth ? 'smooth' : 'auto'
  })
}

// Функция “Назад в каталог”
function goBack() {
  router.push({ name: 'Catalog' })
}

// Функция получения деталей товара
async function fetchDetail() {
  loading.value = true
  detailData.value = null
  try {
    const response = await fetch(`${store.url}/api/product?category=${encodeURIComponent(category)}&sku=${encodeURIComponent(sku)}`)
    if (!response.ok) {
      console.error('Ошибка при получении детализации товара:', response.statusText)
      detailData.value = null
    } else {
      detailData.value = await response.json()
    }
  } catch (err) {
    console.error('Ошибка сети при fetchDetail:', err)
    detailData.value = null
  } finally {
    loading.value = false
  }
}

// При монтировании сразу вызываем fetchDetail
onMounted(async () => {
  await fetchDetail()
  await nextTick()
  scrollToIndex(0, false)
})

// При изменении sku или category — обновляем данные
watch(
  () => [route.params.sku, route.query.category],
  async () => {
    await fetchDetail()
    await nextTick()
    scrollToIndex(0, false)
  }
)

const currentQuantity = ref(0)

// Следим за detailData, чтобы обновить количество в корзине
watch(
  () => detailData.value,
  newVal => {
    if (newVal) {
      currentQuantity.value = store.getProductQuantity(newVal)
    }
  }
)

// Следим за изменением корзины
watch(
  () => store.cart.items.length,
  () => {
    if (detailData.value) {
      currentQuantity.value = store.getProductQuantity(detailData.value)
    }
  }
)

// При клике на “➕” рядом с детальным товаром:
function onIncrease(item) {
  store.increaseQuantity(item)
}

// При клике на “➖” рядом с детальным товаром:
function onDecrease(item) {
  store.decreaseQuantity(item)
}
</script>

<style scoped lang="scss">
.product-detail {
  margin-top: 12vh;
  padding: 2vh;
}

/* Стили для кнопки “Назад” */
.back-button {
  display: flex;
  justify-self: center;
  margin-bottom: 16px;
  padding: 1vh 2vh;
  border-radius: 6px;
  background: #292e3f;
  color: #fff;
  border: 1px solid #bbb;
  cursor: pointer;
  transition: background 0.2s;
}

/* Состояние “Загрузка” */
.loading {
  color: #bbb;
  font-size: 18px;
  text-align: center;
  margin-top: 40px;
}

/* Карточка товара */
.detail-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: $background-color;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Карусель изображений */
.carousel {
  position: relative;
  margin-bottom: 20px;
  overflow: hidden;
}

.images-wrapper {
  display: flex;
  overflow-x: scroll;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}
.images-wrapper::-webkit-scrollbar {
  display: none;
}

.detail-image {
  flex: 0 0 100%;
  width: 100%;
  max-width: 300px;
  scroll-snap-align: center;
  border-radius: 8px;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.detail-image.active {
  transform: scale(1);
}

/* Кнопки “◀ ▶” */
.nav-button {
  background: rgba(0, 0, 0, 0.4);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  transition: background 0.2s;
}
.nav-button.left {
  left: 8px;
}
.nav-button.right {
  right: 8px;
}

/* Если изображений нет */
.no-image {
  color: #bbb;
  font-size: 16px;
  margin-bottom: 20px;
}

/* Блок с текстовой информацией */
.detail-info {
  margin-top: 16px;
  width: 100%;
  max-width: 500px;
}

/* Заголовок (название) */
.detail-name {
  font-size: 24px;
  margin-bottom: 8px;
}

/* Цена */
.detail-price {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 12px;
}

/* Общий стиль для всех полей */
.detail-field {
  display: flex;
  font-size: 14px;
  color: #ccc;
  margin-bottom: 8px;
  word-wrap: break-word;
}
.detail-field a {
  margin-left: 0.5vh;
  color: #ccc;
}

/* Контейнер для управления корзиной */
.detail-cart-controls {
  margin-top: 16px;
}

/* Кнопка “Купить” */
.add-button {
  background: #007bff;
  color: white;
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s;
}

/* Кнопки “➖/➕” */
.quantity-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}
.quantity-controls button {
  background: #007bff;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.quantity {
  font-size: 16px;
  font-weight: bold;
  color: white;
}
</style>
