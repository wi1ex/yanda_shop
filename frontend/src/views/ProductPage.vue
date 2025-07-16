<template>
  <div class="product-detail">
    <!-- 1. Загрузка -->
    <div v-if="!store.detailData && !variantLoading" class="loading">
      <div class="spinner"></div>
    </div>

    <!-- 2. Основная карточка -->
    <div v-else class="detail-wrapper">
      <div v-if="store.detailLoading || variantLoading" class="variant-spinner">
        <div class="spinner"></div>
      </div>

      <div class="detail-card" :class="{ blurred: store.detailLoading || variantLoading }">
        <!-- Шапка: назад -->
        <div v-if="store.detailData" class="top-row">
          <button class="back-button" @click="goBack">
            <img :src="icon_arrow_back" alt="arrow back" />
            Назад
          </button>
        </div>

        <!-- Бренд, имя, артикул, наличие -->
        <div v-if="store.detailData" class="title-block">
          <div class="availability">
            <p class="brand">{{ store.detailData.brand }}</p>
            <span v-if="store.detailData?.count_in_stock > 0">
              В НАЛИЧИИ: {{ store.detailData.count_in_stock }}
            </span>
            <span v-else>ПОД ЗАКАЗ</span>
          </div>
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
            <button class="quantity-buttons" @click="store.decreaseQuantity(cartItem)">➖</button>
            <span class="quantity">{{ currentQuantity }}</span>
            <button class="quantity-buttons" @click="store.increaseQuantity(cartItem)">➕</button>
          </div>
          <button v-else type="button" class="cart-button" @click="handleAddToCart">
            Добавить в корзину
          </button>
          <button v-if="!store.isFavorite(store.detailData.color_sku)" type="button" class="fav-button" @click="store.addToFavorites(store.detailData.color_sku)">
            Добавить в избранное ♡
          </button>
          <button v-else type="button" class="fav-button" @click="store.removeFromFavorites(store.detailData.color_sku)">
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
            <p class="char-row"><strong>Пол:</strong>
              {{ store.detailData.gender === 'F' ? 'Женский' : store.detailData.gender === 'M' ? 'Мужской' : 'Унисекс'}}
            </p>
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
import icon_arrow_back from "@/assets/images/arrow_back.svg";

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
  if (type === 'size') {
    // ищем вариант с точно таким же size_label (строкой)
    const currentColor = store.detailData?.color
    const variant = store.variants.find(v => String(v.size_label) === opt && v.color === currentColor)
    if (variant && variant.variant_sku !== store.detailData.variant_sku) {
      router.replace({
        name: 'ProductDetail',
        params: { variant_sku: variant.variant_sku },
        query: { category: variant.category }
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
        query: { category: target.category }
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

// ← Назад
function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({ name: 'Home' })
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
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

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.product-detail {
  margin-top: 120px;
  .loading {
    text-align: center;
    margin-top: 40px;
    .spinner {
      margin: 0 auto;
      width: 40px;
      height: 40px;
      border: 6px solid $black-10;
      border-top-color: $black-100;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  }
  .detail-wrapper {
    display: flex;
    position: relative;
    .variant-spinner {
      display: flex;
      align-items: center;
      justify-content: center;
      position: absolute;
      padding: 12px;
      top: 50%;
      left: 50%;
      border-radius: 8px;
      transform: translate(-50%, -50%);
      background-color: $white-80;
      box-shadow: 0 2px 4px $black-10;
      .spinner {
        width: 24px;
        height: 24px;
        border: 4px solid $black-10;
        border-top-color: $black-100;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
    }
    .detail-card {
      display: flex;
      flex-direction: column;
      width: 100%;
      will-change: filter;
      transition: filter 0.25s ease-in-out;
      &.blurred {
        filter: blur(4px);
        pointer-events: none;
      }

      .top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
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
      }

      .title-block {
        display: flex;
        flex-direction: column;
        margin: 10px;
        .availability {
          display: flex;
          align-items: baseline;
          justify-content: space-between;
          .brand {
            margin: 0;
            font-size: 16px;
            color: $black-60;
            line-height: 100%;
            letter-spacing: -0.64px;
          }
          span {
            color: $grey-20;
            font-size: 12px;
            line-height: 100%;
            letter-spacing: -0.48px;
            opacity: 0.7;
          }
        }
        .name {
          margin: 12px 0 8px;
          color: $black-100;
          font-family: Bounded-250;
          font-size: 20px;
          line-height: 80%;
          letter-spacing: -1px;
        }
        .sku {
          margin: 0;
          color: $grey-20;
          font-size: 12px;
          line-height: 100%;
          letter-spacing: -0.48px;
          opacity: 0.7;
        }
      }

      .carousel-container {
        display: flex;
        flex-direction: column;
        margin-bottom: 24px;
        padding: 40px 10px 10px;
        background-color: $grey-89;
        .main-image-wrapper {
          overflow: hidden;
          border-radius: 8px;
          .main-image {
            width: 100%;
            display: block;
          }
        }
        .thumbnails-wrapper {
          display: flex;
          gap: 8px;
          overflow-x: auto;
          margin-top: 8px;
          -webkit-overflow-scrolling: touch; /* плавный тач-скролл на iOS */
          scroll-snap-type: x mandatory;
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
            &.active {
              opacity: 1;
              border-color: $black-40;
            }
          }
        }
        .thumbnails-wrapper::-webkit-scrollbar {
          display: none;
        }
      }

      .options-block {
        display: flex;
        flex-direction: column;
        background-color: $grey-95;
        padding: 16px 10px;
        border-radius: 4px;
        .option {
          display: flex;
          flex-direction: column;
          padding: 8px 0;
          label {
            margin: 10px 20px 20px 0;
            color: $grey-20;
            font-size: 15px;
            line-height: 110%;
            letter-spacing: -0.6px;
          }
          .options-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            .option-btn {
              padding: 6px 10px;
              border: 1px solid $white-100;
              border-radius: 6px;
              background-color: $white-100;
              cursor: pointer;
              color: $black-100;
              font-size: 15px;
              line-height: 100%;
              letter-spacing: -0.6px;
              &.active {
                background-color: $black-40;
                color: $white-100;
                border-color: $black-40;
              }
            }
            .color-btn {
              min-width: 40px;
              text-align: center;
              padding: 4px;
              .color-thumb {
                width: 50px;
                height: 50px;
                object-fit: cover;
                border-radius: 50%;
                display: block;
              }
            }
          }
        }
      }

      .delivery-price-block {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background-color: $grey-95;
        padding: 16px 10px;
        .delivery {
          margin-bottom: 12px;
          label {
            color: $grey-20;
            font-size: 15px;
            line-height: 100%;
            letter-spacing: -0.6px;
          }
          .options-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            .option-btn {
              padding: 6px 10px;
              border: 1px solid $grey-95;
              border-radius: 6px;
              background-color: $white-100;
              cursor: pointer;
              color: $black-100;
              font-size: 15px;
              line-height: 100%;
              letter-spacing: -0.6px;
              &.active {
                background-color: $black-40;
                color: $white-100;
                border-color: $black-40;
              }
            }
          }
        }
        .price-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          label {
            color: $grey-20;
            font-size: 15px;
            line-height: 110%;
            letter-spacing: -0.6px;
          }
          .price {
            color: $grey-20;
            font-family: Bounded-350;
            font-size: 16px;
            line-height: 80%;
            letter-spacing: -0.8px;
          }
        }
      }

      .actions-block {
        display: flex;
        flex-direction: column;
        gap: 8px;
        .quantity-controls {
          display: flex;
          align-items: center;
          gap: 12px;
          .quantity-buttons {
            background-color: $black-40;
            color: $white-100;
            border: none;
            padding: 6px 10px;
            border-radius: 6px;
            cursor: pointer;
          }
          .quantity {
            font-size: 16px;
          }
        }
        .cart-button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 24px;
          height: 56px;
          border-radius: 4px;
          background-color: $grey-20;
          border: none;
          color: $white-100;
          font-size: 16px;
          line-height: 100%;
          letter-spacing: -0.64px;
          cursor: pointer;
        }
        .fav-button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 24px;
          height: 56px;
          gap: 8px;
          border-radius: 4px;
          background-color: $white-80;
          border: none;
          color: $black-100;
          font-size: 16px;
          line-height: 100%;
          letter-spacing: -0.64px;
          cursor: pointer;
          img {
            width: 20px;
            height: 20px;
          }
        }
      }

      .section {
        margin-top: 16px;
        &.section-disabled {
          opacity: 0.6;
          .section-header {
            color: $grey-30;
            cursor: default;
            pointer-events: none;
          }
          .arrow {
            opacity: 0.5;
          }
        }
        .section-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          cursor: pointer;
          padding: 8px 0;
          span {
            color: $black-100;
            font-size: 15px;
            line-height: 110%;
            letter-spacing: -0.6px;
          }
          .arrow {
            font-size: 14px;
          }
        }
        .section-body {
          max-height: 0;
          opacity: 0;
          overflow: hidden;
          transition: max-height 0.5s ease-in-out, opacity 0.5s ease-in-out;
          &.open {
            max-height: 800px;
            opacity: 1;
          }
          .char-row {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 14px;
          }
        }
      }
    }
  }
}

@media (max-width: 600px) {
  .product-detail {
    margin-top: 96px;
  }
}

</style>
