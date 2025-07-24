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
        <p>Здесь оригинальные вещи на любой вкус: от классики до уличного кэжуала.</p>
        <p>Только проверенные бренды и актуальные коллекции. Одежда, в которой ты будешь выглядеть современно, уверенно и круто.</p>
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
          <div class="header-cats-div">
            <!-- Кнопка «назад» -->
            <button type="button" class="cat-btn back-btn" @click="store.backToCats()">← Назад</button>
            <!-- Список текущих 2-х подкатегорий -->
            <button type="button" v-for="sub in visibleSubcats" :key="sub" @click="store.pickSubcat(sub)"
                    :class="['cat-btn', { active: store.selectedSubcat === sub }]">
<!--              <img :src="subcategoryImages[sub]" :alt="sub"/>-->
              <span>{{ sub }}</span>
            </button>
          </div>
          <div class="header-cats-div">
            <!-- Кнопки листания -->
            <button type="button" v-if="canPrev" class="cat-btn nav-btn" @click="store.prevSubcatPage()">‹</button>
            <button type="button" v-if="canNext" class="cat-btn nav-btn" @click="store.nextSubcatPage()">›</button>
          </div>
        </div>
      </nav>
    </header>

    <div>
      <!-- Основная колонка -->
      <main>
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

const visibleSubcats = computed(() => {
  const all = store.subcatListMap[store.selectedCategory] || []
  const page = store.currentSubcatPage
  return all.slice(page * 2, page * 2 + 2)
})

const canPrev = computed(() =>
  store.currentSubcatPage > 0
)

const canNext = computed(() => {
  const all = store.subcatListMap[store.selectedCategory] || []
  return (store.currentSubcatPage + 1) * 2 < all.length
})

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
  animateGrid()
  loadCategory(store.selectedCategory)
})
</script>

<style scoped lang="scss">
.catalog {
  background: $grey-87;
  padding: 16px;
  /* === HEADER (мобильный) === */
  &-header {
    text-align: center;
    margin: 32px 0 16px;
    .header-logo {
      display: flex;
      justify-content: center;
      align-items: flex-end;
      .logo-title {
        font-family: Bounded;
        font-weight: 500;
        font-size: 32px;
        line-height: 0.9;
        letter-spacing: -2.24px;
        color: $black-100;
      }
      .logo-count {
        font-size: 15px;
        line-height: 1.1;
        letter-spacing: -0.6px;
        color: $red-active;
        margin-left: 4px;
        margin-bottom: 2px;
      }
    }
    .header-text {
      color: $black-70;
      font-size: 15px;
      line-height: 1.2;
      letter-spacing: -0.6px;
      margin-top: 8px;
      p + p {
        margin-top: 6px;
      }
    }
    .header-cats {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 12px;
      margin-top: 16px;
      .cat-btn {
        background: $white-100;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        transition: box-shadow 0.2s;
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
      .back-btn,
      .nav-btn {
        background: $white-80;
        border-radius: 12px;
        padding: 12px 8px;
        font-size: 18px;
        cursor: pointer;
      }
    }
  }
  /* === MOBILE CONTROLS === */
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
  /* === PRODUCTS GRID (только тут используем grid) === */
  .products-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);;
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
    transition: transform 0.2s;
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
    transition: all 0.3s ease;
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

  /* MOBILE (<600px) */
  @media (max-width: 600px) {
    .catalog {
      .products-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
  }
}
</style>
