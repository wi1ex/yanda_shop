<template>
  <div class="catalog">
    <!-- HEADER: текст, логотип, категории, селект сортировки -->
    <header class="catalog-header">
      <!-- Логотип по центру -->
      <div class="header-logo">
        <span class="logo-title">{{ headerTitle }}</span>
        <sup class="logo-count">{{ totalItems }}</sup>
      </div>

      <!-- Текст слева -->
      <div class="header-text">
        <p>Здесь оригинальные вещи на любой вкус: от классики до уличного кэжуала.<br><br>
          Только проверенные бренды и актуальные коллекции. Одежда, в которой ты будешь выглядеть современно, уверенно и круто.</p>
      </div>

      <!-- Навигация по категориям под логотипом -->
      <nav class="header-cats">
        <!-- 1) Корневые категории -->
        <div v-if="!store.showSubcats" class="header-cats-template">
          <div class="header-cats-div">
            <button type="button" v-for="cat in store.categoryList" :key="cat" @click="onCategoryClick(cat)"
                    :class="['cat-btn', { active: store.selectedCategory === cat }]">
              <img :src="categoryImages[cat]" :alt="cat"/>
              <span>{{ cat }}</span>
            </button>
          </div>
        </div>

        <!-- 2) Подкатегории -->
        <div v-else class="header-cats-template">
          <div class="subcat-slider-wrapper">
            <button class="nav-btn prev" @click="scrollSubcats(-1)" :disabled="!canPrev">
              ‹
            </button>
            <div class="subcat-slider" ref="subcatSlider" @scroll.passive="onScroll"
                 @touchstart.passive="onTouchStart" @touchmove.passive="onTouchMove" @touchend.passive="onTouchEnd">
              <button class="cat-btn back-btn" @click="store.backToCats()">
                ← Назад
              </button>
              <button v-for="sub in store.subcatListMap[store.selectedCategory]" :key="sub" class="cat-btn"
                      :class="{ active: store.selectedSubcat === sub }" @click="store.pickSubcat(sub)">
                <img :src="categoryImages[store.selectedCategory]" alt="" />
                <span>{{ sub }}</span>
              </button>
            </div>
            <button class="nav-btn next" @click="scrollSubcats(1)" :disabled="!canNext">
              ›
            </button>
          </div>
        </div>
      </nav>
    </header>

    <div class="catalog-body">
      <!-- Основная колонка -->
      <main class="main-content">
        <!-- Мобильные контролы -->
        <div class="mobile-controls">
          <div class="mobile-sort">
            <span>Сортировка:</span>
            <select v-model="sortOption">
              <option value="date_desc">Новинки</option>
              <option value="sales_desc">Бестселлеры</option>
              <option value="price_asc">Цена ↑</option>
              <option value="price_desc">Цена ↓</option>
            </select>
          </div>

          <button type="button" @click="mobileFiltersOpen = !mobileFiltersOpen">
            Фильтры <i :class="['arrow', mobileFiltersOpen ? 'up' : 'down']"/>
          </button>

          <transition name="slide">
            <div v-if="mobileFiltersOpen" class="mobile-filters">
              <input type="number" v-model.number="store.filterPriceMin" placeholder="Мин. цена" />
              <input type="number" v-model.number="store.filterPriceMax" placeholder="Макс. цена" />
              <select v-model="store.filterColor">
                <option value="">Все цвета</option>
                <option v-for="color in distinctColors" :key="color" :value="color">{{ color }}</option>
              </select>
              <div class="gender-filter">
              <label :class="{ active: store.filterGender === '' }">
                <input type="radio" v-model="store.filterGender" value="" /> Все
              </label>
              <label :class="{ active: store.filterGender === 'M' }">
                <input type="radio" v-model="store.filterGender" value="M" /> Мужчинам
              </label>
              <label :class="{ active: store.filterGender === 'F' }">
                <input type="radio" v-model="store.filterGender" value="F" /> Женщинам
              </label>
              </div>
              <button type="button" @click="handleClearFilters" class="btn-clear">Сбросить</button>
            </div>
          </transition>
        </div>

        <!-- Сетка товаров -->
        <div class="products-grid" :class="{ blurred: productsLoading }">
          <article v-for="group in paged" :key="group.color_sku" class="product-card">
            <div @click="goToProductDetail(group)">
              <img :src="group.minPriceVariant.image" alt="" class="product-img"/>
              <div class="info">
                <p class="brand">{{ group.minPriceVariant.brand }}</p>
                <p class="name">{{ group.minPriceVariant.name }}</p>
                <p class="price">от {{ group.minPrice }} ₽</p>
              </div>
            </div>
            <button type="button" class="fav" v-if="!store.isFavorite(group.color_sku)" @click.stop="store.addToFavorites(group.color_sku)">♡</button>
            <button type="button" class="fav active" v-else @click.stop="store.removeFromFavorites(group.color_sku)">♥</button>
          </article>
        </div>

        <div class="load-more-container">
          <button type="button" v-if="paged.length < store.displayedProducts.length" @click="loadMore" class="btn-load-more">
            Ещё
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from '@/store/index.js'
import category_shoes from '@/assets/images/category_shoes.png'
import category_clothing from '@/assets/images/category_clothing.png'
import category_accessories from '@/assets/images/category_accessories.png'

const store = useStore()
const route = useRoute()
const router = useRouter()

const page = ref(1)
const perPage = 24
const mobileFiltersOpen = ref(false)
const productsLoading = ref(false)
const subcatSlider = ref(null)
const scrollPos = ref(0)
let touchStartX = 0
let scrollStartX = 0

const categoryImages = {
  'Одежда': category_clothing,
  'Обувь': category_shoes,
  'Аксессуары': category_accessories,
}

// const subcategoryImages = {
//   'Блуза':       subcat_blouse,
//   'Джинсы':      subcat_jeans,
//   // … остальные подкатегории …
// }

const canPrev = computed(() => scrollPos.value > 0)

const canNext = computed(() => {
  const el = subcatSlider.value
  if (!el) return false
  return scrollPos.value + el.clientWidth < el.scrollWidth
})

// стрелки: dir = ±1 — сдвигаем на две карточки
function scrollSubcats(dir) {
  const el = subcatSlider.value
  if (!el) return
  // ширина одной карточки + gap (примерно)
  const cardWidth = el.querySelector('.cat-btn').offsetWidth + 8
  el.scrollBy({
    left: dir * cardWidth * 2,
    behavior: 'smooth'
  })
}

// свайп
function onTouchStart(e) {
  touchStartX = e.touches[0].clientX
  scrollStartX = subcatSlider.value.scrollLeft
}

function onTouchMove(e) {
  const dx = touchStartX - e.touches[0].clientX
  subcatSlider.value.scrollLeft = scrollStartX + dx
}

function onTouchEnd() {
  // ничего не делаем — инерция браузера
}

function onScroll() {
  const el = subcatSlider.value
  if (!el) return
  scrollPos.value = el.scrollLeft
}

// 1) Количество отфильтрованных товаров
const totalItems = computed(() => store.displayedProducts.length)

// 2) Динамический заголовок
const headerTitle = computed(() => {
  if (store.filterGender === 'M') return 'ДЛЯ НЕГО'
  if (store.filterGender === 'F') return 'ДЛЯ НЕЁ'
  return 'КАТАЛОГ'
})

// товары для отображения: первые page*perPage элементов
const paged = computed(() =>
  store.displayedProducts.slice(0, page.value * perPage)
)

const sortOption = computed({
  get() { return `${store.sortBy}_${store.sortOrder}` },
  set(v) {
    const [by, order] = v.split('_')
    store.sortBy = by
    store.sortOrder = order
  }
})

const distinctColors = computed(() =>
  Array.from(new Set(store.products.map(p => p.color).filter(Boolean)))
)

// увеличить страницу (если есть ещё)
function loadMore() {
  if (page.value * perPage < store.displayedProducts.length) {
    page.value++
  }
}

function handleClearFilters() {
  animateGrid()
  store.clearFilters()
}

function onCategoryClick(cat) {
  page.value = 1
  if (!store.showSubcats) {
    // если мы в режиме корней, то переключаемся в подкатегории
    store.selectedCategory = cat
    store.openSubcats()
  } else if (store.selectedCategory !== cat) {
    // если уже в подкатегориях, но кликнули по другому корню — перейти в его подкатегории
    store.selectedCategory = cat
    store.currentSubcatPage = 0
    store.selectedSubcat = ''
    store.filterSubcat = ''
  } else {
    // если кликнули на тот же корень повторно — возврат к корням
    store.backToCats()
  }
}

function goToProductDetail(group) {
  // из всех вариантов данного цвета выбираем сначала подходящие по фильтру цены (если есть)
  let candidates = group.variants.filter(v => v.count_in_stock >= 0)

  if (store.filterPriceMin != null || store.filterPriceMax != null) {
    candidates = candidates.filter(v =>
      (store.filterPriceMin == null || v.price >= store.filterPriceMin) &&
      (store.filterPriceMax == null || v.price <= store.filterPriceMax)
    )
    if (!candidates.length) {
      // если внутри не попало ни одного — возвращаемся к всем
      candidates = group.variants.filter(v => v.count_in_stock >= 0)
    }
  }

  // сортируем кандидатов по минимальному размеру
  candidates.sort((a, b) => {
    const na = parseFloat(a.size_label), nb = parseFloat(b.size_label)
    if (!isNaN(na) && !isNaN(nb)) return na - nb
    if (isNaN(na)) return 1
    if (isNaN(nb)) return -1
    return String(a.size_label).localeCompare(b.size_label)
  })

  const target = candidates[0]
  router.push({
    name: 'ProductDetail',
    params: { variant_sku: target.variant_sku },
    query: { category: target.category }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// вспомогательная функция «анимации» (браур → снятие)
function animateGrid() {
  productsLoading.value = true
  // после следующего рендера через 200 мс убираем блюр
  nextTick(() => {
    setTimeout(() => {
      productsLoading.value = false
    }, 200)
  })
}

async function loadCategory(cat) {
  productsLoading.value = true
  await store.fetchProducts(cat)
  productsLoading.value = false
}

watch(() => store.selectedCategory, (cat) => { page.value = 1; loadCategory(cat)})
watch(() => sortOption.value, () => { page.value = 1; animateGrid() })
watch(() => store.filterColor, () => { page.value = 1; animateGrid() })
watch(() => store.filterGender, () => { page.value = 1; animateGrid() })
watch(() => [store.filterPriceMin, store.filterPriceMax], () => { page.value = 1; animateGrid() })

// При монтировании грузим товары
onMounted(() => {
  if (route.query.sort) {
    const [by, order] = String(route.query.sort).split('_')
    store.sortBy = by
    store.sortOrder = order
  }
  if (route.query.gender) {
    const g = route.query.gender
    store.filterGender = (g === 'M' || g === 'F') ? g : ''
  }
  if (subcatSlider.value) {
    subcatSlider.value.scrollLeft = 0
    scrollPos.value = 0
  }
  animateGrid()
  loadCategory(store.selectedCategory)
})
</script>

<style scoped lang="scss">
.catalog {
  margin-top: 120px;
  /* === HEADER (мобильный) === */
  .catalog-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    .header-logo {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      gap: 4px;
      .logo-title {
        color: $black-100;
        font-family: Bounded;
        font-weight: 400;
        font-size: 32px;
        line-height: 90%;
        letter-spacing: -2.24px;
      }
      .logo-count {
        color: $red-active;
        font-size: 15px;
        line-height: 110%;
        letter-spacing: -0.6px;
      }
    }
    .header-text {
      margin: 24px 0 40px;
      width: 75%;
      text-align: center;
      p {
        margin: 0;
        color: $grey-20;
        font-size: 15px;
        line-height: 110%;
        letter-spacing: -0.6px;
      }
    }
    .header-cats {
      display: flex;
      width: 100%;
      .header-cats-template {
        display: flex;
        flex-direction: column;
        padding: 0 10px;
        width: 100%;
        .header-cats-div {
          display: flex;
          width: 100%;
          gap: 8px;
          .cat-btn {
            display: flex;
            flex-direction: column;
            background: $white-100;
            border-radius: 12px;
            padding: 12px;
            width: 113px;
            height: 113px;
            text-align: center;
            transition: box-shadow 0.25s ease-in-out;
            cursor: pointer;
            &.active {
              box-shadow: 0 0 0 2px $red-active;
            }
            img {
              width: 48px;
              height: 48px;
              object-fit: contain;
              margin-bottom: 6px;
            }
            span {
              display: block;
              font-size: 14px;
              line-height: 1;
              color: $black-100;
            }
          }
        }
        .subcat-slider-wrapper {
          display: flex;
          align-items: center;
          width: 100%;
          .nav-btn {
            flex: 0 0 32px;
            background: $white-80;
            border-radius: 8px;
            font-size: 24px;
            line-height: 1;
            text-align: center;
            padding: 4px;
            cursor: pointer;
            &.prev[disabled],
            &.next[disabled] {
              opacity: 0.3;
              cursor: default;
            }
          }
          .subcat-slider {
            flex: 1;
            overflow-x: auto;
            display: flex;
            gap: 8px;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
            padding: 4px 0;
            &::-webkit-scrollbar {
              display: none;
            }
            .cat-btn,
            .back-btn {
              flex: 0 0 auto;
              width: 96px;
              height: 96px;
              background: $white-100;
              border-radius: 12px;
              padding: 8px;
              text-align: center;
              transition: box-shadow 0.2s;
            }
            .cat-btn.active {
              box-shadow: 0 0 0 2px $red-active;
            }
            .back-btn {
              background: $white-80;
            }
            img {
              width: 40px;
              height: 40px;
              object-fit: contain;
              margin-bottom: 4px;
            }
            span {
              display: block;
              font-size: 12px;
              color: $black-100;
            }
          }
        }
      }
    }
  }
  /* === MOBILE CONTROLS === */
  .catalog-body {
    display: flex;
    flex-direction: column;
    margin-top: 40px;
    .main-content {
      display: flex;
      flex-direction: column;
      .mobile-controls {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 16px;
        .mobile-sort {
          display: flex;
          align-items: center;
          gap: 8px;
          span {
            font-size: 14px;
            color: $black-100;
          }
          select {
            flex: 1;
            padding: 8px;
            border: 1px solid $grey-89;
            border-radius: 6px;
            background: $white-100;
          }
        }
        button {
          width: 100%;
          padding: 10px;
          background: $white-100;
          border: 1px solid $grey-89;
          border-radius: 6px;
          text-align: left;
          display: flex;
          justify-content: space-between;
          align-items: center;
          cursor: pointer;
          .arrow {
            width: 8px;
            height: 8px;
            border: solid $black-100;
            border-width: 0 2px 2px 0;
            display: inline-block;
            transform: rotate(45deg);
            &.up {
              transform: rotate(-135deg);
            }
          }
        }
        .mobile-filters {
          background: $white-100;
          border: 1px solid $grey-89;
          border-radius: 6px;
          padding: 12px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          input,
          select {
            padding: 8px;
            border: 1px solid $grey-89;
            border-radius: 6px;
          }
          .gender-filter {
            display: flex;
            gap: 12px;
            label {
              flex: 1;
              text-align: center;
              padding: 8px 0;
              background: $white-80;
              border-radius: 6px;
              font-size: 14px;
              cursor: pointer;
              position: relative;
              input {
                position: absolute;
                opacity: 0;
                pointer-events: none;
              }
              &.active {
                background: $red-active;
                color: $white-100;
              }
            }
          }
          .btn-clear {
            padding: 8px;
            background: $red-error;
            color: $white-100;
            border: none;
            border-radius: 6px;
            cursor: pointer;
          }
        }
      }
    }
  }
  /* === PRODUCTS GRID (только тут используем grid) === */
  .products-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    &.blurred {
      filter: blur(4px);
    }
  }
  .product-card {
    background: $white-100;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    position: relative;
    transition: transform 0.25s ease-in-out;
    .product-img {
      width: 100%;
      border-radius: 8px;
    }
    .info {
      margin-top: 8px;
      .brand {
        font-size: 12px;
        color: $black-60;
      }
      .name {
        font-size: 16px;
        color: $black-100;
        margin: 4px 0;
      }
      .price {
        font-size: 14px;
        color: $black-100;
      }
    }
    .fav {
      position: absolute;
      top: 8px;
      right: 8px;
      background: none;
      border: none;
      font-size: 16px;
      cursor: pointer;
      &.active {
        color: $red-active;
      }
    }
  }
  /* === LOAD MORE === */
  .load-more-container {
    text-align: center;
    margin: 16px 0;
    .btn-load-more {
      width: 100%;
      padding: 12px 0;
      background: $red-active;
      color: $white-100;
      border: none;
      border-radius: 6px;
      font-size: 18px;
      cursor: pointer;
    }
  }
  /* === SLIDE TRANSITIONS === */
  .slide-enter-active,
  .slide-leave-active {
    transition: all 0.25s ease-in-out;
  }
  .slide-enter-from,
  .slide-leave-to {
    max-height: 0;
    opacity: 0;
    overflow: hidden;
  }
  .slide-enter-to,
  .slide-leave-from {
    max-height: 500px;
    opacity: 1;
  }
}

/* MOBILE (<600px) */
@media (max-width: 600px) {
  .catalog {
    margin-top: 96px;
  }
}
</style>
