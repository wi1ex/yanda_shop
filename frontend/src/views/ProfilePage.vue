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
      <button type="button" @click="onLogout()" v-if="!store.userStore.isTelegramWebApp">Выйти из профиля</button>
    </div>

    <div v-if="currentSection==='profile'" class="content">
      <h2>Мой профиль</h2>
      <p>Твои личные данные важны для покупок,<br>поэтому проверяй их актуальность.</p>
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
      <h2>Мои заказы</h2>
      <p v-if="!store.userStore.orders.length">У тебя нет оформленных заказов.</p>
      <button type="button" v-if="!store.userStore.orders.length" class="action-button" @click="goCatalog">Перейти в каталог</button>






      <div v-if="store.userStore.orders.length">
        <h2>Мои заказы</h2>
        <div v-for="o in store.userStore.orders" :key="o.id" class="order-card" @click="loadOrder(o.id)">
          <div class="status" :class="o.status">{{ o.statusLabel }}</div>
          <div class="preview">
            <img v-for="it in o.items.slice(0,3)" :src="it.image_url" :key="it.sku"  alt="image"/>
          </div>
          <div class="timeline">
            <span v-for="(d, idx) in o.datesFormated" :key="idx">{{ d }}</span>
          </div>
          <div class="total">Итог: {{ o.total }} ₽</div>
        </div>

        <div v-if="store.userStore.orderDetail" class="order-detail">
          <h2>#{{ store.userStore.orderDetail.id }} <span class="status">{{ store.userStore.orderDetail.statusLabel }}</span></h2>
          <div class="timeline-full">
            <div v-for="(stage, idx) in store.userStore.orderDetail.timeline" :key="idx" class="stage">
              <div class="dot" :class="{done: stage.done}"></div>
              <div class="line" v-if="idx<store.userStore.orderDetail.timeline.length-1"></div>
              <p>{{ stage.label }}<br/><small>{{ stage.date }}</small></p>
            </div>
          </div>
          <div class="info-block">
            <p>Оплата: {{ store.userStore.orderDetail.payment_method }}</p>
            <p>Доставка: {{ store.userStore.orderDetail.delivery_type }}</p>
            <p>Адрес: {{ store.userStore.orderDetail.delivery_address }}</p>
          </div>
          <div class="info-block">
            <p>Сумма товаров: {{ store.userStore.orderDetail.subtotal }} ₽</p>
            <p>Курьер: {{ store.userStore.orderDetail.delivery_price }} ₽</p>
            <p class="bold">Итог: {{ store.userStore.orderDetail.total }} ₽</p>
          </div>
          <div class="items">
            <div v-for="it in store.userStore.orderDetail.items" :key="it.sku" class="item">
              <img :src="it.image_url"  alt="image"/>
              <div>
                <p class="title">{{ it.brand }} {{ it.name }}</p>
                <p>Артикул: {{ it.sku }}</p>
                <p>Кол-во: {{ it.qty }}</p>
                <p>Размер: {{ it.size }}</p>
                <p>Доставка: {{ it.delivery_period }}</p>
              </div>
            </div>
          </div>
          <button type="button" v-if="store.userStore.orderDetail.canRepeat" class="repeat" @click="repeatOrder(store.userStore.orderDetail.id)">Повторить заказ</button>
        </div>
      </div>






    </div>

    <div v-if="currentSection==='addresses'" class="content">
      <h2 :style="{ marginBottom: (sortedAddresses.length || addressFormVisible) ? '40px' : '' }">
        Мои адреса{{ sortedAddresses.length ? ` [ ${sortedAddresses.length} ]` : '' }}
      </h2>
      <p v-if="!sortedAddresses.length && !addressFormVisible">У тебя нет сохранённых адресов.</p>
      <div v-if="sortedAddresses.length && !addressFormVisible" class="list_addresses">
        <div v-for="a in sortedAddresses" class="address" :key="a.id">
          <label class="radio-button address-text" @click="selectAddress(a.id)">
            <input type="radio" :value="a.id" v-model="selectedAddress" />
            {{ a.full }}
          </label>
          <button type="button" @click.stop="editAddress(a)">
            <img :src="icon_arrow_mini_black" alt="" style="transform: rotate(180deg)"/>
          </button>
        </div>
      </div>
      <button type="button" v-if="!addressFormVisible" class="action-button" @click="editAddress()">Добавить адрес</button>

      <div v-if="addressFormVisible" class="card">
        <label class="card-label">{{ addressForm.id ? 'Редактировать адрес' : 'Добавить новый адрес' }}</label>
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
        <button type="button" v-if="!addressForm.id" class="action-button" @click="saveAddress">Сохранить</button>
        <button type="button" v-if="!addressForm.id" class="default-button" @click="cancelAddress">Отменить</button>
        <button type="button" v-if="addressForm.id" class="action-button" @click="deleteAddress(addressForm.id)">Удалить адрес</button>
      </div>
    </div>
  </div>
  <div class="line-hor" style="margin-top: 96px;"></div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

import icon_default_avatar_grey from '@/assets/images/default_avatar_grey.svg'
import icon_arrow_grey from "@/assets/images/arrow_grey.svg";
import icon_arrow_mini_black from "@/assets/images/arrow_mini_black.svg";
import icon_arrow_mini_red from "@/assets/images/arrow_mini_red.svg";

const store = useStore()
const router = useRouter()

// UI-state
const currentSection = ref(null)

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
  id: null,
  city: '',
  street: '',
  house: '',
  apartment: '',
  intercom: '',
  entrance: '',
  floor: '',
  comment: '',
})

const sortedAddresses = computed(() => {
  const list = store.userStore.addresses.slice()
  const primary = list.filter(a => a.selected)
  const others = list
    .filter(a => !a.selected)
    .sort((a, b) => a.full.localeCompare(b.full))
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
  if (sec==='addresses') {
    await store.userStore.fetchAddresses()
    selectedAddress.value = sortedAddresses.find(a => a.selected)?.id || null
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
}

function repeatOrder(id) {
  // например: store.userStore.repeatOrder(id) → router.push('/checkout')
}

// ADDRESSES
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
      id: null,
      city: '',
      street: '',
      house: '',
      apartment: '',
      intercom: '',
      entrance: '',
      floor: '',
      comment: ''
    })
  }
  addressFormVisible.value = true
}

function cancelAddress() {
  addressFormVisible.value = false
}

async function saveAddress() {
  if(addressForm.id)
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
      margin: 10px;
      color: $black-100;
      font-family: Bounded;
      font-size: 24px;
      font-weight: 250;
      line-height: 80%;
      letter-spacing: -1.2px;
      z-index: 20;
    }
    p {
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
