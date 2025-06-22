<template>
  <div class="catalog">
    <!-- Верхнее меню с категориями -->
    <div class="sticky-nav">
      <div class="categories">
        <button v-for="cat in store.categoryList" :key="cat" :class="{ active: cat === store.selectedCategory }" @click="onCategoryClick(cat)">
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- Заголовок текущей категории -->
    <h2>{{ store.selectedCategory }}</h2>

    <!-- Блок управления сортировкой -->
    <div class="sorting-controls">
      <span>Сортировать:</span>
      <select v-model="sortOption">
        <option value="date_desc">Дата добавления: по убыванию</option>
        <option value="date_asc">Дата добавления: по возрастанию</option>
        <option value="price_asc">Цена: по возрастанию</option>
        <option value="price_desc">Цена: по убыванию</option>
      </select>
    </div>

    <!-- Блок фильтров -->
    <div class="filter-controls">
      <span>Фильтры:</span>

      <!-- Цена: Мин. -->
      <input type="number" v-model.number="store.filterPriceMin" placeholder="Мин. цена" class="filter-input"/>
      <!-- Цена: Макс. -->
      <input type="number" v-model.number="store.filterPriceMax" placeholder="Макс. цена" class="filter-input"/>

      <!-- Цвет -->
      <select v-model="store.filterColor" class="filter-select">
        <option value="">Все цвета</option>
        <option v-for="color in distinctColors" :key="color" :value="color">
          {{ color }}
        </option>
      </select>

      <!-- Кнопка сброса фильтров -->
      <button @click="store.clearFilters" class="clear-filters-button">
        Сбросить фильтры
      </button>
    </div>

    <!-- Сетка товаров -->
    <div class="products-grid">
      <div v-for="group in store.displayedProducts" :key="group.color_sku" class="product-card">
        <div @click="goToProductDetail(group)" class="clickable-area">
          <img :src="group.minPriceVariant.image" alt="product" class="product-image"/>
          <div class="product-info">
            <p class="product-brand">{{ group.minPriceVariant.brand }}</p>
            <p class="product-name">{{ group.minPriceVariant.name }}</p>
            <p class="product-price">от {{ group.minPrice }} ₽</p>
          </div>
        </div>

        <button class="favorite-button" v-if="!store.isFavorite(group.color_sku)" @click.stop="store.addToFavorites(group.color_sku)">
          В избранное
        </button>
        <button class="favorite-button remove" v-else @click.stop="store.removeFromFavorites(group.color_sku)">
          Убрать из избранного
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch, computed } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

// При монтировании грузим товары
onMounted(store.fetchProducts)
watch(() => store.selectedCategory, () => store.fetchProducts())

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
</script>

<style scoped lang="scss">

.catalog {
  margin-top: 5vh;
  padding: 2vw;
}

.sticky-nav {
  position: relative;
  padding: 2vh 2vw;
  width: calc(100% - 4vw);
}

.categories {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.categories button {
  padding: 10px;
  border-radius: 8px;
  background: #252a3b;
  color: white;
  transition: 0.3s ease;
}

.categories button.active {
  background: #007bff;
  color: #ffffff;
}

h2 {
  text-align: center;
}

/* Блок сортировки */
.sorting-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.sorting-controls select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: #ffffff;
  cursor: pointer;
}

/* Блок фильтров */
.filter-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-input {
  width: 100px;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.filter-select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: #ffffff;
  cursor: pointer;
}

.clear-filters-button {
  padding: 6px 12px;
  background: #dc3545;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.3s ease;
}

/* Сетка товаров */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(135px, 1fr));
  gap: 16px;
}

.product-card {
  background: $background-color;
  border-radius: 15px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  cursor: pointer;
  position: relative;
}

.clickable-area {
  cursor: pointer;
}

.product-image {
  width: 100%;
  border-radius: 10px;
}

.product-info {
  margin-top: 8px;
}

.product-price {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.product-name {
  font-size: 14px;
  color: #555;
  margin-top: 4px;
}

.product-brand {
  font-size: 12px;
  color: #777;
  margin-top: 2px;
}

.favorite-button {
  margin-top: 8px;
  width: 100%;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: #ffc107;
  color: #000;
  cursor: pointer;
  transition: background 0.3s;
}

.favorite-button.remove {
  background: #dc3545;
  color: #fff;
}

/* Брейкпоинт 360px (уже есть) */
@media (max-width: 360px) {
  .products-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .product-card { width: 100%; }
}

/* Новый брейкпоинт для мобильных до 600px */
@media (max-width: 600px) {
  /* 1. Две колонки товаров */
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  /* 2. Sticky-nav & категории */
  .sticky-nav {
    top: 2vh;
    padding: 1vh 2vw;
  }
  .categories {
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-start;
  }
  .categories button {
    flex: 1 1 calc(50% - 8px);
    padding: 8px;
    text-align: center;
  }

  /* 3. Сортировка по колонке */
  .sorting-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .sorting-controls span {
    order: -1;
  }
  .sorting-controls select {
    width: 100%;
  }

  /* 4. Фильтры */
  .filter-controls {
    gap: 8px;
  }
  .filter-input,
  .filter-select {
    flex: 1 1 calc(50% - 4px);
    min-width: 80px;
  }
  .clear-filters-button {
    flex: 1 1 100%;
  }
}

</style>
