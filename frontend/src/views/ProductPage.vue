<template>
  <div class="product-detail">
    <div class="line-vert"></div>
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
            <img :src="icon_arrow_grey" alt="arrow back" />
            Назад
          </button>
        </div>

        <div class="line-hor"></div>

        <!-- Бренд, имя, артикул, наличие -->
        <div v-if="store.detailData" class="title-block">
          <div class="availability">
            <p class="brand">{{ store.detailData.brand }}</p>
            <span v-if="store.detailData?.count_in_stock > 0">
              В НАЛИЧИИ: {{ store.detailData.count_in_stock }}
            </span>
            <span v-else>ПОД ЗАКАЗ</span>
          </div>
          <p class="name">{{ store.detailData.name }}</p>
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

        <!-- Параметры -->
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
          <div class="line-hor"></div>
          <!-- Цвет -->
          <div class="option">
            <label>Цвет</label>
            <div class="options-list">
              <button  v-for="opt in colorOptions" :key="opt" class="option-btn-color" :title="opt"
                       :class="{ active: opt === store.detailData.color }" @click="selectVariantByOpt('color', opt)">
                <img :src="getImageForColor(opt)" alt="" class="color-thumb"/>
              </button>
            </div>
          </div>
          <div class="line-hor"></div>
          <!-- Доставка -->
          <div class="option">
            <label>Доставка</label>
            <div class="options-list">
              <button v-for="(opt, idx) in visibleDeliveryOptions" :key="idx" class="option-btn-delivery"
                      :class="{ active: idx === selectedDeliveryIndex }" @click="selectedDeliveryIndex = idx">
                <span>{{ opt.label }}</span>
                <span class="delivery-price">{{ formatPrice(Math.round(store.detailData.price * opt.multiplier)) }} ₽</span>
              </button>
            </div>
          </div>
          <div class="line-hor"></div>
          <!-- Цена -->
          <div class="option-price">
            <label>Цена:</label>
            <span class="price">{{ formatPrice(computedPrice) }} ₽</span>
          </div>
        </div>

        <!-- В корзину -->
        <div class="quantity-controls">
          <div v-if="currentQuantity > 0" class="quantity-div">
            <button class="quantity-buttons" @click="store.decreaseQuantity(cartItem)">
              <img :src="icon_minus_grey" alt="" />
            </button>
            <span class="quantity">{{ currentQuantity }} в корзине</span>
            <button class="quantity-buttons" @click="store.increaseQuantity(cartItem)">
              <img :src="icon_plus_red" alt="" />
            </button>
          </div>
          <button v-if="currentQuantity > 0" type="button" class="cart-button" @click="store.openCartDrawer()">
            Оформить заказ
          </button>
          <button v-if="currentQuantity == 0" type="button" class="cart-button" @click="handleAddToCart">
            Добавить в корзину
          </button>
        </div>

        <!-- В избранное -->
        <div v-if="store.detailData" class="fav-block">
          <button v-if="!store.isFavorite(store.detailData.color_sku)" type="button" class="fav-button"
                  @click="store.addToFavorites(store.detailData.color_sku)">
            Добавить в избранное
            <img :src="icon_favorites_grey" alt="" />
          </button>
          <button v-else type="button" class="fav-button" @click="store.removeFromFavorites(store.detailData.color_sku)">
            Товар в избранном
            <img :src="icon_favorites_black" alt="" />
          </button>
        </div>

        <!-- Описание -->
        <div v-if="store.detailData" class="section" @click="toggleDescription"
             :class="{ 'section-disabled': !store.detailData?.description?.trim(), open: showDescription }">
          <div class="section-header">
            <span>Описание</span>
            <img :src="showDescription ? icon_arrow_up : icon_arrow_down" alt="" />
          </div>
          <div class="section-body" :class="{ open: showDescription }">
            <p>{{ store.detailData.description }}</p>
          </div>
        </div>

        <!-- Материал -->
        <div v-if="store.detailData" class="section"
             @click="toggleMaterial" :class="{ open: showMaterial }">
          <div class="section-header">
            <span>Материал</span>
            <img :src="showMaterial ? icon_arrow_up : icon_arrow_down" alt="" />
          </div>
          <div class="section-body" :class="{ open: showMaterial }">
            <p>{{ store.detailData.material }}</p>
          </div>
        </div>

        <!-- Размеры -->
        <div v-if="store.detailData" class="section"
             @click="toggleSize" :class="{ open: showSize }">
          <div class="section-header">
            <span>Размеры</span>
            <img :src="showSize ? icon_arrow_up : icon_arrow_down" alt="" />
          </div>
          <div class="section-body" :class="{ open: showSize }">
            <p class="char-row" v-if="store.detailData.category === 'Обувь'">
              <p v-if="store.detailData.depth_mm">Глубина: {{ store.detailData.depth_mm }} мм</p>
            </p>
            <p class="char-row" v-else-if="store.detailData.category === 'Одежда'">
              <p v-if="store.detailData.chest_cm">Плечи: {{ store.detailData.chest_cm }} см</p>
              <p v-if="store.detailData.height_cm">Высота: {{ store.detailData.height_cm }} см</p>
            </p>
            <p class="char-row" v-else-if="store.detailData.category === 'Аксессуары'">
              <p v-if="store.detailData.width_cm">Ширина: {{ store.detailData.width_cm }} см</p>
              <p v-if="store.detailData.height_cm">Высота: {{ store.detailData.height_cm }} см</p>
              <p v-if="store.detailData.depth_cm">Глубина:{{ store.detailData.depth_cm }} см</p>
            </p>
          </div>
        </div>

        <!-- Доставка и оплата -->
        <div v-if="store.parameters" class="section"
             @click="toggleDelivery" :class="{ open: showDelivery }">
          <div class="section-header">
            <span>Доставка и оплата</span>
            <img :src="showDelivery ? icon_arrow_up : icon_arrow_down" alt="" />
          </div>
          <div class="section-body" :class="{ open: showDelivery }">
            <p>Выкуп и доставка товара занимают от 14 до 25 дней.</p>
            <p>Все заказы тщательно упаковываются и передаются в курьерскую службу.</p>
            <p>Вы всегда можете отследить статус доставки в <a href="/profile">личном кабинете</a>.</p>
            <br>
            <p>Оплата производится полностью заранее после подтверждения заказа.</p>
            <p>Мы фиксируем цену, подтверждаем покупки и дальше занимаемся всем сами.</p>
          </div>
        </div>

        <!-- Возврат -->
        <div v-if="store.parameters" class="section" style="margin-bottom: 96px;"
             @click="toggleRefund" :class="{ open: showRefund }">
          <div class="section-header">
            <span>Возврат</span>
            <img :src="showRefund ? icon_arrow_up : icon_arrow_down" alt="" />
          </div>
          <div class="section-body" :class="{ open: showRefund }">
            <p>Мы принимаем возвраты только в случае бракованного товара или ошибки с нашей стороны.</p>
            <p>Каждый случай рассматривается индивидуально — напишите нам в
              <a v-if="store.parameters.url_social_telegram_user1" :href="store.parameters.url_social_telegram_user1"
                 target="_blank" rel="noopener">Telegram</a>, и мы найдём решение.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="line-hor"></div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from '@/store/index.js'
import icon_arrow_grey from "@/assets/images/arrow_grey.svg";
import icon_favorites_grey from "@/assets/images/favorites_grey.svg";
import icon_favorites_black from "@/assets/images/favorites_black.svg";
import icon_minus_grey from '@/assets/images/minus_grey.svg'
import icon_plus_red from '@/assets/images/plus_red.svg'
import icon_arrow_down from '@/assets/images/arrow_down.svg'
import icon_arrow_up from '@/assets/images/arrow_up.svg'

const store = useStore()
const route = useRoute()
const router = useRouter()

const selectedDeliveryIndex  = ref(2)
const currentIndex = ref(0)
const thumbsRef = ref(null)
const showDescription = ref(false)
const showMaterial = ref(false)
const showSize = ref(false)
const showDelivery = ref(false)
const showRefund = ref(false)
const variantLoading = ref(false)

function formatPrice(val) {
  return String(val).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

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
  const opts = [...store.detailData.delivery_options]
  if (store.detailData.count_in_stock > 0) {
    return opts
  } else {
    return opts.slice(1)
  }
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

function toggleMaterial() {
  showMaterial.value = !showMaterial.value
}

function toggleSize() {
  showSize.value = !showSize.value
}

function toggleDelivery() {
  showDelivery.value = !showDelivery.value
}

function toggleRefund() {
  showRefund.value = !showRefund.value
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
  showMaterial.value = false
  showSize.value = false
  showDelivery.value = false
  showRefund.value = false
  variantLoading.value = true
  try {
    const sku = route.params.variant_sku
    const cat = route.query.category
    await store.fetchDetail(sku, cat)
  } finally {
    variantLoading.value = false
  }
  selectedDeliveryIndex.value = 0
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
      z-index: 20;
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
          font-family: Bounded;
          font-weight: 250;
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
        padding: 24px 10px 10px;
        background-color: $grey-89;
        .main-image-wrapper {
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          .main-image {
            width: 100%;
          }
        }
        .thumbnails-wrapper {
          display: flex;
          gap: 4px;
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
          scroll-snap-type: x mandatory;
          .thumbnail {
            display: flex;
            flex: 0 0 auto;
            width: 68px;
            height: 68px;
            object-fit: cover;
            border-radius: 4px;
            cursor: pointer;
            scroll-snap-align: center;
            background-color: $white-40;
            &.active {
              background-color: $white-100;
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
        padding: 0 10px;
        border-radius: 4px 4px 0 0;
        .option {
          display: flex;
          flex-direction: column;
          gap: 16px;
          margin: 16px 0;
          label {
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
              padding: 8px;
              min-width: 50px;
              border: none;
              border-radius: 4px;
              background-color: $white-100;
              cursor: pointer;
              color: $black-100;
              font-size: 15px;
              line-height: 100%;
              letter-spacing: -0.6px;
              &.active {
                background-color: $black-100;
                color: $white-100;
              }
            }
            .option-btn-color {
              display: flex;
              margin-right: -4px;
              padding: 0;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              background-color: $white-40;
              .color-thumb {
                width: 50px;
                height: 50px;
                object-fit: cover;
              }
              &.active {
                background-color: $white-100;
              }
            }
            .option-btn-delivery {
              display: flex;
              flex-direction: column;
              margin-right: -4px;
              padding: 8px;
              min-width: 85px;
              gap: 8px;
              border-radius: 4px;
              border: none;
              background-color: $white-100;
              cursor: pointer;
              color: $black-100;
              font-size: 15px;
              line-height: 100%;
              letter-spacing: -0.6px;
              .delivery-price {
                font-size: 12px;
                line-height: 80%;
                letter-spacing: -0.48px;
                opacity: 0.4;
              }
              &.active {
                background-color: $black-100;
                color: $white-100;
                border-color: $black-40;
              }
            }
          }
        }
        .option-price {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin: 16px 0;
          label {
            color: $grey-20;
            font-size: 15px;
            line-height: 110%;
            letter-spacing: -0.6px;
          }
          .price {
            color: $grey-20;
            font-family: Bounded;
            font-weight: 250;
            font-size: 16px;
            line-height: 80%;
            letter-spacing: -0.8px;
          }
        }
      }

      .quantity-controls {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        background-color: $grey-95;
        .quantity-div {
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: calc(100% - 20px);
          height: 40px;
          border-radius: 4px 4px 0 0;
          background-color: $white-100;
          .quantity-buttons {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background: none;
            border: none;
            cursor: pointer;
            img {
              width: 20px;
              height: 20px;
              object-fit: cover;
            }
          }
          .quantity {
            font-size: 15px;
            line-height: 100%;
            letter-spacing: -0.6px;
          }
        }
        .cart-button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 24px;
          width: 100%;
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
      }

      .fav-block {
        display: flex;
        margin: 8px 0 40px;
        .fav-button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 24px;
          width: 100%;
          height: 40px;
          gap: 8px;
          border-radius: 4px;
          background-color: $white-100;
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
        display: flex;
        flex-direction: column;
        padding: 12px 10px;
        background-color: $grey-95;
        border-bottom: 1px solid $white-100;
        border-top: 1px solid $white-100;
        cursor: pointer;
        font-size: 15px;
        line-height: 110%;
        letter-spacing: -0.6px;
        &.section-disabled {
          cursor: default;
          pointer-events: none;
          .section-header {
            span {
              color: $black-40;
            }
          }
        }
        .section-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          span {
            color: $black-100;
          }
          img {
            width: 20px;
            height: 20px;
          }
        }
        .section-body {
          max-height: 0;
          opacity: 0;
          overflow: hidden;
          white-space: pre-wrap;
          transition: all 0.5s ease-in-out;
          &.open {
            margin-top: 24px;
            max-height: 800px;
            opacity: 1;
          }
          p {
            margin: 0;
            a {
              color: $red-active;
            }
          }
          .char-row {
            display: flex;
            flex-direction: column;
          }
        }
        &.open {
          background-color: $white-100;
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
