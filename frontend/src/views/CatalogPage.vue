<template>
  <div class="catalog">
    <!-- === Header === -->
    <div class="catalog__header">
      <div class="header__text">
        <h1 class="title">КАТАЛОГ<small>XYZ</small></h1>
        <p>Здесь оригинальные вещи на любой вкус: от классики до уличного кэжуала.</p>
        <p>Только проверенные бренды и актуальные коллекции. Одежда, в которой ты будешь выглядеть современно, уверенно и круто.</p>
      </div>

      <div class="header__categories">
        <button v-for="cat in store.categoryList" :key="cat" @click="onCategoryClick(cat)"
                :class="['category-btn', { active: cat === store.selectedCategory }]">
          <img :src="`/icons/${cat}.svg`" :alt="cat" />
          <span>{{ cat }}</span>
        </button>
      </div>

      <div class="header__sorting desktop-only">
        <span>Сортировка:</span>
        <select v-model="sortOption">
          <option value="date_desc">Новинки</option>
          <option value="price_asc">Цена ↑</option>
          <option value="price_desc">Цена ↓</option>
        </select>
      </div>
    </div>

    <div class="catalog__body">
      <!-- Sidebar фильтров (desktop) -->
      <aside class="sidebar desktop-only">
        <button class="filters-toggle">Фильтры <i class="icon-filter"/></button>
        <div class="filter-controls">
          <input type="number" v-model.number="store.filterPriceMin" placeholder="Мин. цена" />
          <input type="number" v-model.number="store.filterPriceMax" placeholder="Макс. цена" />
          <select v-model="store.filterColor">
            <option value="">Все цвета</option>
            <option v-for="color in distinctColors" :key="color" :value="color">{{ color }}</option>
          </select>
          <button @click="handleClearFilters" class="clear-btn">Сбросить</button>
        </div>
      </aside>

      <!-- Основное содержимое -->
      <section class="main">
        <!-- Мобильная сортировка + фильтры -->
        <div class="mobile-controls mobile-only">
          <button class="filters-toggle">Фильтры <i class="icon-filter"/></button>
          <button class="sort-toggle">Сортировка: {{ sortLabel }}</button>
        </div>

        <!-- Сетка товаров -->
        <div class="products-grid" :class="{ blurred: productsLoading }">
          <article v-for="group in store.displayedProducts" :key="group.color_sku" class="product-card">
            <div class="clickable-area" @click="goToProductDetail(group)">
              <img :src="group.minPriceVariant.image" alt="" />
              <div class="info">
                <p class="brand">{{ group.minPriceVariant.brand }}</p>
                <p class="name">{{ group.minPriceVariant.name }}</p>
                <p class="price">от {{ group.minPrice }} ₽</p>
              </div>
            </div>
            <button class="fav-btn" v-if="!store.isFavorite(group.color_sku)" @click.stop="store.addToFavorites(group.color_sku)">♡</button>
            <button class="fav-btn active" v-else @click.stop="store.removeFromFavorites(group.color_sku)">♥</button>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

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
.catalog {
  padding: 2vw 4vw;
  background: #DEDEDE;

  // === Header ===
  &__header {
    display: grid;
    grid-template-columns: 2fr 3fr 1fr;
    align-items: end;
    gap: 20px;
    margin-bottom: 40px;

    .header__text {
      p {
        margin: 8px 0;
        font-size: 16px;
        line-height: 1.4;
        color: #333;
      }
      .title {
        font-size: 48px;
        font-weight: 700;
        margin: 0;
        small {
          font-size: 18px;
          color: #FF3B30;
          margin-left: 8px;
        }
      }
    }

    .header__categories {
      display: flex;
      justify-content: center;
      gap: 32px;

      .category-btn {
        background: #FFF;
        border-radius: 12px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        transition: box-shadow .2s;

        &.active {
          box-shadow: 0 0 0 2px #FF3B30;
        }

        img {
          width: 64px;
          height: 64px;
          object-fit: contain;
          margin-bottom: 8px;
        }
        span {
          font-size: 16px;
          font-weight: 500;
          color: #000;
        }
      }
    }

    .header__sorting {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 8px;

      select {
        padding: 6px 10px;
        border: 1px solid #CCC;
        border-radius: 6px;
        background: #FFF;
      }
    }
  }

  // === Body ===
  &__body {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 24px;

    .desktop-only { display: block; }
    .mobile-only  { display: none; }
  }

  // Sidebar фильтров
  .sidebar {
    position: sticky;
    top: 100px;
    background: #FFF;
    border-radius: 12px;
    padding: 16px;

    .filters-toggle {
      width: 100%;
      background: none;
      border: 1px solid #CCC;
      border-radius: 6px;
      padding: 8px;
      margin-bottom: 16px;
      text-align: left;
      cursor: pointer;
    }

    .filter-controls {
      display: flex;
      flex-direction: column;
      gap: 12px;

      input, select {
        padding: 8px;
        border: 1px solid #CCC;
        border-radius: 6px;
      }

      .clear-btn {
        background: #DC3545;
        color: #FFF;
        border: none;
        border-radius: 6px;
        padding: 8px;
        cursor: pointer;
      }
    }
  }

  // Основная секция
  .main {
    .mobile-controls {
      display: flex;
      gap: 12px;
      margin-bottom: 16px;

      button {
        flex: 1;
        padding: 8px;
        border: 1px solid #CCC;
        border-radius: 6px;
        background: #FFF;
      }
    }

    .products-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 24px;
      &.blurred { filter: blur(4px); }

      .product-card {
        background: #FFF;
        border-radius: 12px;
        padding: 16px;
        position: relative;
        text-align: center;

        img {
          width: 100%;
          border-radius: 8px;
        }
        .info {
          margin-top: 12px;
          .brand { font-size: 12px; color: #777; }
          .name  { font-size: 14px; color: #333; margin: 4px 0; }
          .price { font-size: 16px; font-weight: 700; color: #000; }
        }

        .fav-btn {
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
  }

  // === Responsive ===
  @media (max-width: 768px) {
    &__body {
      grid-template-columns: 1fr;
      .desktop-only { display: none; }
      .mobile-only  { display: flex; }
    }

    .header__header {
      display: block;
      text-align: center;

      .header__categories {
        justify-content: center;
        margin: 16px 0;
      }
      .header__sorting {
        justify-content: center;
        margin-top: 16px;
      }
    }

    .main .products-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }
  }
}
</style>
