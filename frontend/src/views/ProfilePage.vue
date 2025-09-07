<template>
  <div class="profile-page">
    <div class="line-vert"></div>
    <h1 class="section-title">ЛИЧНЫЙ КАБИНЕТ</h1>

    <button type="button" class="back-button" @click="goBack()">
      <img :src="icon_arrow_grey" alt="arrow back" />
      {{ backLabel }}
    </button>

    <div class="line-hor"></div>

    <div class="profile-menu" v-if="!currentSection">
      <button type="button" @click="select('profile')">Мой профиль</button>
      <button type="button" @click="select('orders')">Заказы</button>
      <button type="button" @click="select('addresses')">Мои адреса</button>
      <button type="button" @click="select('favorites')">Избранное</button>
      <button type="button" @click="onLogout()" v-if="!store.userStore.isTelegramWebApp">Выйти из профиля</button>
    </div>

    <div v-if="currentSection==='profile'" class="content">
      <h2>Мой профиль</h2>
      <p class="description">Твои личные данные важны для покупок,<br>поэтому проверяй их актуальность.</p>
      <div class="card">
        <label class="card-label">Фото профиля</label>
        <div class="photo-row">
          <img :src="store.userStore.user.photo_url || icon_default_avatar_grey" alt="">
          <button type="button" v-if="!store.userStore.user.photo_url" @click="triggerFile">Загрузить</button>
          <button type="button" v-if="store.userStore.user.photo_url" @click="triggerFile">Изменить</button>
          <button type="button" v-if="store.userStore.user.photo_url" class="text" @click="removePhoto">Удалить</button>
          <input type="file" ref="fileInput" class="visually-hidden" @change="onFileChange" />
        </div>
      </div>
      <div class="card">
        <label class="card-label">Личная информация</label>
        <input class="info" v-model="form.last_name" placeholder="Фамилия*" />
        <input class="info" v-model="form.first_name" placeholder="Имя*" />
        <input class="info" v-model="form.middle_name" placeholder="Отчество*" />
      </div>
      <div class="card">
        <label class="card-label">Пол</label>
        <div class="gender">
          <label class="radio-button">
            <input type="radio" value="male" v-model="form.gender" />
            Мужчина
          </label>
          <label class="radio-button">
            <input type="radio" value="female" v-model="form.gender" />
            Женщина
          </label>
        </div>
      </div>
      <div class="card">
        <label class="card-label">Дата рождения</label>
        <input class="info" type="date" ref="dateInput" v-model="form.date_of_birth" @click="openCalendar" :max="maxDate" />
      </div>
      <div class="card">
        <label class="card-label">Контакты</label>
        <input class="info" v-model="form.phone" placeholder="Телефон*" @input="onPhoneInput" />
        <input class="info" v-model="form.email" placeholder="Почта*" type="email"/>
      </div>
      <button type="button" v-if="formDirty" class="action-button" @click="saveProfile">Сохранить</button>
    </div>

    <div v-if="currentSection==='orders'" class="content">
      <h2 v-if="!store.userStore.orderDetail" :style="{ marginBottom: (store.userStore.orders.length || store.userStore.orderDetail) ? '40px' : '' }">
        Мои заказы
        <span class="title-count" v-if="store.userStore.orders.length">{{ store.userStore.orders.length }}</span>
      </h2>
      <p class="description" v-if="!store.userStore.orders.length && !store.userStore.orderDetail">У тебя нет оформленных заказов.</p>
      <button type="button" v-if="!store.userStore.orders.length" class="action-button" @click="goCatalog">Перейти в каталог</button>

      <!-- Секция сортировки -->
      <div class="mobile-sort" v-if="store.userStore.orders.length && !store.userStore.orderDetail">
        <button type="button" ref="sortBtn" class="sort-btn" @click="sortOpen = !sortOpen" :style="{ borderRadius: sortOpen ? '4px 4px 0 0' : '4px' }">
          <span>Сортировка: {{ currentLabel }}</span>
          <img :src="icon_arrow_red" alt="toggle" :style="{ transform: sortOpen ? 'rotate(90deg)' : 'rotate(-90deg)' }"/>
        </button>
        <transition name="slide-down">
          <ul v-if="sortOpen" ref="sortList" class="sort-list">
            <li v-for="opt in sortOptions" :key="opt.value" @click="selectSort(opt.value)" :class="{ active: sortOption === opt.value }">
              {{ opt.label }}
            </li>
          </ul>
        </transition>
      </div>

      <div v-if="!store.userStore.orderDetail" class="order-cards">
        <div v-for="o in sortedOrders" :key="o.id" class="order-card">
          <div class="status-div">
            <div class="status-block" :class="o.status === 'Отменен' ? 'canceled' : o.status === 'Выполнен' ? 'completed' : ''">
              {{ o.status }}
            </div>
            <p class="order-id">#{{ o.id }}</p>
          </div>
          <div class="preview-div">
            <p class="preview-text">количество товаров / {{ o.items.length }} шт.</p>
            <div class="preview-images">
              <img v-for="it in o.items" :src="it.image_url" :key="it.variant_sku" alt="image"/>
            </div>
          </div>
          <div class="timeline">
            <div class="timeline-div">
              <p class="timeline-date">{{ o.created_at }}</p>
              <p class="timeline-text">Дата заказа</p>
            </div>
            <div class="timeline-vector" v-if="o.status !== 'Выполнен' && o.status !== 'Отменен'" style="margin-top: 5px;">
              <img :src="icon_order_dot" alt="timeline" />
              <img :src="icon_order_line" alt="timeline" />
              <img :src="icon_order_dot" alt="timeline" />
            </div>
            <div class="timeline-vector" v-if="o.status === 'Выполнен'">
              <img :src="icon_order_dot" alt="timeline" />
              <img :src="icon_order_line" alt="timeline" />
              <img :src="icon_order_done" alt="timeline" />
            </div>
            <div class="timeline-div" v-if="o.status !== 'Отменен'">
              <p class="timeline-date" :class="o.status !== 'Выполнен' ? 'processed' : ''">{{ o.finish_date }}</p>
              <p class="timeline-text">{{ o.status === 'Выполнен' ? o.status : 'Получение' }}</p>
            </div>
          </div>
          <div class="total">
            <p class="total-text">
              Итог:
              <span class="total-price">{{ formatPrice(o.total) }} ₽</span>
            </p>
            <button type="button" class="total-button" v-if="o.status !== 'Отменен'" @click="loadOrder(o.id)">
              Перейти
              <img :src="icon_arrow_grey" alt="arrow right" style="transform: rotate(180deg)" />
            </button>
          </div>
        </div>
      </div>

      <div v-else class="order-detail">
        <div class="status-id">
          <h3 class="detail-id">#{{ store.userStore.orderDetail.id }}</h3>
          <div class="detail-status" :class="store.userStore.orderDetail.status === 'Отменен' ? 'canceled' : store.userStore.orderDetail.status === 'Выполнен' ? 'completed' : ''">
            {{ store.userStore.orderDetail.status }}
          </div>
        </div>
        <div class="order-timeline">
          <div v-for="(stage, idx) in store.userStore.orderDetail.timeline" :key="idx" class="order-timeline-div">
            <div class="order-timeline-vector" :class="{ 'incomplete': !stage.done }">
              <img :src="icon_order_dot" alt="timeline" v-if="idx !== store.userStore.orderDetail.timeline.length - 1" />
              <img :src="icon_order_line" alt="timeline" v-if="idx !== store.userStore.orderDetail.timeline.length - 1" />
              <img :src="icon_order_done" alt="timeline" v-if="idx === store.userStore.orderDetail.timeline.length - 1" />
            </div>
            <p class="order-timeline-date" :class="!stage.done ? 'processed' : ''">{{ stage.date }}</p>
            <p class="order-timeline-label">{{ stage.label }}</p>
          </div>
        </div>
        <div class="info-block">
          <p class="info-block-info title">Информация о заказе</p>
          <p class="info-block-info">Оплата:</p>
          <p class="info-block-info value">{{ store.userStore.orderDetail.payment_method }}</p>
          <p class="info-block-info" style="margin-top: -4px;">Способ доставки:</p>
          <p class="info-block-info value">{{ store.userStore.orderDetail.delivery_type }}</p>
          <p class="info-block-info" style="margin-top: -4px;">Адрес доставки:</p>
          <p class="info-block-info value">{{ store.userStore.orderDetail.delivery_address }}</p>
        </div>
        <div class="info-block" style="margin-top: -32px;">
          <p class="info-block-info title">Стоимость</p>
          <div class="info-block-price">
            <div class="info-block-div">
              <p class="info-block-text">Стоимость:</p>
              <p class="info-block-text">{{ formatPrice(store.userStore.orderDetail.subtotal) }} ₽</p>
            </div>
            <div class="info-block-div">
              <p class="info-block-text">Курьерская доставка:</p>
              <p class="info-block-text">{{ formatPrice(store.userStore.orderDetail.delivery_price) }} ₽</p>
            </div>
          </div>
          <div class="info-block-price">
            <div class="info-block-div">
              <p class="info-block-text black">Итог:</p>
              <p class="info-block-text price">{{ formatPrice(store.userStore.orderDetail.total) }} ₽</p>
            </div>
          </div>
        </div>
        <div class="cart-drawer">
          <div class="info-block" style="padding-bottom: 24px;">
            <p class="info-block-info title">Товары [ {{ store.userStore.orderDetail.items.length }} ]</p>
          </div>
          <div class="cart-items-frame">
            <div v-for="item in store.userStore.orderDetail.items" :key="item.variant_sku" class="cart-item">
              <div class="item-image-container">
                <img :src="item.image_url" alt="image" />
              </div>
              <div class="item-details-div">
                <div class="item-details">
                  <p class="item-brand">{{ item.brand }}</p>
                  <p class="item-name-price">{{ item.name }}</p>
                  <p class="item-sku">артикул: {{ item.world_sku }}</p>
                  <p class="item-name-price">{{ formatPrice(item.price) }} ₽</p>
                </div>
                <div class="item-info-row">
                  <div class="item-info-div">
                    <p class="item-info">
                      Количество:
                      <span class="item-info-value">{{ item.qty }}</span>
                    </p>
                    <p class="item-info">
                      Размер:
                      <span class="item-info-value">{{ item.size_label }}</span>
                    </p>
                    <p class="item-info">
                      Доставка:
                      <span class="item-info-value">{{ item.delivery_option || '—' }}</span>
                    </p>
                  </div>
                  <button type="button" class="add-btn" v-if="item.canAddToCart" @click="addItem(item)">
                    <span class="add-text">Добавить в корзину</span>
                    <img :src="icon_cart_add" alt="Добавить" class="add-icon" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
<!--        <button type="button" v-if="store.userStore.orderDetail.canRepeat" class="repeat" @click="repeatOrder(store.userStore.orderDetail.id)">Повторить заказ</button>-->
      </div>
    </div>

    <div v-if="currentSection==='addresses'" class="content">
      <h2 :style="{ marginBottom: (sortedAddresses.length || addressFormVisible) ? '40px' : '' }">
        Мои адреса{{ sortedAddresses.length ? ` [ ${sortedAddresses.length} ]` : '' }}
      </h2>
      <p class="description" v-if="!sortedAddresses.length && !addressFormVisible">У тебя нет сохранённых адресов.</p>
      <div v-if="sortedAddresses.length && !addressFormVisible" class="list_addresses">
        <div v-for="a in sortedAddresses" class="address" :key="a.id">
          <label class="radio-button address-text" @click="selectAddress(a.id)">
            <input type="radio" :value="a.id" v-model="selectedAddress" />
            {{ a.label }}
          </label>
          <button type="button" @click.stop="editAddress(a)">
            <img :src="icon_arrow_mini_black" alt="arrow" style="transform: rotate(180deg)"/>
          </button>
        </div>
      </div>
      <button type="button" v-if="!addressFormVisible" class="action-button" @click="editAddress()">Добавить адрес</button>

      <div v-if="addressFormVisible" class="card">
        <label class="card-label">{{ addressForm.id ? 'Редактировать адрес' : 'Добавить новый адрес' }}</label>
        <input class="info" v-model="addressForm.label" placeholder="Название адреса*" />
        <input class="info" v-model="addressForm.city" placeholder="Город*" />
        <input class="info" v-model="addressForm.street" placeholder="Улица*" />
        <input class="info" v-model="addressForm.house" placeholder="Дом, строение, корпус*" />
        <div class="row">
          <input class="info" v-model="addressForm.apartment" placeholder="Квартира" />
          <input class="info" v-model="addressForm.intercom" placeholder="Домофон" />
        </div>
        <div class="row">
          <input class="info" v-model="addressForm.entrance" placeholder="Подъезд" />
          <input class="info" v-model="addressForm.floor" placeholder="Этаж" />
        </div>
        <input class="info" v-model="addressForm.comment" placeholder="Комментарий курьеру" >
      </div>
      <div v-if="addressFormVisible" class="buttons">
        <button type="button" class="action-button" v-if="(!addressForm.id && canSave) || addressFormDirty" @click="saveAddress">
          {{ addressForm.id ? 'Сохранить изменения' : 'Сохранить' }}
        </button>
        <button type="button" class="default-button" @click="cancelAddress">
          Отменить
        </button>
        <button type="button" v-if="addressForm.id" class="action-button" @click="deleteAddress(addressForm.id)">
          Удалить адрес
        </button>
      </div>
    </div>

    <div v-if="currentSection==='favorites'" class="content">
      <h2 :style="{ marginBottom: (favoriteProductsRaw.length) ? '40px' : '' }">
        Избранное
        <span class="title-count" v-if="favoriteProductsRaw.length">{{ favoriteProductsRaw.length }}</span>
      </h2>
      <p class="description" v-if="!favoriteProductsRaw.length">Ты еще не добавлял товары в избранное.</p>
      <button type="button" v-if="!favoriteProductsRaw.length" class="action-button" @click="goCatalog">Перейти в каталог</button>

      <div class="mobile-sort" v-if="favoriteProductsRaw.length">
        <button type="button" ref="favSortBtn" class="sort-btn" @click="favSortOpen = !favSortOpen"
                :style="{ borderRadius: favSortOpen ? '4px 4px 0 0' : '4px' }">
          <span>Сортировка: {{ favCurrentLabel }}</span>
          <img :src="icon_arrow_red" alt="toggle" :style="{ transform: favSortOpen ? 'rotate(90deg)' : 'rotate(-90deg)' }"/>
        </button>
        <transition name="slide-down">
          <ul v-if="favSortOpen" ref="favSortList" class="sort-list">
            <li v-for="opt in favSortOptions" :key="opt.value" @click="selectFavSort(opt.value)"
                :class="{ active: favSortOption === opt.value }">
              {{ opt.label }}
            </li>
          </ul>
        </transition>
      </div>

      <div class="products-grid" v-if="favoriteProductsRaw.length">
        <div v-for="product in sortedFavorites" :key="product.color_sku" @click="goToProduct(product)" class="product-card">
          <button type="button" class="remove-fav-btn" @click.prevent.stop="store.cartStore.removeFromFavorites(product.color_sku)" aria-label="Удалить из избранного">
            <img :src="icon_favorites_black" alt="product" />
          </button>
          <img class="product-image" :src="product.image" alt="product" />
          <div class="product-info">
            <p class="product-brand">{{ product.brand }}</p>
            <p class="product-name">{{ product.name }}</p>
            <p class="product-price">от {{ formatPrice(product.price) }} ₽</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="line-hor" style="margin-top: 96px;"></div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from '@/store/index.js'
import { useRoute, useRouter } from 'vue-router'

import icon_default_avatar_grey from '@/assets/images/default_avatar_grey.svg'
import icon_arrow_grey from "@/assets/images/arrow_grey.svg";
import icon_arrow_mini_black from "@/assets/images/arrow_mini_black.svg";
import icon_arrow_mini_red from "@/assets/images/arrow_mini_red.svg";
import icon_arrow_red from '@/assets/images/arrow_red.svg'
import icon_order_dot from "@/assets/images/order_dot.svg";
import icon_order_line from "@/assets/images/order_line.svg";
import icon_order_done from "@/assets/images/order_done.svg";
import icon_minus_grey from "@/assets/images/minus_grey.svg";
import icon_plus_grey from "@/assets/images/plus_grey.svg";
import icon_cart_add from "@/assets/images/cart_add.svg";
import icon_favorites_black from "@/assets/images/favorites_black.svg";

const store = useStore()
const route = useRoute()
const router = useRouter()

// UI-state
const currentSection   = ref(null)
const sortBtn          = ref(null)
const sortList         = ref(null)
const sortOpen         = ref(false)
const sortOption       = ref('id_desc')  // по умолчанию: по убыванию
const sortOptions      = [
  { value: 'id_desc', label: 'От нового к старому' },
  { value: 'id_asc',  label: 'От старого к новому' },
  { value: 'status',  label: 'По статусу' },
]
const favSortBtn     = ref(null)
const favSortList    = ref(null)
const favSortOpen    = ref(false)
const favSortOption  = ref('date_desc') // по умолчанию: по дате добавления (новые сверху)
const favSortOptions = [
  { value: 'date_desc', label: 'По дате добавления' },
  { value: 'price_asc', label: 'По возрастанию цены' },
  { value: 'price_desc', label: 'По убыванию цены' },
]

const statusPriority = {
  'Дата заказа':         0,
  'В обработке':         1,
  'Выкуплен':            2,
  'Собран':              3,
  'В пути':              4,
  'Передан в доставку':  5,
  'Выполнен':            6,
  'Отменен':             7,
}

const currentLabel = computed(() => {
  const opt = sortOptions.find(o => o.value === sortOption.value)
  return opt ? opt.label : ''
})

const favCurrentLabel = computed(() => {
  const opt = favSortOptions.find(o => o.value === favSortOption.value)
  return opt ? opt.label : ''
})

// отсортированные заказы
const sortedOrders = computed(() => {
  const arr = [...store.userStore.orders]
  if (sortOption.value === 'status') {
    const prio = (s) => (s in statusPriority ? statusPriority[s] : 999)
    return arr.sort((a, b) => {
      const pa = prio(a.status)
      const pb = prio(b.status)
      if (pa !== pb) return pa - pb
      return b.id - a.id
    })
  }
  if (sortOption.value === 'id_asc') {
    return arr.sort((a, b) => a.id - b.id)
  } else {
    return arr.sort((a, b) => b.id - a.id)
  }
})

// сохраняем порядок из store.cartStore.favorites.items (это порядок добавления)
const favoriteProductsRaw = computed(() =>
  store.cartStore.favorites.items
    .map((cs, idx) => {
      const group = store.productStore.colorGroups.find(g => g.color_sku === cs)
      if (!group) return null
      const v = group.minPriceVariant
      return {
        ...v,
        color_sku: group.color_sku,
        __addedIndex: idx,          // индекс добавления (меньше — раньше добавлен)
      }
    })
    .filter(Boolean)
)

// итоговый список с учётом выбранной сортировки
const sortedFavorites = computed(() => {
  const arr = [...favoriteProductsRaw.value]
  switch (favSortOption.value) {
    case 'price_asc':
      return arr.sort((a, b) => (a.price ?? 0) - (b.price ?? 0))
    case 'price_desc':
      return arr.sort((a, b) => (b.price ?? 0) - (a.price ?? 0))
    case 'date_desc':
    default:
      // новые сверху: предполагаем, что конец original list — самые новые
      return arr.sort((a, b) => b.__addedIndex - a.__addedIndex)
  }
})

function selectSort(val) {
  sortOption.value = val
  sortOpen.value   = false
}

function selectFavSort(val) {
  favSortOption.value = val
  favSortOpen.value   = false
}

function onClickOutside(e) {
  // сортировка заказов
  if (sortOpen.value &&
      !sortBtn.value?.contains(e.target) &&
      !sortList.value?.contains(e.target)) {
    sortOpen.value = false
  }
  // сортировка избранного
  if (favSortOpen.value &&
      !favSortBtn.value?.contains(e.target) &&
      !favSortList.value?.contains(e.target)) {
    favSortOpen.value = false
  }
}

// PROFILE
const form = reactive({
  first_name:    '',
  last_name:     '',
  middle_name:   '',
  gender:        '',
  date_of_birth: '',
  phone:         '',
  email:         '',
})
const fileInput = ref()
const dateInput = ref(null)
const maxDate = new Date().toISOString().split('T')[0]

// ADDRESSES
const selectedAddress     = ref(null)
const addressFormVisible  = ref(false)
const addressForm         = reactive({
  id:        null,
  label:     '',
  city:      '',
  street:    '',
  house:     '',
  apartment: '',
  intercom:  '',
  entrance:  '',
  floor:     '',
  comment:   '',
})
const requiredFilled = v => !!(v && String(v).trim())
const canSave = computed(() =>
  ['label', 'city', 'street', 'house'].every(k => requiredFilled(form[k]))
)

const sortedAddresses = computed(() => {
  const list = store.userStore.addresses.slice()
  const primary = list.filter(a => a.selected)
  const others = list
    .filter(a => !a.selected)
    .sort((a, b) => a.label.localeCompare(b.label))
  return [...primary, ...others]
})

// Смена раздела
const backLabel = computed(() => {
  if (store.userStore.orderDetail) return 'К заказам'
  if (addressFormVisible.value) return 'К адресам'
  if (currentSection.value) return 'Мой кабинет'
  return 'Назад'
})

async function select(sec) {
  currentSection.value = sec
  store.userStore.orderDetail = null
  addressFormVisible.value = false
  if (sec==='orders') {
    await store.userStore.fetchOrders()
  }
}

// LOGOUT
async function onLogout() {
  await store.userStore.logout()
  router.push({ name: 'Home' })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goBack() {
  if (store.userStore.orderDetail !== null) {
    store.userStore.orderDetail = null
  } else if (addressFormVisible.value) {
    addressFormVisible.value = false
  } else if (currentSection.value) {
    currentSection.value = null
  } else {
    if (window.history.length > 1) {
      router.back()
    } else {
      router.push({ name: 'Home' })
    }
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goCatalog() {
  currentSection.value = null
  router.push({ name: 'Catalog' })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToProduct(p) {
  router.push({
    name: 'ProductDetail',
    params: { variant_sku: p.variant_sku },
    query: { category: p.category }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// PROFILE
const formDirty = computed(() => {
  const u = store.userStore.user
  const normPhone = v => String(v || '').replace(/\D/g, '')
  return (
    form.first_name       !== (u.first_name       || '') ||
    form.last_name        !== (u.last_name        || '') ||
    form.middle_name      !== (u.middle_name      || '') ||
    form.gender           !== (u.gender           || '') ||
    form.date_of_birth    !== (u.date_of_birth    || '') ||
    form.email            !== (u.email            || '') ||
    normPhone(form.phone) !== (normPhone(u.phone) || '')
  )
})

function openCalendar() {
  dateInput.value?.showPicker?.()
}

function triggerFile() {
  fileInput.value.click()
}

async function onFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    await store.userStore.uploadAvatar(file)
  }
}

async function removePhoto() {
  await store.userStore.deleteAvatar()
}

async function saveProfile() {
  const fd = new FormData()
  for (const [k, v] of Object.entries(form)) {
    fd.append(k, v ?? '')
  }
  await store.userStore.updateProfile(fd)
}

function formatPhone(raw = '') {
  // оставляем только цифры и обрезаем до 11
  const d = raw.replace(/\D/g, '').slice(0, 11)
  const c1 = d.slice(0, 1)       // «8»
  const c2 = d.slice(1, 4)       // код оператора
  const c3 = d.slice(4, 7)       // первые 3
  const c4 = d.slice(7, 9)       // следующие 2
  const c5 = d.slice(9, 11)      // последние 2
  let out = ''

  if (c1) out += c1
  if (c2.length > 0) out += ' (' + c2
  if (c2.length === 3 && c3.length > 0) out += ')'
  if (c3.length > 0) out += ' ' + c3
  if (c4.length > 0) out += '-' + c4
  if (c5.length > 0) out += '-' + c5
  return out
}

function onPhoneInput(e) {
  const formatted = formatPhone(e.target.value)
  e.target.value = formatted
  form.phone = formatted
}

// ORDERS
async function loadOrder(id) {
  await store.userStore.fetchOrder(id)
  await ensureProductsLoaded();
  markAddableFlags();
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function formatPrice(val) {
  return String(val).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

async function ensureProductsLoaded() {
  if (!store.productStore.products.length) {
    try { await store.productStore.fetchProducts() } catch (e) { /* noop */ }
  }
}

function markAddableFlags() {
  if (!store.userStore.orderDetail) return;
  const items = store.userStore.orderDetail.items || [];
  // Если есть индекс:
  const index = store.productStore.variantBySku || null;
  store.userStore.orderDetail.items = items.map(it => {
    let exists;
    if (index && index.size) {
      exists = index.has(it.variant_sku);
    } else {
      // fallback без индекса
      exists = store.productStore.products.some(p => p.variant_sku === it.variant_sku);
    }
    return { ...it, canAddToCart: exists };
  });
}

async function addItem(item) {
  // Каталог гарантированно загружен, флаг уже стоит
  const variant = store.productStore.variantBySku?.get(item.variant_sku)
               || store.productStore.products.find(p => p.variant_sku === item.variant_sku);

  if (!variant) {
    // Теоретический гон: пока смотрели — каталог обновился.
    alert('Этого товара больше нет в каталоге');
    return;
  }

  const payload = {
    variant_sku:     variant.variant_sku,
    world_sku:       variant.world_sku || null,
    image:           variant.image_url || item.image_url || '',
    brand:           variant.brand || '',
    name:            variant.name  || '',
    size_label:      variant.size_label || '',
    computed_price:  variant.price,
    price:           variant.price,
    delivery_option: item.delivery_option ? { label: item.delivery_option } : null
  };

  store.cartStore.addToCart(payload);
  store.cartStore.openCartDrawer();
}

// function repeatOrder(id) {
//   // например: store.userStore.repeatOrder(id) → router.push('/checkout')
// }

// ADDRESSES
const addressFormDirty = computed(() => {
  if (!addressForm.id) {
    return Boolean(
      addressForm.city      ||
      addressForm.street    ||
      addressForm.house     ||
      addressForm.apartment ||
      addressForm.intercom  ||
      addressForm.entrance  ||
      addressForm.floor     ||
      addressForm.comment
    )
  }
  const orig = store.userStore.addresses.find(a => a.id === addressForm.id)
  if (!orig) return false
  return (
    addressForm.city              !== orig.city              ||
    addressForm.street            !== orig.street            ||
    addressForm.house             !== orig.house             ||
    (addressForm.apartment || '') !== (orig.apartment || '') ||
    (addressForm.intercom  || '') !== (orig.intercom  || '') ||
    (addressForm.entrance  || '') !== (orig.entrance  || '') ||
    (addressForm.floor     || '') !== (orig.floor     || '') ||
    (addressForm.comment   || '') !== (orig.comment   || '')
  )
})

async function selectAddress(id) {
  await store.userStore.setPrimaryAddress(id)
  await store.userStore.fetchAddresses()
  selectedAddress.value = id
}

function editAddress(a = null) {
  if (a) {
    Object.assign(addressForm, a)
  } else {
    Object.assign(addressForm, {
      id:        null,
      label:     '',
      city:      '',
      street:    '',
      house:     '',
      apartment: '',
      intercom:  '',
      entrance:  '',
      floor:     '',
      comment:   ''
    })
  }
  addressFormVisible.value = true
}

function cancelAddress() {
  addressFormVisible.value = false
}

async function saveAddress() {
  if (!addressForm.label || !addressForm.label.trim()) return
  if (addressForm.id)
    await store.userStore.updateAddress(addressForm.id, addressForm)
  else
    await store.userStore.addAddress(addressForm)
  await store.userStore.fetchAddresses()
  addressFormVisible.value = false
}

async function deleteAddress(id) {
  await store.userStore.deleteAddress(id)
  await store.userStore.fetchAddresses()
  addressFormVisible.value = false
}

watch(
  () => store.userStore.user,
  u => {
    if (!u.id) return
    form.first_name    = u.first_name    || ''
    form.last_name     = u.last_name     || ''
    form.middle_name   = u.middle_name   || ''
    form.gender        = u.gender        || ''
    form.date_of_birth = u.date_of_birth || ''
    form.email         = u.email         || ''
    form.phone         = u.phone         || ''
  },
  { immediate: true }
)

watch(() => route.query.section, sec => {
  if (sec) select(sec)
})

onMounted(async () => {
  document.addEventListener('click', onClickOutside)
  await store.userStore.fetchOrders()
  await store.userStore.fetchAddresses()
  selectedAddress.value = sortedAddresses.value.find(a => a.selected)?.id || null
  await store.productStore.fetchProducts()
  await store.cartStore.loadFavoritesFromServer()
  if (route.query.section) {
    currentSection.value = route.query.section
  }
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

.profile-page {
  margin-top: 120px;
  .section-title {
    margin: 96px 0 40px;
    text-align: center;
    color: $black-100;
    font-family: Bounded;
    font-weight: 400;
    font-size: 32px;
    line-height: 90%;
    letter-spacing: -2.24px;
    z-index: 20;
  }
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
  .profile-menu {
    display: flex;
    flex-direction: column;
    position: relative;
    padding: 10px 10px 0;
    z-index: 20;
    button {
      display: flex;
      padding: 16px 8px;
      border: none;
      border-bottom: 1px solid $white-100;
      background-color: $grey-95;
      color: $grey-20;
      font-family: Bounded;
      font-size: 16px;
      font-weight: 350;
      line-height: 80%;
      letter-spacing: -0.8px;
      cursor: pointer;
    }
    button:first-child {
      border-radius: 4px 4px 0 0;
    }
    button:last-child {
      border-radius: 0 0 4px 4px;
      border-bottom: none;
    }
  }
  .content {
    display: flex;
    flex-direction: column;
    h2 {
      display: flex;
      margin: 10px;
      gap: 4px;
      color: $black-100;
      font-family: Bounded;
      font-size: 24px;
      font-weight: 250;
      line-height: 80%;
      letter-spacing: -1.2px;
      z-index: 20;
      .title-count {
        margin: 0;
        color: $red-active;
        font-family: Manrope;
        font-size: 16px;
        font-weight: 500;
        line-height: 110%;
        letter-spacing: -0.64px;
      }
    }
    .description {
      margin: 6px 10px 40px;
      color: $grey-20;
      font-size: 15px;
      line-height: 110%;
      letter-spacing: -0.6px;
      z-index: 20;
    }
    .card {
      display: flex;
      flex-direction: column;
      position: relative;
      margin-bottom: 10px;
      padding: 20px 10px;
      width: calc(100% - 20px);
      border-radius: 4px;
      background-color: $white-100;
      z-index: 20;
      .card-label {
        margin-bottom: 24px;
        color: $grey-20;
        font-size: 16px;
        line-height: 110%;
        letter-spacing: -0.64px;
      }
      .row {
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .photo-row {
        display: flex;
        align-items: center;
        gap: 24px;
        img {
          width: 120px;
          height: 120px;
          object-fit: cover;
          border-radius: 999px;
        }
        button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 24px;
          height: 40px;
          border: none;
          border-radius: 999px;
          background-color: $grey-20;
          color: $white-100;
          font-size: 16px;
          line-height: 100%;
          letter-spacing: -0.64px;
          cursor: pointer;
          &.text {
            margin-left: -8px;
            padding: 0;
            background: none;
            color: $black-100;
          }
        }
        input {
          display: none;
        }
      }
      .info {
        margin-bottom: 15px;
        padding: 21px 10px 8px;
        width: calc(100% - 20px);
        outline: none;
        box-shadow: none;
        border: none;
        border-bottom: 1px solid $grey-20;
        color: $grey-20;
        font-size: 15px;
        line-height: 100%;
        letter-spacing: -0.6px;
        &::placeholder {
          color: $black-40;
        }
      }
      .gender {
        display: flex;
        gap: 24px;
      }
    }
    .list_addresses {
      display: flex;
      flex-direction: column;
      margin-bottom: 40px;
      gap: 10px;
      z-index: 20;
      .address {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 10px;
        border-radius: 4px;
        background-color: $grey-95;
        .address-text {
          font-size: 16px;
          line-height: 110%;
          letter-spacing: -0.64px;
        }
        button {
          padding: 0;
          border: none;
          background: none;
          cursor: pointer;
          img {
            width: 24px;
            height: 24px;
            object-fit: cover;
          }
        }
      }
    }
    .mobile-sort {
      display: flex;
      position: relative;
      margin: 0 10px 40px;
      z-index: 20;
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

    .order-cards {
      display: flex;
      flex-direction: column;
      width: 100%;
      gap: 8px;
      z-index: 15;
      .order-card {
        display: flex;
        flex-direction: column;
        padding: 20px 10px;
        width: calc(100% - 20px);
        gap: 40px;
        border-radius: 4px;
        background-color: $grey-95;
        .status-div {
          display: flex;
          align-items: center;
          justify-content: space-between;
          .status-block {
            display: flex;
            padding: 8px 12px;
            border-radius: 26px;
            background-color: $grey-20;
            color: $white-100;
            font-size: 15px;
            line-height: 100%;
            letter-spacing: -0.6px;
            &.completed {
              background-color: $green-active;
            }
            &.canceled {
              background-color: $black-40;
            }
          }
          .order-id {
            margin: 0;
            color: $black-40;
            font-size: 16px;
            line-height: 110%;
            letter-spacing: -0.64px;
          }
        }
        .preview-div {
          display: flex;
          flex-direction: column;
          gap: 16px;
          .preview-text {
            margin: 0;
            color: $black-100;
            font-size: 15px;
            line-height: 110%;
            letter-spacing: -0.6px;
          }
          .preview-images {
            display: flex;
            gap: 8px;
            img {
              border-radius: 4px;
              background-color: $grey-90;
              min-width: 64px;
              min-height: 64px;
              width: 64px;
              height: 64px;
              object-fit: contain;
            }
          }
        }
        .timeline {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          .timeline-div {
            display: flex;
            flex-direction: column;
            gap: 8px;
            .timeline-date {
              margin: 0;
              color: $black-100;
              font-family: Bounded;
              font-size: 20px;
              font-weight: 300;
              line-height: 90%;
              letter-spacing: -1px;
              &.processed {
                color: $black-40;
              }
            }
            .timeline-text {
              margin: 0;
              width: max-content;
              color: $black-40;
              font-size: 14px;
              line-height: 100%;
              letter-spacing: -0.56px;
            }
          }
          .timeline-vector {
            display: flex;
            align-items: center;
            width: 100%;
            img:nth-child(2) {
              flex: 1;
              width: 100%;
              height: 1px;
              object-fit: cover;
            }
          }
        }
        .total {
          display: flex;
          align-items: center;
          justify-content: space-between;
          .total-text {
            margin: 0;
            color: $grey-20;
            font-size: 15px;
            line-height: 100%;
            letter-spacing: -0.6px;
            .total-price {
              margin: 0 0 0 8px;
              color: $black-100;
              font-family: Bounded;
              font-size: 20px;
              font-weight: 300;
              line-height: 90%;
              letter-spacing: -1px;
            }
          }
          .total-button {
            display: flex;
            align-items: center;
            padding: 0;
            gap: 4px;
            border: none;
            background: none;
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
      }
    }
    .order-detail {
      display: flex;
      flex-direction: column;
      gap: 40px;
      .status-id {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 10px 10px 0;
        .detail-id {
          margin: 0;
          color: $black-100;
          font-family: Bounded;
          font-size: 24px;
          font-weight: 250;
          line-height: 80%;
          letter-spacing: -1.2px;
        }
        .detail-status {
          display: flex;
          padding: 8px 12px;
          border-radius: 26px;
          background-color: $grey-20;
          color: $white-100;
          font-size: 15px;
          line-height: 100%;
          letter-spacing: -0.6px;
          &.completed {
            background-color: $green-active;
          }
          &.canceled {
            background-color: $black-40;
          }
        }
      }
      .order-timeline {
        display: flex;
        align-items: center;
        margin: 0 10px;
        z-index: 20;
        overflow-x: auto;
        overflow-y: hidden;
        scrollbar-width: none;
        -ms-overflow-style: none;
        -webkit-overflow-scrolling: touch;
        scroll-snap-type: x mandatory;
        .order-timeline-div {
          flex: 0 0 auto;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          height: 72px;
          scroll-snap-align: center;
          .order-timeline-vector {
            display: flex;
            align-items: center;
            height: 16px;
            &.incomplete {
              opacity: 0.4;
            }
          }
          .order-timeline-date {
            display: flex;
            margin: 16px 0 0;
            color: $black-100;
            font-family: Bounded;
            font-size: 20px;
            font-weight: 300;
            line-height: 90%;
            letter-spacing: -1px;
            &.processed {
              color: $black-40;
            }
          }
          .order-timeline-label {
            display: flex;
            margin: 0;
            color: $black-40;
            font-size: 14px;
            line-height: 100%;
            letter-spacing: -0.56px;
          }
        }
      }
      .order-timeline::-webkit-scrollbar {
        display: none;
      }
      .info-block {
        display: flex;
        padding: 20px 10px;
        flex-direction: column;
        gap: 24px;
        border-radius: 4px;
        background-color: $white-100;
        z-index: 20;
        .info-block-info {
          margin: 0;
          color: $grey-20;
          font-size: 15px;
          line-height: 100%;
          letter-spacing: -0.6px;
          &.title {
            font-size: 16px;
            line-height: 110%;
            letter-spacing: -0.64px;
          }
          &.value {
            margin-top: -16px;
            color: $black-100;
          }
        }
        .info-block-price {
          display: flex;
          flex-direction: column;
          gap: 4px;
          .info-block-div {
            display: flex;
            align-items: center;
            justify-content: space-between;
            .info-block-text {
              margin: 0;
              color: $black-40;
              font-size: 15px;
              line-height: 100%;
              letter-spacing: -0.6px;
              &.black {
                color: $grey-20;
                font-size: 16px;
                line-height: 110%;
                letter-spacing: -0.64px;
              }
              &.price {
                color: $black-100;
                font-family: Bounded;
                font-size: 16px;
                font-weight: 300;
                line-height: 80%;
                letter-spacing: -0.8px;
              }
            }
          }
        }
      }
      .cart-drawer {
        display: flex;
        flex-direction: column;
        background-color: $white-100;
        z-index: 20;
        .cart-items-frame {
          flex: 1;
          overflow-y: auto;
          padding: 0 10px 20px;
          position: relative;
          line-height: 100%;
          letter-spacing: -0.04em;
          scrollbar-width: thin;
          scrollbar-color: $black-25 transparent;
          &::after {
            content: '';
            position: sticky;
            bottom: 0;
            left: 0;
            right: 0;
            height: 20px;
            background: linear-gradient(transparent, $black-10);
            pointer-events: none;
          }
          &::-webkit-scrollbar {
            width: 6px;
          }
          &::-webkit-scrollbar-track {
            background: transparent;
          }
          &::-webkit-scrollbar-thumb {
            background-color: $black-40;
            border-radius: 3px;
          }
        }
        .cart-item {
          display: flex;
          padding: 24px 0;
          border-top: 1px solid $grey-87;
          &:last-child {
            border-bottom: 1px solid $grey-87;
          }
          .item-image-container {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 5px;
            min-width: 134px;
            min-height: 178px;
            width: 134px;
            height: 178px;
            border-radius: 8px;
            background-color: $grey-95;
            img {
              width: 100%;
              height: 100%;
              object-fit: cover;
            }
          }
          .item-details-div {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-left: 8px;
            height: 188px;
            .item-details {
              display: flex;
              flex-direction: column;
              .item-brand {
                margin: 0 0 12px;
                color: $black-60;
                font-size: 15px;
                line-height: 100%;
                letter-spacing: -0.6px;
              }
              .item-sku {
                margin: 8px 0 16px;
                color: $black-60;
                font-size: 12px;
                line-height: 100%;
                letter-spacing: -0.48px;
              }
              .item-name-price {
                margin: 0;
                color: $black-100;
                font-family: Bounded;
                font-size: 16px;
                font-weight: 300;
                line-height: 90%;
                letter-spacing: -0.8px;
              }
            }
            .item-info-row {
              display: flex;
              align-items: flex-end;
              font-size: 12px;
              .item-info-div {
                display: flex;
                flex-direction: column;
                gap: 4px;
                .item-info {
                  flex: 0 0 80%;
                  margin: 0;
                  color: $black-40;
                  font-size: 15px;
                  line-height: 100%;
                  letter-spacing: -0.6px;
                  &-value {
                    color: $grey-20;
                  }
                }
              }
              .add-btn {
                margin-left: auto;
                padding: 0;
                height: 24px;
                border: none;
                background: none;
                cursor: pointer;
                .add-text {
                  display: none;
                  font-size: 12px;
                  color: $black-40;
                  border-bottom: 1px solid $black-40;
                }
                .add-icon {
                  width: 24px;
                  height: 24px;
                  object-fit: cover;
                }
              }
            }
          }
        }
      }
    }
    .products-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(187px, 1fr));
      transition: filter 0.25s ease-in-out;
      .product-card {
        display: flex;
        flex-direction: column;
        position: relative;
        min-width: 0;
        background-color: $grey-89;
        cursor: pointer;
        transition: transform 0.25s ease-in-out;
        .remove-fav-btn {
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
        .product-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .product-info {
          display: flex;
          flex-direction: column;
          padding: 10px 10px 16px;
          background-color: $grey-87;
          .product-brand {
            margin: 0;
            font-size: 12px;
            line-height: 100%;
            letter-spacing: -0.48px;
            color: $black-60;
          }
          .product-name {
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
          .product-price {
            margin: 0;
            font-size: 15px;
            line-height: 80%;
            letter-spacing: -0.6px;
            color: $grey-20;
          }
        }
      }
    }
    .buttons {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin-top: 30px;
      gap: 24px;
    }
    .radio-button {
      display: flex;
      align-items: center;
      gap: 8px;
      color: $black-100;
      font-size: 15px;
      line-height: 100%;
      letter-spacing: -0.6px;
      input[type="radio"] {
        margin: 0;
        appearance: none;
        width: 20px;
        height: 20px;
        border: 1px solid $black-40;
        border-radius: 50%;
        background: none;
        cursor: pointer;
      }
      input[type="radio"]:checked {
        border-color: $black-100;
        background-color: $black-100;
        box-shadow: inset 0 0 0 4px $white-100;
      }
    }
    .action-button {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 24px;
      width: 100%;
      height: 56px;
      border: none;
      border-radius: 4px;
      background-color: $grey-20;
      color: $white-100;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      cursor: pointer;
      z-index: 20;
    }
    .default-button {
      display: flex;
      align-items: center;
      justify-content: center;
      border: none;
      background: none;
      color: $black-100;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      cursor: pointer;
      z-index: 20;
    }
  }
}

@media (max-width: 600px) {
  .profile-page {
    margin-top: 96px;
  }
}

</style>
