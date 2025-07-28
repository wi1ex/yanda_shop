<template>
  <div class="catalog">
    <div class="line-vert"></div>
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
      <nav class="header-cats" :class="{ blurred: productsLoading }">
        <!-- 1) Корневые категории -->
        <div v-if="!store.showSubcats" class="header-cats-template">
          <div class="header-cats-div">
            <button type="button" class="cat-btn" v-for="cat in store.categoryList"
                    :class="{ active: store.selectedCategory === cat }" :key="cat" @click="onCategoryClick(cat)">
              <img :src="categoryImages[cat]" :alt="cat"/>
              <span>{{ cat }}</span>
            </button>
          </div>
        </div>

        <!-- 2) Подкатегории -->
        <div v-else class="header-cats-template">
          <div class="subcat-slider-wrapper">
            <div class="subcat-slider-row">
              <div class="subcat-slider" ref="subcatSlider" @scroll.passive="onScroll">
                <button type="button" class="back-btn" @click="store.backToCats()">назад</button>
                <button type="button" class="cat-btn" v-for="sub in store.subcatListMap[store.selectedCategory]" :key="sub"
                        :class="{ active: store.selectedSubcat === sub }" @click="store.pickSubcat(sub)">
                  <img v-if="subcategoryImages[sub]" :src="subcategoryImages[sub]" :alt="sub"/>
                  <span>{{ sub }}</span>
                </button>
              </div>
            </div>
            <div class="subcat-slider-div">
              <button type="button" class="nav-btn prev" @click="scrollSubcats(-1)" :disabled="!canPrev">
                <img :src="canPrev ? icon_arrow_mini_red : icon_arrow_mini_black" alt=""/>
              </button>
              <button type="button" class="nav-btn next" @click="scrollSubcats(1)" :disabled="!canNext">
                <img :src="canNext ? icon_arrow_mini_red : icon_arrow_mini_black" alt="" style="transform: rotate(180deg)"/>
              </button>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <div class="catalog-body" :class="{ blurred: productsLoading }">
      <!-- Мобильные контролы -->
      <div class="mobile-controls">
        <div class="mobile-filter">
          <button type="button" ref="filterBtn" class="filter-btn" @click="filtersOpen = !filtersOpen"
                  :style="{ borderRadius: filtersOpen ? '4px 4px 0 0' : '4px' }">
            Фильтры
            <img :src="filtersOpen ? icon_close : icon_filter" alt=""/>
          </button>
          <transition name="slide-down">
            <ul v-if="filtersOpen" ref="filterList" class="filter-list">
              <!-- Активные фильтры -->
              <li v-if="activeFilters.length" class="applied-filters">
                <span v-for="f in activeFilters" :key="f.key" class="applied-filters-item" @click.stop="clearFilterItem(f)">
                  {{ f.label }}
                  <img :src="icon_close" alt="×"/>
                </span>
              </li>

              <!-- Секция «Для кого» -->
              <li class="filter-item">
                <button type="button" class="filter-header" @click="openSection('gender')">
                  Для кого
                  <img :src="icon_arrow_up" alt="" :style="{ transform: openSections.gender ? 'none' : 'rotate(180deg)'}"/>
                </button>
                <transition name="slide-down">
                  <div v-if="openSections.gender" class="gender-buttons">
                    <button type="button" class="gender-btn" :class="{ active: store.filterGender === '' }"
                            @click="store.filterGender = ''">Все</button>
                    <button type="button" class="gender-btn" :class="{ active: store.filterGender === 'F' }"
                            @click="store.filterGender = 'F'">Для неё</button>
                    <button type="button" class="gender-btn" :class="{ active: store.filterGender === 'M' }"
                            @click="store.filterGender = 'M'">Для него</button>
                  </div>
                </transition>
              </li>

              <!-- Секция «Бренды» -->
              <li class="filter-item">
                <button class="filter-header" @click="openSection('brand')">
                  Бренды
                  <img :src="icon_arrow_up" alt="" :style="{ transform: openSections.brand ? 'none' : 'rotate(180deg)'}"/>
                </button>
                <transition name="slide-down">
                  <div v-if="openSections.brand" class="filter-body">
                    <div class="options-list">
                      <label v-for="b in store.distinctBrands" :key="b" class="option">
                        <input type="checkbox" :value="b" v-model="store.filterBrands"/>
                        <span>{{ b }}</span>
                      </label>
                    </div>
                  </div>
                </transition>
              </li>

              <!-- Секция «Размер» -->
              <li class="filter-item">
                <button class="filter-header" @click="openSection('size')">
                  Размер
                  <img :src="icon_arrow_up" alt="" :style="{ transform: openSections.size ? 'none' : 'rotate(180deg)' }"/>
                </button>
                <transition name="slide-down">
                  <div v-if="openSections.size" class="filter-body">
                    <div class="options-list">
                      <label v-for="s in store.distinctSizes" :key="s" class="option">
                        <input type="checkbox" :value="s" v-model="store.filterSizes"/>
                        <span>{{ s }}</span>
                      </label>
                    </div>
                  </div>
                </transition>
              </li>

              <!-- Секция «Цвет» -->
              <li class="filter-item">
                <button class="filter-header" @click="openSection('color')">
                  Цвет
                  <img :src="icon_arrow_up" alt="" :style="{ transform: openSections.color ? 'none' : 'rotate(180deg)'}"/>
                </button>
                <transition name="slide-down">
                  <div v-if="openSections.color" class="filter-body">
                    <div class="options-list">
                      <label v-for="c in store.distinctColors" :key="c" class="option">
                        <input type="checkbox" :value="c" v-model="store.filterColors"/>
                        <span>{{ c }}</span>
                      </label>
                    </div>
                  </div>
                </transition>
              </li>

              <!-- Секция «Цена» -->
              <li class="filter-item">
                <button type="button" class="filter-header" @click="openSection('price')">
                  Цена
                  <img :src="icon_arrow_up" alt="" :style="{ transform: openSections.price ? 'none' : 'rotate(180deg)'}"/>
                </button>
                <transition name="slide-down">
                  <div v-if="openSections.price" class="filter-body">
                    <input type="number" v-model.number="store.filterPriceMin" :placeholder="`от ${formatPrice(priceBounds[0])} ₽`" />
                    <input type="number" v-model.number="store.filterPriceMax" :placeholder="`до ${formatPrice(priceBounds[1])} ₽`" />
                  </div>
                </transition>
              </li>
            </ul>
          </transition>
        </div>
        <div class="mobile-sort">
          <button type="button" ref="sortBtn" class="sort-btn" @click="sortOpen = !sortOpen"
                  :style="{ borderRadius: sortOpen ? '4px 4px 0 0' : '4px' }">
            <span>Сортировка: {{ currentLabel }}</span>
            <img :src="icon_arrow_red" alt="" :style="{ transform: sortOpen ? 'rotate(90deg)' : 'rotate(-90deg)' }"/>
          </button>
          <transition name="slide-down">
            <ul v-if="sortOpen" ref="sortList" class="sort-list">
              <li v-for="opt in sortOptions" :key="opt.value" @click="selectSort(opt.value)" :class="{ active: sortOption === opt.value }">
                {{ opt.label }}
              </li>
            </ul>
          </transition>
        </div>
      </div>

      <div class="line-hor"></div>

      <!-- Сетка товаров -->
      <div class="products-grid">
        <div v-for="group in paged" :key="group.color_sku" class="product-card" @click="goToProductDetail(group)">
          <button type="button" class="fav" @click.stop="toggleFav(group)">
            <img :src="store.isFavorite(group.color_sku) ? icon_favorites_black : icon_favorites_grey" alt="" />
          </button>
          <div class="product-img">
            <img :src="group.minPriceVariant.image" alt="product" />
          </div>
          <div class="info">
            <p class="brand">{{ group.minPriceVariant.brand }}</p>
            <p class="name">{{ group.minPriceVariant.name }}</p>
            <p class="price">от {{ formatPrice(group.minPrice) }} ₽</p>
          </div>
        </div>
      </div>

      <button type="button" v-if="paged.length < store.displayedProducts.length" @click="loadMore" class="btn-load-more">Ещё</button>
      <div v-else class="btn-load-more-div"></div>
    </div>
  </div>
  <div class="line-hor"></div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from '@/store/index.js'
import icon_close from '@/assets/images/close.svg'
import icon_filter from '@/assets/images/filter.svg'
import icon_arrow_red from '@/assets/images/arrow_red.svg'
import icon_arrow_mini_red from '@/assets/images/arrow_mini_red.svg'
import icon_arrow_mini_black from '@/assets/images/arrow_mini_black.svg'
import category_shoes from '@/assets/images/category_shoes.png'
import category_clothing from '@/assets/images/category_clothing.png'
import category_accessories from '@/assets/images/category_accessories.png'
import icon_favorites_black from "@/assets/images/favorites_black.svg";
import icon_favorites_grey from "@/assets/images/favorites_grey.svg";
import icon_arrow_up from "@/assets/images/arrow_up.svg";
const imagesContext = import.meta.glob(
  '@/assets/images/subcats/*.png',
  { eager: true, as: 'url' }
)

const store = useStore()
const route = useRoute()
const router = useRouter()

const page = ref(1)
const perPage = 24
const filtersOpen = ref(false)
const productsLoading = ref(false)
const subcatSlider = ref(null)
const scrollPos = ref(0)
const sortOpen = ref(false)
const sortOption = ref(store.sortBy + '_' + store.sortOrder)
const sortBtn = ref(null)
const sortList = ref(null)
const filterBtn = ref(null)
const filterList = ref(null)
const allSubcatImages = {}

for (const path in imagesContext) {
  // path = '/src/assets/images/subcats/Common_Subcategory_Shoes_Sneakers.png'
  const file = path.split('/').pop().replace('.png','')
  allSubcatImages[file] = imagesContext[path]
}

const openSections = reactive({
  gender: false,
  brand:  false,
  size:   false,
  color:  false,
  price:  false,
})

const categoryImages = {
  'Одежда': category_clothing,
  'Обувь': category_shoes,
  'Аксессуары': category_accessories,
}

// 1) Добавляем маппинг русских имён категорий → английским ключам в именах файлов
const categoryFileKey = {
  'Одежда':      'Clothing',
  'Обувь':       'Shoes',
  'Аксессуары':  'Accessories',
}

// 2) Маппинг русских имён → ключи файлов
const subcatNameToFileKey = {
  // Одежда
  'Блузы':              'Blouse',
  'Бомберы':            'Bomber',
  'Брюки':              'Trousers',
  'Верхняя Одежда':     'Outerwear',
  'Джемперы':           'Jumper',
  'Джинсы':             'Jeans',
  'Жилетки':            'Vest',
  'Кардиганы':          'Cardigan',
  'Купальники':         'Swimsuit',
  'Лонгсливы':          'Longsleeve',
  'Майки':              'T_shirt',
  'Нижнее Белье':       'Underwear',
  'Пиджаки':            'Blazer',
  'Платья':             'Dress',
  'Поло':               'Polo',
  'Пуховики':           'Down_jacket',
  'Рубашки':            'Shirt',
  'Свитеры':            'Sweater',
  'Свитшоты':           'Sweatshirt',
  'Спортивные Костюмы': 'Sports_suit',
  'Футболки':           'Tee_shirt',
  'Худи':               'Hoodie',
  'Шорты':              'Shorts',
  'Юбки':               'Skirt',
  'Плавательные шорты': 'Swimming_shorts',

  // Обувь
  'Балетки':            'Ballet',
  'Босоножки':          'Slingbacks',
  'Ботильоны':          'Ankle_boots',
  'Казаки':             'Cossacks',
  'Кеды':               'Keds',
  'Кроссовки':          'Sneakers',
  'Мокасины':           'Moccasins',
  'Мюли':               'Mules',
  'Резиновая обувь':    'Rubber_shoes',
  'Сабо':               'Sabo',
  'Сандалии':           'Sandals',
  'Сапоги':             'Boots',
  'Слипоны':            'Slip_ons',
  'Топсайдеры':         'Topsiders',
  'Туфли':              'Shoes',
  'Шлепки':             'Flip_flops',
  'Эспадрильи':         'Espadrilles',

  // Аксессуары
  'Головные Уборы':     'Headwear',
  'Очки':               'Glasses',
  'Ремни':              'Belts',
  'Сумки':              'Bags',
  'Рюкзаки':            'Backpacks',
  'Кошельки':           'Wallets',
  'Платки':             'Handkerchiefs',
  'Украшения':          'Decorations',
  'Часы':               'Watch',
  'Шарфы':              'Scarves',
}

const subcategoryImages = computed(() => {
  // 3.1 префикс по полу
  const genderSuffix = store.filterGender === 'M' ? 'Man' : store.filterGender === 'F' ? 'Woman' : 'Common'

  // 3.2 переводим корневую категорию в английский ключ файлов
  const catEng = categoryFileKey[store.selectedCategory]
  if (!catEng) return {}

  // 3.3 собираем полный префикс
  const prefixGen    = `${genderSuffix}_Subcategory_${catEng}_`
  const prefixCommon = `Common_Subcategory_${catEng}_`

  const result = {}
  // 3.4 проходим по всем названиям подкатегорий, которые есть в сторе
  const allNames = Array.from(new Set(Object.values(store.subcatListMap).flat()))
  allNames.forEach(name => {
    const fileKey = subcatNameToFileKey[name]
    if (!fileKey) return
    // сначала пробуем гендерный вариант, потом общий
    const genKey = prefixGen + fileKey
    const comKey = prefixCommon + fileKey
    if (allSubcatImages[genKey]) {
      result[name] = allSubcatImages[genKey]
    } else if (allSubcatImages[comKey]) {
      result[name] = allSubcatImages[comKey]
    }
  })

  return result
})

// Список опций
const sortOptions = [
  { value: 'price_asc',  label: 'Цена по возрастанию' },
  { value: 'price_desc', label: 'Цена по убыванию'    },
  { value: 'sales_desc', label: 'Популярное'          },
  { value: 'date_desc',  label: 'Новинки'             },
]

const currentLabel = computed(() => {
  const opt = sortOptions.find(o => o.value === sortOption.value)
  return opt ? opt.label : ''
})

const canPrev = computed(() =>
  scrollPos.value > 0
)

const canNext = computed(() => {
  const el = subcatSlider.value
  if (!el) return false
  return scrollPos.value + el.clientWidth + 1 < el.scrollWidth
})

// собираем все цены из отображаемых (отфильтрованных) групп
const allPrices = computed(() => {
  return store.displayedProducts
    .flatMap(group => group.variants.map(v => v.price))
    .filter(p => typeof p === 'number')
})

// границы диапазона
const priceBounds = computed(() => {
  if (!allPrices.value.length) {
    return [0, 0]
  }
  return [
    Math.min(...allPrices.value),
    Math.max(...allPrices.value)
  ]
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
function onScroll() {
  const el = subcatSlider.value
  if (!el) return
  scrollPos.value = el.scrollLeft
}

// при выборе — обновляем стор и закрываем
function selectSort(val) {
  const [by, order] = val.split('_')
  store.sortBy      = by
  store.sortOrder   = order
  sortOption.value  = val
  sortOpen.value    = false
  page.value        = 1
  animateGrid()
}

// 1) Количество отфильтрованных товаров
const totalItems = computed(() => store.displayedProducts.length)

// 2) Динамический заголовок
const headerTitle = computed(() => {
  if (store.filterGender === 'M') return 'Для него'
  if (store.filterGender === 'F') return 'Для неё'
  if (store.filterBrands.length === 1) return store.filterBrands[0]
  return 'Каталог'
})

// товары для отображения: первые page*perPage элементов
const paged = computed(() =>
  store.displayedProducts.slice(0, page.value * perPage)
)

// увеличить страницу (если есть ещё)
function loadMore() {
  if (page.value * perPage < store.displayedProducts.length) {
    page.value++
  }
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

function openSection(key) {
  Object.keys(openSections).forEach(k => {
    if (k === key) {
      openSections[key] = !openSections[key]
    } else {
      openSections[k] = false
    }
  })
}

// Сохранение в избранное оставляем, но вешаем .stop на клик, чтобы не перегружать маршрут
function toggleFav(p) {
  store.isFavorite(p.color_sku) ? store.removeFromFavorites(p.color_sku) : store.addToFavorites(p.color_sku)
}

function formatPrice(val) {
  return String(val).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

async function loadCategory(cat) {
  productsLoading.value = true
  await store.fetchProducts(cat)
  productsLoading.value = false
}

function onClickOutside(e) {
  // если дропдаун открыт, и клик был вне кнопки и не внутри списка
  if (
    sortOpen.value &&
    !sortBtn.value.contains(e.target) &&
    !sortList.value?.contains(e.target)
  ) {
    sortOpen.value = false
  }
  if (
    filtersOpen.value &&
    !filterBtn.value.contains(e.target) &&
    !filterList.value?.contains(e.target)
  ) {
    filtersOpen.value = false
  }
}

const activeFilters = computed(() => {
  const arr = []
  // пол
  if (store.filterGender) {
    arr.push({ key: 'gender', type: 'gender', label: store.filterGender === 'M' ? 'Для него' : 'Для неё' })
  }
  // бренды
  store.filterBrands.forEach(b => {
    arr.push({ key: `brand:${b}`, type: 'brand', label: b })
  })
  // цвета
  store.filterColors.forEach(c => {
    arr.push({ key: `color:${c}`, type: 'color', label: c })
  })
  // размеры
  store.filterSizes.forEach(s => {
    arr.push({ key: `size:${s}`, type: 'size',  label: s })
  })
  // цена от
  if (store.filterPriceMin != null) {
    arr.push({ key: 'priceMin', type: 'priceMin', label: `от ${formatPrice(store.filterPriceMin)} ₽` })
  }
  // цена до
  if (store.filterPriceMax != null) {
    arr.push({ key: 'priceMax', type: 'priceMax', label: `до ${formatPrice(store.filterPriceMax)} ₽` })
  }
  return arr
})

function clearFilterItem(f) {
  switch (f.type) {
    case 'gender':
      store.filterGender = ''
      break
    case 'brand':
      store.filterBrands = store.filterBrands.filter(x => x !== f.label)
      break
    case 'color':
      store.filterColors = store.filterColors.filter(x => x !== f.label)
      break
    case 'size':
      store.filterSizes = store.filterSizes.filter(x => x !== f.label)
      break
    case 'priceMin':
      store.filterPriceMin = null
      break
    case 'priceMax':
      store.filterPriceMax = null
      break
  }
}

watch(() => store.selectedCategory, (cat) => { page.value = 1; loadCategory(cat)})
watch(
  () => [store.sortBy, store.sortOrder],
  () => { sortOption.value = `${store.sortBy}_${store.sortOrder}` }
)
watch(
  () => [
    store.filterGender,
    store.filterPriceMin,
    store.filterPriceMax,
    store.filterColors.join(','),
    store.filterBrands.join(','),
    store.filterSizes.join(','),
  ],
  () => {
    page.value = 1
    animateGrid()
  }
)

// При монтировании грузим товары
onMounted(() => {
  document.addEventListener('click', onClickOutside)

  if (route.query.sort) {
    const [by, order] = String(route.query.sort).split('_')
    store.sortBy = by
    store.sortOrder = order
  }

  if (route.query.gender) {
    const g = route.query.gender
    store.filterGender = (g === 'M' || g === 'F') ? g : ''
  }

  if (route.query.brand) {
    store.filterBrands = String(route.query.brand).split(',')
  } else {
    store.filterBrands = []
  }

  if (route.query.color) {
    store.filterColors = String(route.query.color).split(',')
  } else {
    store.filterColors = []
  }

  if (route.query.size) {
    store.filterSizes = String(route.query.size).split(',')
  } else {
    store.filterSizes = []
  }

  if (subcatSlider.value) {
    subcatSlider.value.scrollLeft = 0
    scrollPos.value = 0
    onScroll()
  }

  animateGrid()
  loadCategory(store.selectedCategory)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside)
})

</script>

<style scoped lang="scss">

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
.catalog {
  margin-top: 120px;
  /* === HEADER (мобильный) === */
  .catalog-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 20;
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
        text-transform: uppercase;
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
      transition: all 0.25s cubic-bezier(0, 0.5, 0.25, 1);
      &.blurred {
        filter: blur(4px);
      }
      .header-cats-template {
        display: flex;
        flex-direction: column;
        width: 100%;
        .header-cats-div {
          display: flex;
          justify-content: center;
          gap: 8px;
          .cat-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 8px;
            width: 113px;
            height: 113px;
            border-radius: 4px;
            border: none;
            background-color: $grey-95;
            cursor: pointer;
            transition: all 0.25s ease-in-out;
            img {
              width: 60px;
              height: 60px;
              object-fit: cover;
              transition: all 0.25s ease-in-out;
            }
            span {
              color: $grey-20;
              font-family: Bounded;
              font-size: 14px;
              font-weight: 350;
              line-height: 80%;
              letter-spacing: -0.84px;
              transition: all 0.25s ease-in-out;
            }
            &.active {
              background-color: $white-100;
              img {
                width: 65px;
                height: 65px;
              }
              span {
                color: $black-100;
              }
            }
          }
        }
        .subcat-slider-wrapper {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 0 10px;
          gap: 16px;
          .subcat-slider-row {
            display: flex;
            width: 100%;
            align-items: center;
            .subcat-slider {
              display: flex;
              width: 100%;
              gap: 8px;
              overflow-x: auto;
              scroll-behavior: smooth;
              scroll-snap-type: x mandatory;
              -webkit-overflow-scrolling: touch;
              &::-webkit-scrollbar {
                display: none;
              }
              .back-btn,
              .cat-btn {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 8px;
                min-width: 113px;
                min-height: 113px;
                width: 113px;
                height: 113px;
                border-radius: 4px;
                border: none;
                cursor: pointer;
                scroll-snap-align: start;
              }
              .back-btn {
                justify-content: center;
                background-color: $grey-20;
                color: $white-100;
                font-size: 16px;
                line-height: 100%;
                letter-spacing: -0.64px;
              }
              .cat-btn {
                justify-content: space-between;
                background-color: $grey-95;
                transition: all 0.25s ease-in-out;
                img {
                  width: 60px;
                  height: 60px;
                  object-fit: cover;
                  transition: all 0.25s ease-in-out;
                }
                span {
                  color: $grey-20;
                  font-family: Bounded;
                  font-size: 14px;
                  font-weight: 350;
                  line-height: 80%;
                  letter-spacing: -0.84px;
                  transition: all 0.25s ease-in-out;
                }
                &.active {
                  background-color: $white-100;
                  img {
                    width: 65px;
                    height: 65px;
                  }
                  span {
                    color: $black-100;
                  }
                }
              }
            }
          }
          .subcat-slider-div {
            display: flex;
            align-items: center;
            gap: 10px;
            .nav-btn {
              display: flex;
              align-items: center;
              justify-content: center;
              padding: 8px 12px;
              width: 40px;
              height: 30px;
              border-radius: 64px;
              border: none;
              background-color: $white-80;
              cursor: pointer;
              transition: all 0.25s ease-in-out;
              img {
                width: 16px;
                height: 16px;
                object-fit: cover;
                transition: all 0.25s ease-in-out;
              }
              &.prev[disabled],
              &.next[disabled] {
                cursor: default;
                pointer-events: none;
                img {
                  opacity: 0.4;
                }
              }
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
    transition: all 0.25s cubic-bezier(0, 0.5, 0.25, 1);
    &.blurred {
      filter: blur(4px);
    }
    .mobile-controls {
      display: flex;
      padding: 0 10px 10px;
      gap: 10px;
      .mobile-filter {
        display: flex;
        position: relative;
        min-width: calc(50% - 5px);
        .filter-btn {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 8px;
          width: 100%;
          border: none;
          background-color: $grey-95;
          color: $grey-20;
          font-family: Bounded;
          font-size: 14px;
          font-weight: 350;
          line-height: 120%;
          letter-spacing: -0.7px;
          cursor: pointer;
          img {
            width: 16px;
            height: 16px;
            object-fit: cover;
            transition: all 0.25s ease-in-out;
          }
        }
        .filter-list {
          display: flex;
          flex-direction: column;
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          margin: 0;
          padding: 0;
          border-radius: 0 0 4px 4px;
          background-color: $white-100;
          list-style: none;
          z-index: 200;
          .applied-filters {
            display: flex;
            padding: 4px 8px 12px;
            gap: 8px;
            background-color: $grey-95;
            flex-wrap: wrap;
            .applied-filters-item {
              display: inline-flex;
              align-items: center;
              padding: 8px;
              border-radius: 4px;
              background-color: $white-40;
              color: $black-100;
              font-size: 15px;
              line-height: 100%;
              letter-spacing: -0.6px;
              cursor: pointer;
              img {
                width: 16px;
                height: 16px;
                object-fit: cover;
              }
            }
          }
          .filter-item {
            display: flex;
            flex-direction: column;
            border-top: 1px solid $white-100;
            .filter-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              width: 100%;
              padding: 12px 10px;
              border: none;
              background-color: $grey-95;
              font-size: 15px;
              line-height: 110%;
              letter-spacing: -0.6px;
              cursor: pointer;
              img {
                width: 20px;
                height: 20px;
                object-fit: cover;
                transition: all 0.25s ease-in-out;
              }
            }
            .gender-buttons {
              display: flex;
              padding: 12px 10px;
              gap: 8px;
              background-color: $grey-95;
              flex-wrap: wrap;
              .gender-btn {
                padding: 8px 12px;
                border-radius: 4px;
                border: none;
                background-color: $white-40;
                color: $black-100;
                font-size: 15px;
                line-height: 100%;
                letter-spacing: -0.6px;
                cursor: pointer;
                &.active {
                  background-color: $black-100;
                  color: $white-100;
                }
              }
            }
            .filter-body {
              display: flex;
              flex-direction: column;
              padding: 12px 10px;
              background-color: $grey-95;
              .options-list {
                display: flex;
                flex-direction: column;
                padding: 0 12px;
                max-height: 153px;
                gap: 8px;
                overflow-y: auto;
                overflow-x: hidden;
                .option {
                  display: flex;
                  align-items: center;
                  position: relative;
                  gap: 8px;
                  cursor: pointer;
                  input[type="checkbox"] {
                    -webkit-appearance: none;
                    appearance: none;
                    width: 16px;
                    height: 16px;
                    border: 2px solid $grey-20;
                    border-radius: 2px;
                    cursor: pointer;
                    vertical-align: middle;
                    background-color: transparent;
                  }
                  input[type="checkbox"]:checked {
                    border-color: $black-100;
                  }
                  input[type="checkbox"]:checked::after {
                    content: "";
                    position: absolute;
                    top: 2px;
                    left: 4px;
                    width: 5px;
                    height: 9px;
                    border: solid $black-100;
                    border-width: 0 2px 2px 0;
                    transform: rotate(45deg);
                  }
                  span {
                    color: $grey-20;
                    font-size: 15px;
                    line-height: 110%;
                    letter-spacing: -0.6px;
                  }
                }
              }
              .options-list::-webkit-scrollbar {
                width: 2px;
              }
              .options-list::-webkit-scrollbar-track {
                background: transparent;
              }
              .options-list::-webkit-scrollbar-thumb {
                background-color: $grey-20;
                border-radius: 1px;
              }
            }
          }
        }
      }
      .mobile-sort {
        display: flex;
        position: relative;
        min-width: calc(50% - 5px);
        .sort-btn {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 8px;
          width: 100%;
          border: none;
          background-color: $grey-95;
          cursor: pointer;
          span {
            color: $grey-20;
            font-family: Bounded;
            font-size: 14px;
            font-weight: 350;
            line-height: 120%;
            letter-spacing: -0.7px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          img {
            width: 16px;
            height: 16px;
            object-fit: cover;
            transition: all 0.25s ease-in-out;
          }
        }
        .sort-list {
          display: flex;
          flex-direction: column;
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          margin: 0;
          padding: 0;
          border-radius: 0 0 4px 4px;
          background-color: $grey-95;
          list-style: none;
          z-index: 200;
          li {
            padding: 12px 10px;
            border-top: 1px solid $white-100;
            background-color: $grey-95;
            color: $grey-20;
            font-size: 15px;
            line-height: 110%;
            letter-spacing: -0.6px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: pointer;
            &.active {
              color: $black-100;
              background-color: $white-100;
            }
          }
        }
      }
      /* Плавное раскрытие вверх-вниз */
      .slide-down-enter-active,
      .slide-down-leave-active {
        transition: max-height 0.25s ease-in-out, opacity 0.25s ease-in-out;
      }
      .slide-down-enter-from,
      .slide-down-leave-to {
        max-height: 0;
        opacity: 0;
      }
      .slide-down-enter-to,
      .slide-down-leave-from {
        max-height: 500px;
        opacity: 1;
      }
    }
  }
  /* === PRODUCTS GRID (только тут используем grid) === */
  .products-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    margin-top: 10px;
    .product-card {
      display: flex;
      box-sizing: border-box;
      flex-direction: column;
      position: relative;
      min-width: 0;
      background-color: $grey-89;
      cursor: pointer;
      .fav {
        display: flex;
        position: absolute;
        padding: 0;
        top: 10px;
        right: 10px;
        background: none;
        border: none;
        width: 24px;
        height: 24px;
        cursor: pointer;
        img {
          width: 24px;
          height: 24px;
          object-fit: cover;
        }
      }
      .product-img {
        display: flex;
        padding: 40px 24px;
        height: 100%;
        img {
          width: 100%;
          object-fit: cover;
        }
      }
      .info {
        display: flex;
        flex-direction: column;
        padding: 10px 10px 16px;
        background-color: $grey-87;
        .brand {
          margin: 0;
          font-size: 12px;
          line-height: 100%;
          letter-spacing: -0.48px;
          color: $black-60;
        }
        .name {
          margin: 4px 0 12px;
          font-family: Manrope-SemiBold;
          font-size: 15px;
          line-height: 100%;
          letter-spacing: -0.6px;
          color: $black-100;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .price {
          margin: 0;
          font-size: 15px;
          line-height: 80%;
          letter-spacing: -0.6px;
          color: $grey-20;
        }
      }
    }
  }
  /* === LOAD MORE === */
  .btn-load-more {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 16px 0 96px;
    padding: 0 24px;
    width: 100%;
    height: 56px;
    border-radius: 4px;
    border: none;
    background-color: $grey-20;
    color: $grey-95;
    font-size: 16px;
    line-height: 100%;
    letter-spacing: -0.64px;
    cursor: pointer;
    z-index: 20;
  }
  .btn-load-more-div {
    display: flex;
    margin: 0 0 96px;
    width: 100%;
  }
}

/* MOBILE (<600px) */
@media (max-width: 600px) {
  .catalog {
    margin-top: 96px;
  }
}
</style>
