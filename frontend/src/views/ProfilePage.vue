<template>
  <div class="profile-page">
    <div class="line-vert"></div>
    <h1 class="section-title">ЛИЧНЫЙ КАБИНЕТ</h1>

    <button type="button" class="back-button" @click="goBack()">
      <img :src="icon_arrow_grey" alt="arrow back" />
      {{ currentSection ? 'Мой кабинет' : 'Назад' }}
    </button>

    <div class="line-hor"></div>

    <div class="profile-menu" v-if="!currentSection">
      <button type="button" @click="select('profile')">Мой профиль</button>
      <button type="button" @click="select('orders')">Заказы</button>
      <button type="button" @click="select('addresses')">Мои адреса</button>
      <button type="button" @click="onLogout()" v-if="!store.userStore.isTelegramWebApp">Выйти из профиля</button>
    </div>

    <!-- Контент секции -->
    <div v-if="currentSection==='profile'" class="content">
      <h2>Мой профиль</h2>
      <p>Твои личные данные важны для покупок,<br>поэтому проверяй их актуальность.</p>
      <!-- Фото + загрузка -->
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
      <!-- Личные данные -->
      <div class="card">
        <label class="card-label">Личная информация</label>
        <input class="info" v-model="form.last_name" placeholder="Фамилия*" />
        <input class="info" v-model="form.first_name" placeholder="Имя*" />
        <input class="info" v-model="form.middle_name" placeholder="Отчество*" />
      </div>
      <!-- Пол -->
      <div class="card">
        <label class="card-label">Пол</label>
        <div class="gender">
          <label class="gender-label">
            <input type="radio" value="male" v-model="form.gender" />
            Мужчина
          </label>
          <label class="gender-label">
            <input type="radio" value="female" v-model="form.gender" />
            Женщина
          </label>
        </div>
      </div>
      <!-- Дата рождения -->
      <div class="card">
        <label class="card-label">Дата рождения</label>
        <input class="info" type="date" ref="dateInput" v-model="form.date_of_birth" @click="openCalendar" :max="maxDate" />
      </div>
      <!-- Контакты -->
      <div class="card">
        <label class="card-label">Контакты</label>
        <input class="info" v-model="form.phone" placeholder="Телефон*" @input="onPhoneInput" />
        <input class="info" v-model="form.email" placeholder="Почта*" type="email"/>
      </div>
      <!-- Кнопка Сохранить -->
      <button type="button" v-if="formDirty" class="save" @click="saveProfile">Сохранить</button>
    </div>

    <div v-if="currentSection==='orders'" class="content">
      <div v-if="!orders.length" class="empty">
        У тебя нет оформленных заказов.
      </div>
      <div v-else>
        <div v-for="o in orders" :key="o.id" class="order-card" @click="loadOrder(o.id)">
          <div class="status" :class="o.status">{{ o.statusLabel }}</div>
          <div class="preview">
            <img v-for="it in o.items.slice(0,3)" :src="it.image_url" :key="it.sku"  alt="image"/>
          </div>
          <div class="timeline">
            <span v-for="(d, idx) in o.datesFormated" :key="idx">{{ d }}</span>
          </div>
          <div class="total">Итог: {{ o.total }} ₽</div>
        </div>

        <!-- Детали заказа -->
        <div v-if="orderDetail" class="order-detail">
          <h2>#{{ orderDetail.id }} <span class="status">{{ orderDetail.statusLabel }}</span></h2>
          <div class="timeline-full">
            <div v-for="(stage, idx) in orderDetail.timeline" :key="idx" class="stage">
              <div class="dot" :class="{done: stage.done}"></div>
              <div class="line" v-if="idx<orderDetail.timeline.length-1"></div>
              <p>{{ stage.label }}<br/><small>{{ stage.date }}</small></p>
            </div>
          </div>
          <div class="info-block">
            <p>Оплата: {{ orderDetail.payment_method }}</p>
            <p>Доставка: {{ orderDetail.delivery_type }}</p>
            <p>Адрес: {{ orderDetail.delivery_address }}</p>
          </div>
          <div class="info-block">
            <p>Сумма товаров: {{ orderDetail.subtotal }} ₽</p>
            <p>Курьер: {{ orderDetail.delivery_price }} ₽</p>
            <p class="bold">Итог: {{ orderDetail.total }} ₽</p>
          </div>
          <div class="items">
            <div v-for="it in orderDetail.items" :key="it.sku" class="item">
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
          <button type="button" v-if="orderDetail.canRepeat" class="repeat" @click="repeatOrder(orderDetail.id)">Повторить заказ</button>
        </div>
      </div>
    </div>

    <div v-if="currentSection==='addresses'" class="content">
      <div v-if="!addresses.length" class="empty">
        У тебя нет сохранённых адресов.
        <button type="button" class="add-btn" @click="editAddress()">Добавить адрес</button>
      </div>
      <div v-else>
        <div v-for="a in addresses" :key="a.id" class="addr-item" @click="selectAddress(a.id)">
          <label><input type="radio" :value="a.id" v-model="selectedAddress" /> {{ a.full }}</label>
          <button type="button" class="edit" @click.stop="editAddress(a)">›</button>
        </div>
        <button type="button" class="add-btn" @click="editAddress()">Добавить адрес</button>
      </div>

      <!-- Форма адреса -->
      <div v-if="addressFormVisible" class="card form">
        <label>Город*</label><input v-model="addressForm.city" placeholder="Город*" />
        <label>Улица*</label><input v-model="addressForm.street" placeholder="Улица*" />
        <label>Дом*</label><input v-model="addressForm.house" placeholder="Дом*" />
        <div class="row">
          <input v-model="addressForm.apartment" placeholder="Квартира" />
          <input v-model="addressForm.intercom" placeholder="Домофон" />
        </div>
        <div class="row">
          <input v-model="addressForm.entrance" placeholder="Подъезд" />
          <input v-model="addressForm.floor" placeholder="Этаж" />
        </div>
        <label>Комментарий курьеру</label>
        <textarea v-model="addressForm.comment" placeholder="Комментарий курьеру"></textarea>
        <div class="buttons">
          <button type="button" class="save" @click="saveAddress">Сохранить</button>
          <button type="button" class="cancel" @click="cancelAddress">Отменить</button>
          <button type="button" v-if="addressForm.id" class="delete" @click="deleteAddress(addressForm.id)">Удалить адрес</button>
        </div>
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

const formDirty = computed(() => {
  const u = store.userStore.user
  const normPhone = v => String(v||'').replace(/\D/g, '')
  return (
    form.first_name  !== (u.first_name  || '') ||
    form.last_name   !== (u.last_name   || '') ||
    form.middle_name !== (u.middle_name || '') ||
    form.gender      !== (u.gender      || '') ||
    form.date_of_birth !== (u.date_of_birth || '') ||
    normPhone(form.phone) !== (u.phone  || '') ||
    form.email       !== (u.email       || '')
  )
})

// ORDERS
const orders      = ref([])
const orderDetail = ref(null)

// ADDRESSES
const addresses           = ref([])
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

function openCalendar() {
  dateInput.value?.showPicker?.()
}

// Смена раздела
async function select(sec) {
  currentSection.value = sec
  orderDetail.value = null
  addressFormVisible.value = false
  if (sec==='orders') {
    orders.value = await store.userStore.fetchOrders()
  }
  if (sec==='addresses') {
    addresses.value = await store.userStore.fetchAddresses()
  }
}

// LOGOUT
async function onLogout() {
  await store.userStore.logout()
  router.push({ name: 'Home' })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goBack() {
  if (currentSection.value) {
    currentSection.value = null
  } else {
    if (window.history.length > 1) {
      router.back()
    } else {
      router.push({ name: 'Home' })
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// PROFILE: загрузка файла
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

// PROFILE: сохранить
async function saveProfile() {
  const fd = new FormData()
  for (const [k, v] of Object.entries(form)) {
    fd.append(k, v ?? '')
  }
  await store.userStore.updateProfile(fd)
}

// ORDERS: детали
async function loadOrder(id) {
  orderDetail.value = await store.userStore.fetchOrder(id)
}

// ORDERS: повторить
function repeatOrder(id) {
  // например: store.userStore.repeatOrder(id) → router.push('/checkout')
}

// ADDRESSES
function selectAddress(id) {
  selectedAddress.value = id
}

function editAddress(a = null) {
  if(a){
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
  addresses.value = await store.userStore.fetchAddresses()
  addressFormVisible.value = false
}

async function deleteAddress(id) {
  await store.userStore.deleteAddress(id)
  addresses.value = await store.userStore.fetchAddresses()
  addressFormVisible.value = false
}

function formatPhone(raw = '') {
  raw = String(raw || '')
  let d = raw.replace(/\D/g, '').slice(0, 11)
  if (d && d[0] !== '8') d = '8' + d
  const [c1, c2, c3, c4, c5] = [
    d.slice(0,1),
    d.slice(1,4),
    d.slice(4,7),
    d.slice(7,9),
    d.slice(9,11),
  ]
  let out = ''
  if (c1) out = c1
  if (c2) out += ` (${c2}`
  if (c2.length === 3) out += `)`
  if (c3) out += ` ${c3}`
  if (c4) out += `-${c4}`
  if (c5) out += `-${c5}`
  return out
}

function onPhoneInput(e) {
  const formatted = formatPhone(e.target.value)
  e.target.value = formatted
  form.phone = formatted
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
    form.phone         = formatPhone(u.phone)
    form.email         = u.email         || ''
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
        .gender-label {
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
          }
          input[type="radio"]:checked {
            border-color: $black-100;
            background-color: $black-100;
            box-shadow: inset 0 0 0 4px $white-100;
          }
        }
      }
    }
    .save {
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

    .orders {
      .add-btn,
      .repeat {
        display: block;
        width: 100%;
        padding: 16px;
        background-color: $black-100;
        color: #FFFFFF;
        font-family: Bounded;
        font-size: 16px;
        line-height: 100%;
        letter-spacing: -0.64px;
        border: none;
        border-radius: 4px;
        margin-top: 8px;
        cursor: pointer;
      }
      .order-card {
        position: relative;
        background-color: #FFFFFF;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 16px;
        cursor: pointer;
        .status {
          position: absolute;
          top: 16px;
          right: 16px;
          background-color: $grey-90;
          border-radius: 12px;
          padding: 4px 8px;
          font-family: Bounded;
          font-size: 14px;
          line-height: 100%;
          color: #FFFFFF;
        }
        .preview img {
          width: 40px;
          height: 40px;
          border-radius: 4px;
          margin-right: 8px;
        }
        .timeline {
          display: flex;
          gap: 8px;
          font-family: Bounded;
          font-size: 12px;
          line-height: 100%;
          color: $grey-87;
          margin: 16px 0;
        }
        .total {
          font-family: Bounded;
          font-size: 18px;
          line-height: 100%;
          text-align: right;
        }
      }
    }
    .order-detail {
      .timeline-full {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
        .stage {
          text-align: center;
          flex: 1;
          .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: $grey-90;
            margin: 0 auto;
            &.done {
              background-color: #4CAF50;
            }
          }
          .line {
            height: 2px;
            background-color: $grey-90;
            margin: 4px auto;
          }
          p {
            font-family: Bounded;
            font-size: 12px;
            line-height: 100%;
            margin-top: 4px;
          }
        }
      }
      .info-block {
        background-color: #FFFFFF;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 16px;
        p {
          margin: 4px 0;
        }
        &.cost .bold {
          font-weight: 600;
        }
      }
      .items .item {
        display: flex;
        background-color: #FFFFFF;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 16px;
        img {
          width: 80px;
          height: 80px;
          border-radius: 4px;
        }
        .title {
          font-family: Bounded;
          font-size: 16px;
          font-weight: 500;
          line-height: 100%;
          margin-bottom: 4px;
        }
      }
    }
    .addresses {
      .addr-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #FFFFFF;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 8px;
        label {
          font-family: Bounded;
          font-size: 16px;
          line-height: 100%;
        }
        .edit {
          background: none;
          border: none;
          font-size: 24px;
          color: $grey-87;
          cursor: pointer;
        }
      }
      .form {
        .row {
          display: flex;
          gap: 16px;
        }
        .buttons {
          display: flex;
          gap: 8px;
          margin-top: 16px;
          .cancel {
            background: none;
            color: $grey-87;
          }
          .delete {
            background-color: #FF5E5E;
            color: #FFFFFF;
          }
        }
      }
    }
  }
}

@media (max-width: 600px) {
  .profile-page {
    margin-top: 96px;
  }
}

</style>
