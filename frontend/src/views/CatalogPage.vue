<template>
  <div class="catalog">
    <!-- HEADER: текст, логотип, категории, селект сортировки -->
    <header class="catalog-header">
      <!-- Текст слева -->
      <div class="header-text">
        <p>Здесь оригинальные вещи на любой вкус: от классики до уличного кэжуала.</p>
        <p>Только проверенные бренды и актуальные коллекции. Одежда, в которой ты будешь выглядеть современно, уверенно и круто.</p>
      </div>

      <!-- Логотип по центру -->
      <div class="header-logo">
        <span class="logo-title">КАТАЛОГ</span><sup class="logo-year">XYZ</sup>
      </div>

      <!-- Селект сортировки (вёрстка web) -->
      <div class="header-sort desktop-only">
        <span>Сортировка:</span>
        <select v-model="sortOption">
          <option value="date_desc">Новинки</option>
          <option value="price_asc">Цена ↑</option>
          <option value="price_desc">Цена ↓</option>
        </select>
      </div>

      <!-- Навигация по категориям под логотипом -->
      <nav class="header-cats">
        <button v-for="cat in store.categoryList" :key="cat" @click="onCategoryClick(cat)"
                :class="['cat-btn', { active: cat === store.selectedCategory }]">
          <img :src="`/icons/${cat}.svg`" :alt="cat" />
          <span>{{ cat }}</span>
        </button>
      </nav>
    </header>

    <div class="catalog-body">
      <!-- Фильтры слева (desktop) -->
      <aside class="sidebar desktop-only">
        <div class="filters-panel">
          <input type="number" v-model.number="store.filterPriceMin" placeholder="Мин. цена" />
          <input type="number" v-model.number="store.filterPriceMax" placeholder="Макс. цена" />
          <select v-model="store.filterColor">
            <option value="">Все цвета</option>
            <option v-for="color in distinctColors" :key="color" :value="color">{{ color }}</option>
          </select>
          <button @click="handleClearFilters" class="btn-clear">Сбросить</button>
        </div>
      </aside>

      <!-- Основная колонка -->
      <main class="main-content">
        <!-- Мобильные контролы -->
        <div class="mobile-controls mobile-only">
          <div class="mobile-sort">
            <span>Сортировка:</span>
            <select v-model="sortOption">
              <option value="date_desc">Новинки</option>
              <option value="price_asc">Цена ↑</option>
              <option value="price_desc">Цена ↓</option>
            </select>
          </div>

          <button @click="mobileFiltersOpen = !mobileFiltersOpen">
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
              <button @click="handleClearFilters" class="btn-clear">Сбросить</button>
            </div>
          </transition>
        </div>

        <!-- Сетка товаров -->
        <div class="products-grid" :class="{ blurred: productsLoading }">
          <article v-for="group in store.displayedProducts" :key="group.color_sku" class="product-card">
            <div class="clickable" @click="goToProductDetail(group)">
              <img :src="group.minPriceVariant.image" alt="" class="product-img"/>
              <div class="info">
                <p class="brand">{{ group.minPriceVariant.brand }}</p>
                <p class="name">{{ group.minPriceVariant.name }}</p>
                <p class="price">от {{ group.minPrice }} ₽</p>
              </div>
            </div>
            <button class="fav" v-if="!store.isFavorite(group.color_sku)" @click.stop="store.addToFavorites(group.color_sku)">♡</button>
            <button class="fav active" v-else @click.stop="store.removeFromFavorites(group.color_sku)">♥</button>
          </article>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

const mobileFiltersOpen = ref(false)
const productsLoading = ref(false)

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

function handleClearFilters() {
  animateGrid()
  store.clearFilters()
}

function onCategoryClick(cat) {
  store.changeCategory(cat)
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
    query: { category: store.selectedCategory }
  })
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

watch(() => store.selectedCategory, loadCategory)
// следим за сортировкой
watch(() => sortOption.value, animateGrid)
// за цветом
watch(() => store.filterColor, animateGrid)
// за диапазоном цен
watch(() => [store.filterPriceMin, store.filterPriceMax], animateGrid)

// При монтировании грузим товары
onMounted(() => {
  animateGrid()
  loadCategory(store.selectedCategory)
})
</script>

<style scoped lang="scss">

/* === Visibility Helpers === */
.desktop-only {
  display: block !important;
}
.mobile-only  {
  display: none  !important;
}

.catalog {
  padding: 2vw 4vw;
  background: #DEDEDE;
}

/* === HEADER === */
.catalog-header {
  display: grid;
  grid-template-columns: 1fr auto auto;
  grid-template-rows: auto auto;
  gap: 16px;
  align-items: center;
  margin-bottom: 32px;

  .header-text {
    grid-column: 1;
    grid-row: 1 / span 2;
    font-size: 16px;
    line-height: 1.4;
    color: #333;
  }

  .header-logo {
    grid-column: 2;
    grid-row: 1;
    justify-self: center;
    .logo-title {
      font-size: 48px;
      font-weight: 700;
    }
    .logo-year  {
      font-size: 18px;
      color: #FF3B30;
      margin-left: 8px;
    }
  }

  .header-sort {
    grid-column: 3;
    grid-row: 2;
    justify-self: start;
    display: flex;
    align-items: center;
    gap: 8px;

    select {
      padding: 6px 10px;
      border: 1px solid #CCC;
      border-radius: 6px;
      background: #FFF;
    }
  }

  .header-cats {
    grid-column: 2;
    grid-row: 2;
    display: flex;
    gap: 32px;
    justify-content: center;

    .cat-btn {
      background: #FFF;
      border-radius: 12px;
      padding: 16px;
      text-align: center;
      transition: box-shadow .2s;

      &.active {
        box-shadow: 0 0 0 2px #FF3B30;
      }

      img {
        width: 64px; height: 64px;
        object-fit: contain;
        margin-bottom: 8px;
      }
      span {
        display: block;
        font-size: 16px;
        color: #000;
      }
    }
  }
}

/* === BODY === */
.catalog-body {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 24px;
}

/* Sidebar фильтров */
.sidebar {
  .filters-panel {
    background: #FFF;
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;

    input, select {
      padding: 8px;
      border: 1px solid #CCC;
      border-radius: 6px;
    }
    .btn-clear {
      background: #DC3545;
      color: #FFF;
      border: none;
      border-radius: 6px;
      padding: 8px;
      cursor: pointer;
    }
  }
}

/* Main content */
.main-content {
  .mobile-controls {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;

    button {
      width: 100%;
      padding: 10px;
      background: #FFF;
      border: 1px solid #CCC;
      border-radius: 6px;
      text-align: left;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;

      .arrow {
        border: solid #333;
        border-width: 0 2px 2px 0;
        display: inline-block;
        padding: 4px;
        &.down  {
          transform: rotate(45deg);
        }
        &.up    {
          transform: rotate(-135deg);
        }
      }
    }

    /* Новый блок «мобильной сортировки» (отдельный от кнопок) */
    .mobile-sort {
      display: flex;
      align-items: center;
      gap: 8px;

      span {
        font-size: 14px;
      }
      select {
        flex: 1;
        padding: 8px;
        border: 1px solid #CCC;
        border-radius: 6px;
        background: #FFF;
      }
    }

    .mobile-filters {
      background: #FFF;
      border: 1px solid #CCC;
      border-radius: 6px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;

      input, select {
        padding: 8px;
        border: 1px solid #CCC;
        border-radius: 6px;
      }
      .btn-clear {
        background: #DC3545;
        color: #FFF;
        border: none;
        border-radius: 6px;
        padding: 8px;
      }
    }
  }

  /* Сетка товаров */
  .products-grid {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 24px;
    &.blurred {
      filter: blur(4px);
    }
  }
  .product-card {
    background: #FFF;
    border-radius: 12px;
    padding: 16px;
    position: relative;
    text-align: center;

    .product-img {
      width: 100%;
      border-radius: 8px;
    }
    .info {
      margin-top: 12px;
      .brand {
        font-size: 12px;
        color: #777;
      }
      .name  {
        font-size: 14px;
        color: #333;
        margin: 4px 0;
      }
      .price {
        font-size: 16px;
        font-weight: 700;
        color: #000;
      }
    }
    .fav {
      position: absolute;
      top: 12px; right: 12px;
      background: none;
      border: none;
      font-size: 18px;
      cursor: pointer;
      &.active { color: #FF3B30; }
    }
  }
}

/* Плавное развёртывание */
.slide-enter-active, .slide-leave-active {
  transition: all .3s ease;
}
.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}
.slide-enter-to, .slide-leave-from {
  max-height: 500px;
  opacity: 1;
}

/* === MEDIA (<600px) === */
@media (max-width: 600px) {
  .desktop-only {
    display: none  !important;
  }
  .mobile-only  {
    display: flex  !important;
  }

  .catalog-body {
    grid-template-columns: 1fr;
  }

  .catalog-header {
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto auto;
    text-align: center;
    .header-text   {
      grid-row: 2;
    }
    .header-logo   {
      grid-row: 1;
    }
    .header-cats   {
      grid-row: 3;
      justify-content: space-around;
      gap: 16px;
    }
    .header-sort   {
      display: none;
    }
  }

  .main-content .products-grid {
    grid-template-columns: repeat(2,1fr);
    gap: 12px;
  }
}
</style>
