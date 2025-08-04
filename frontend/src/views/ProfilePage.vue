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
      <button type="button" @click="onLogout()">Выйти из профиля</button>
    </div>

    <!-- Контент секции -->
    <div v-if="currentSection==='profile'" class="content profile">
      <!-- Фото + загрузка -->
      <div class="card photo">
        <label>Фото профиля</label>
        <div class="photo-row">
          <div class="avatar">
            <img :src="store.userStore.user.photo_url || icon_default_avatar_grey" alt="">
          </div>
          <button v-if="!hasPhoto" @click="triggerFile">Загрузить</button>
          <template v-else>
            <button @click="triggerFile">Изменить</button>
            <button class="text" @click="removePhoto">Удалить</button>
          </template>
          <input type="file" ref="fileInput" class="visually-hidden" @change="onFileChange" />
        </div>
      </div>

      <!-- Личные данные -->
      <div class="card info">
        <label>Личная информация</label>
        <input v-model="form.last_name" placeholder="Фамилия*" />
        <input v-model="form.first_name" placeholder="Имя*" />
        <input v-model="form.middle_name" placeholder="Отчество*" />
        <input v-model="form.username" placeholder="Никнейм*" />
      </div>

      <!-- Пол -->
      <div class="card gender">
        <label>Пол</label>
        <label><input type="radio" value="male"   v-model="form.gender" /> Мужчина</label>
        <label><input type="radio" value="female" v-model="form.gender" /> Женщина</label>
      </div>

      <!-- Дата рождения -->
      <div class="card dob">
        <label>Дата рождения</label>
        <input v-model="form.date_of_birth" placeholder="ДД / ММ / ГГГГ" />
      </div>

      <!-- Контакты -->
      <div class="card contacts">
        <label>Контакты</label>
        <input v-model="form.phone" placeholder="Телефон*" />
        <input v-model="form.email" placeholder="Почта*" />
      </div>

      <button class="save" @click="saveProfile">Сохранить</button>
    </div>

    <div v-if="currentSection==='orders'" class="content orders">
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
          <div class="info-block cost">
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
          <button v-if="orderDetail.canRepeat" class="repeat" @click="repeatOrder(orderDetail.id)">Повторить заказ</button>
        </div>
      </div>
    </div>

    <div v-if="currentSection==='addresses'" class="content addresses">
      <div v-if="!addresses.length" class="empty">
        У тебя нет сохранённых адресов.
        <button class="add-btn" @click="editAddress()">Добавить адрес</button>
      </div>
      <div v-else>
        <div v-for="a in addresses" :key="a.id" class="addr-item" @click="selectAddress(a.id)">
          <label><input type="radio" :value="a.id" v-model="selectedAddress" /> {{ a.full }}</label>
          <button class="edit" @click.stop="editAddress(a)">›</button>
        </div>
        <button class="add-btn" @click="editAddress()">Добавить адрес</button>
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
          <button class="save" @click="saveAddress">Сохранить</button>
          <button class="cancel" @click="cancelAddress">Отменить</button>
          <button v-if="addressForm.id" class="delete" @click="deleteAddress(addressForm.id)">Удалить адрес</button>
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
  first_name: '',
  last_name: '',
  middle_name: '',
  username: '',
  gender: '',
  date_of_birth: '',
  phone: '',
  email: '',
  photo_url: null,
  _file: null,
  _remove: false,
})
const fileInput = ref()
const hasPhoto = computed(() => !!form.photo_url)

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

function onFileChange(e) {
  form._file = e.target.files[0]
}

function removePhoto() {
  form.photo_url = null;
  form._remove = true
}

// PROFILE: сохранить
async function saveProfile() {
  const fd = new FormData()
  for (const [k, v] of Object.entries(form)) {
    if (k === '_file' && v) {
      fd.append('photo', v)
    }
    else if (k.startsWith('_')) {
      continue
    }
    else {
      fd.append(k, v ?? '')
    }
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

watch(
  () => store.userStore.user,
  u => {
    Object.assign(form, {
      first_name:    u.first_name,
      last_name:     u.last_name,
      middle_name:   u.middle_name,
      username:      u.username,
      gender:        u.gender,
      date_of_birth: u.date_of_birth,
      phone:         u.phone,
      email:         u.email,
      photo_url:     u.photo_url,
      _file:         null,
      _remove:       false,
    })
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
  .subheader {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    .back-button {
      display: flex;
      align-items: center;
      background: none;
      border: none;
      font-family: Bounded;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      color: $black-100;
      cursor: pointer;
      img {
        width: 24px;
        height: 24px;
        margin-right: 8px;
      }
    }
  }
  .divider {
    height: 1px;
    background-color: $white-100;
    margin-bottom: 24px;
  }
  .content {
    .card {
      background-color: #FFFFFF;
      border-radius: 4px;
      padding: 16px;
      margin-bottom: 16px;
      label {
        display: block;
        font-family: Bounded;
        font-size: 16px;
        line-height: 80%;
        letter-spacing: -0.8px;
        color: $black-70;
        margin-bottom: 8px;
      }
    }
    .photo-row {
      display: flex;
      align-items: center;
      gap: 16px;
      .avatar {
        width: 96px;
        height: 96px;
        border-radius: 50%;
        background-size: cover;
        background-position: center;
      }
      button {
        padding: 12px 24px;
        border-radius: 24px;
        font-family: Bounded;
        font-size: 16px;
        line-height: 100%;
        letter-spacing: -0.64px;
        background-color: $black-100;
        color: #FFFFFF;
        border: none;
        cursor: pointer;
        &.text {
          background: none;
          color: $grey-30;
        }
      }
    }
    input,
    textarea {
      width: 100%;
      border: none;
      border-bottom: 1px solid $grey-90;
      padding: 8px 0;
      margin-bottom: 16px;
      font-family: Bounded;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
    }
    .gender {
      display: flex;
      gap: 32px;
      label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: Bounded;
        font-size: 16px;
        line-height: 100%;
        letter-spacing: -0.64px;
      }
    }
    .save,
    .add-btn,
    .repeat {
      display: block;
      width: 100%;
      padding: 16px;
      background-color: $black-100;
      color: #FFFFFF;
      font-family: Bounded;
      font-size: 32px;
      line-height: 100%;
      letter-spacing: -0.64px;
      border: none;
      border-radius: 4px;
      margin-top: 8px;
      cursor: pointer;
    }
    .orders {
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
          &.completed {
            background-color: #4CAF50;
          }
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
