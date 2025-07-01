<template>
  <div class="product-detail">
    <!-- 1. Загрузка -->
    <div v-if="!store.detailData && !variantLoading" class="loading">
      Загрузка...
    </div>

    <!-- 2. Основная карточка -->
    <div v-else class="detail-wrapper">
      <div v-if="store.detailLoading || variantLoading" class="variant-spinner">
        Загрузка...
      </div>

      <div class="detail-card" :class="{ blurred: store.detailLoading || variantLoading }">
        <!-- Шапка: назад + наличие -->
        <div v-if="store.detailData" class="top-row">
          <button class="back-button" @click="goCatalog">← Назад</button>
          <div class="availability">
            <span v-if="store.detailData?.count_in_stock > 0">
              В НАЛИЧИИ: {{ store.detailData.count_in_stock }}
            </span>
            <span v-else>ПОД ЗАКАЗ</span>
          </div>
        </div>

        <!-- Бренд, имя, артикул -->
        <div v-if="store.detailData" class="title-block">
          <p class="brand">{{ store.detailData.brand }}</p>
          <h1 class="name">{{ store.detailData.name }}</h1>
          <p class="sku">артикул: {{ store.detailData.world_sku }}</p>
        </div>

        <!-- Галерея: главное + миниатюры + свайп -->
        <div v-if="store.detailData" class="carousel-container">
          <div class="main-image-wrapper" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
            <img :src="store.detailData.images[currentIndex]" alt="product" class="main-image"/>
          </div>
          <div class="thumbnails-wrapper" ref="thumbsRef">
            <img v-for="(img, idx) in store.detailData.images" :key="idx" :src="img" alt="" class="thumbnail"
                 :class="{ active: idx === currentIndex }" @click="scrollToIndex(idx)"/>
          </div>
        </div>

        <!-- 4. Параметры: Размер или Г×Ш×В + Цвет -->
        <div v-if="store.detailData" class="options-block">
          <!-- Размер -->
          <div class="option">
            <label>Размер</label>
            <div class="options-list">
              <button v-for="opt in sizeOptions" :key="opt" class="option-btn" @click="selectVariantByOpt('size', opt)"
                      :class="{ active: String(opt) === String(store.detailData.size_label) }">
                {{ opt }}
              </button>
            </div>
          </div>
          <!-- Цвет -->
          <div class="option">
            <label>Цвет</label>
            <div class="options-list">
              <button  v-for="opt in colorOptions" :key="opt" class="option-btn color-btn" :title="opt"
                       :class="{ active: opt === store.detailData.color }" @click="selectVariantByOpt('color', opt)">
                <img :src="getImageForColor(opt)" alt="" class="color-thumb"/>
              </button>
            </div>
          </div>
        </div>

        <!-- Доставка и цена -->
        <div v-if="store.detailData" class="delivery-price-block">
          <div class="delivery">
            <label>Доставка</label>
            <div class="options-list">
              <button v-for="(opt, idx) in visibleDeliveryOptions" :key="idx" class="option-btn"
                      :class="{ active: idx === selectedDeliveryIndex }" @click="selectedDeliveryIndex = idx">
                {{ opt.label }} {{ Math.round(store.detailData.price * opt.multiplier) }} ₽
              </button>
            </div>
          </div>
          <div class="price-row">
            <label>Цена:</label>
            <span class="price">{{ computedPrice }}₽</span>
          </div>
        </div>

        <!-- 1. Кнопка/контролы корзины + избранное -->
        <div v-if="store.detailData" class="actions-block">
          <div v-if="currentQuantity > 0" class="quantity-controls">
            <button @click="store.decreaseQuantity(cartItem)">➖</button>
            <span class="quantity">{{ currentQuantity }}</span>
            <button @click="store.increaseQuantity(cartItem)">➕</button>
            <button class="add-fav-button">Товар в корзине</button>
          </div>
          <button v-else type="button" class="add-cart-button" @click="handleAddToCart">
            Добавить в корзину
          </button>

          <button v-if="!store.isFavorite(store.detailData.color_sku)" type="button" class="add-fav-button" @click="store.addToFavorites(store.detailData.color_sku)">
            Добавить в избранное ♡
          </button>
          <button v-else type="button" class="remove-fav-button" @click="store.removeFromFavorites(store.detailData.color_sku)">
            Товар в избранном ♥
          </button>
        </div>

        <!-- Описание -->
        <div v-if="store.detailData" class="section" :class="{ 'section-disabled': !store.detailData?.description?.trim() }">
          <div class="section-header" @click="toggleDescription">
            <span>Описание</span>
            <span class="arrow">{{ showDescription ? '⯅' : '▼' }}</span>
          </div>
          <div class="section-body" :class="{ open: showDescription }">
            <p v-if="store.detailData?.description">{{ store.detailData.description }}</p>
          </div>
        </div>

        <!-- Характеристики -->
        <div v-if="store.detailData" class="section">
          <div class="section-header" @click="toggleCharacteristics">
            <span>Характеристики</span>
            <span class="arrow">{{ showCharacteristics ? '⯅' : '▼' }}</span>
          </div>
          <div class="section-body" :class="{ open: showCharacteristics }">
            <p class="char-row"><strong>Пол:</strong>{{ store.detailData.gender }}</p>
            <p class="char-row"><strong>Категория:</strong>{{ store.detailData.category }}</p>
            <p class="char-row"><strong>Подкатегория:</strong>{{ store.detailData.subcategory }}</p>
            <p class="char-row"><strong>Материал:</strong>{{ store.detailData.material }}</p>
            <p class="char-row" v-if="store.detailData.category === 'Обувь'">
              <strong>Глубина:</strong>{{ store.detailData.depth_mm }} мм
            </p>
            <p class="char-row" v-else-if="store.detailData.category === 'Одежда'">
              <strong>Плечи:</strong>{{ store.detailData.chest_cm }} см
              <strong>Высота:</strong>{{ store.detailData.height_cm }} см
            </p>
            <p class="char-row" v-else-if="store.detailData.category === 'Аксессуары'">
              <strong>Ширина:</strong>{{ store.detailData.width_cm }} см
              <strong>Высота:</strong>{{ store.detailData.height_cm }} см
              <strong>Глубина:</strong>{{ store.detailData.depth_cm }} см
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from '@/store/index.js'

const store = useStore()
const route = useRoute()
const router = useRouter()

const selectedDeliveryIndex  = ref(2)
const currentIndex = ref(0)
const thumbsRef = ref(null)
const showDescription = ref(false)
const showCharacteristics = ref(false)
const variantLoading = ref(false)

const colorOptions = computed(() =>
  Array.from(new Set(store.variants.map(v => v.color)))
)

// Показываем размеры только для текущего цвета
const sizeOptions = computed(() => {
  if (!store.detailData) return []
  const currentColor = store.detailData.color
  // фильтруем варианты по текущему цвету
  let opts = store.variants.filter(v => v.color === currentColor).map(v => v.size_label)
  // уникальность
  opts = Array.from(new Set(opts))
  // считаем числовыми только чистые цифры или с точкой
  const numericRe = /^\d+(\.\d+)?$/
  if (opts.every(o => numericRe.test(o))) {
    return opts.map(o => parseFloat(o)).sort((a, b) => a - b).map(n => n.toString())
  }
  // иначе — оставляем оригинальные строки (например "200-300-400")
  return opts
})

const computedPrice = computed(() => {
  if (!store.detailData) return 0
  const opt = visibleDeliveryOptions.value[selectedDeliveryIndex.value] || { multiplier: 1 }
  return Math.round(store.detailData.price * opt.multiplier)
})

const visibleDeliveryOptions = computed(() => {
  if (!store.detailData) return []
  return store.detailData.count_in_stock > 0 ? store.detailData.delivery_options : store.detailData.delivery_options.slice(1)
})

const cartItem = computed(() =>
  store.cart.items.find(i =>
    i.variant_sku === store.detailData?.variant_sku &&
    i.delivery_option?.label === visibleDeliveryOptions.value[selectedDeliveryIndex.value]?.label
  )
)

const currentQuantity = computed(() => {
  if (!store.detailData) return 0
  return store.cart.items.filter(i =>
    i.variant_sku === store.detailData.variant_sku &&
    i.delivery_option?.label === visibleDeliveryOptions.value[selectedDeliveryIndex.value]?.label
  ).length
})

async function handleAddToCart() {
  // 1) добавляем в корзину
  store.addToCart({
    ...store.detailData,
    delivery_option: visibleDeliveryOptions.value[selectedDeliveryIndex.value],
    computed_price: computedPrice.value
  })
  // 2) сбрасываем карусель на первый слайд
  currentIndex.value = 0
}

function getImageForColor(color) {
  const v = store.variants.find(v => v.color === color)
  return v?.image || ''
}

// Переход на другой variant по опции
function selectVariantByOpt(type, opt) {
  const cat = route.query.category
  if (type === 'size') {
    // ищем вариант с точно таким же size_label (строкой)
    const currentColor = store.detailData?.color
    const variant = store.variants.find(v => String(v.size_label) === opt && v.color === currentColor)
    if (variant && variant.variant_sku !== store.detailData.variant_sku) {
      router.replace({
        name: 'ProductDetail',
        params: { variant_sku: variant.variant_sku },
        query: { category: cat }
      })
    }
    return
  }

  if (type === 'color') {
    if (opt === store.detailData.color) return
    // все варианты того же цвета, в наличии
    const sameColor = store.variants.filter(v => v.color === opt && v.count_in_stock >= 0)
    // сортируем по «минимальному» размеру: числовые сначала
    sameColor.sort((a, b) => {
      const na = parseFloat(a.size_label)
      const nb = parseFloat(b.size_label)
      if (!isNaN(na) && !isNaN(nb)) return na - nb
      if (isNaN(na)) return 1
      if (isNaN(nb)) return -1
      // обе не числа — лексикографически
      return String(a.size_label).localeCompare(b.size_label)
    })
    const target = sameColor[0]
    if (target && target.variant_sku !== store.detailData.variant_sku) {
      router.replace({
        name: 'ProductDetail',
        params: { variant_sku: target.variant_sku },
        query: { category: cat }
      })
    }
  }
}

// Swipe
let touchStartX = 0, touchDeltaX = 0, isSwiping = false
function onTouchStart(e) {
  isSwiping = true;
  touchStartX = e.touches[0].clientX;
  touchDeltaX = 0
}

function onTouchMove(e) {
  if (!isSwiping) return;
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
  if (!store.detailData?.images) return
  const cnt = store.detailData.images.length
  currentIndex.value = ((idx % cnt) + cnt) % cnt
  nextTick(() => {
    const thumb = thumbsRef.value?.children[currentIndex.value]
    if (thumb) {
      const offset = thumb.offsetLeft - thumbsRef.value.clientWidth/2 + thumb.clientWidth/2
      thumbsRef.value.scrollTo({ left: offset, behavior: 'smooth' })
    }
  })
}

// Аккордеоны
function toggleDescription() {
  if (!store.detailData?.description?.trim()) return
  showDescription.value = !showDescription.value
}

function toggleCharacteristics() {
  showCharacteristics.value = !showCharacteristics.value
}

// ← Назад → каталог
function goCatalog() {
  router.push({ name: 'Catalog' })
}

// Инициализация
async function init() {
  showDescription.value = false
  showCharacteristics.value = false
  variantLoading.value = true
  try {
    const sku = route.params.variant_sku
    const cat = route.query.category
    await store.fetchDetail(sku, cat)
  } finally {
    variantLoading.value = false
  }
  selectedDeliveryIndex.value = Math.min(2, visibleDeliveryOptions.value.length - 1)
  currentIndex.value = 0
}

watch(
  () => [route.params.variant_sku, route.query.category],
  init
)

onMounted(init)

</script>

<style scoped lang="scss">

.product-detail {
  padding: 2vh;
  max-width: 480px;
  margin: 12vh auto 0;
}

.loading {
  text-align: center;
  color: #bbb;
  font-size: 18px;
  margin-top: 40px;
}

.detail-card {
  background: $grey-87;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  will-change: filter;
  transition: filter 0.2s ease-in-out;
}
.blurred {
  filter: blur(4px);
}

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

.title-block {
  margin-bottom: 12px;
}

.brand {
  font-size: 14px;
  color: #777;
}

.name  {
  font-size: 20px;
  margin: 4px 0;
}

.sku   {
  font-size: 12px;
  color: #777;
}

.carousel-container {
  margin-bottom: 16px;
}

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
  -webkit-overflow-scrolling: touch; /* плавный тач-скролл на iOS */
  scroll-snap-type: x mandatory;
}

.thumbnails-wrapper::-webkit-scrollbar {
  display: none;
}

.thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  opacity: 0.6;
  cursor: pointer;
  flex: 0 0 auto;
  border: 2px solid transparent;
  scroll-snap-align: center;
}

.thumbnail.active {
  opacity: 1;
  border-color: #007bff;
}

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

.option + .option {
  border-top: 1px solid #eee;
}

label {
  font-weight: bold;
  color: #333;
  margin: 10px 20px 20px 0;
}

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

.color-btn {
  min-width: 40px;
  text-align: center;
  padding: 4px;
}

.color-thumb {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 50%;
  display: block;
}

.value {
  color: #555;
  margin-left: 5px;
}

.delivery {
  margin-bottom: 12px;
}
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

.quantity {
  font-size: 16px;
}

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
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-height 0.5s ease-in-out, opacity 0.5s ease-in-out;
}
.section-body.open {
  max-height: 800px;
  opacity: 1;
}
/* «Неактивный» стиль для секции без описания */
.section-disabled {
  opacity: 0.6;
}
.section-disabled .section-header {
  color: #999;
  cursor: default;
  pointer-events: none;
}
.section-disabled .arrow {
  opacity: 0.5;
}

.arrow {
  font-size: 14px;
}

.char-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.detail-wrapper {
  position: relative;
}

.variant-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
  color: #666;
  background: rgba(255,255,255,0.8);
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

@media (max-width: 600px) {
  /* общий контейнер */
  .product-detail {
    padding: 1vh;
    margin-top: 8vh;
  }
  .detail-card {
    padding: 12px;
  }
  .carousel-container {
    margin-bottom: 12px; /* чуть меньше, чем 16px */
  }

  /* Шапка */
  .top-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .back-button {
    font-size: 14px;
  }

  /* Заголовок */
  .title-block .name {
    font-size: 18px;
  }

  /* Галерея */
  .main-image {
    max-height: 40vh;
    object-fit: contain;
  }
  .thumbnails-wrapper {
    gap: 4px;
  }
  .thumbnail {
    width: 40px;
    height: 40px;
  }

  /* Опции */
  .options-list {
    gap: 4px;
  }
  .option {
    flex-direction: column;
    align-items: flex-start;
    padding: 4px 0;
  }
  .option-btn {
    padding: 4px 8px;
    font-size: 14px;
  }

  /* Доставка и цена */
  .delivery-price-block {
    flex-direction: column;
    gap: 8px;
  }
  .price-row .price {
    font-size: 16px;
  }

  /* Кнопки действий */
  .actions-block {
    gap: 8px;
  }
  .add-cart-button, .add-fav-button, .remove-fav-button {
    width: 100%;
    font-size: 14px;
    padding: 10px;
  }
  .quantity-controls {
    gap: 6px;
  }

  /* Секции «Описание» и «Характеристики» */
  .section-header {
    padding: 8px;
  }
  .section-body p {
    font-size: 14px;
  }
}

</style>
