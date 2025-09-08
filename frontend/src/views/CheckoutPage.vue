<template>
  <div class="checkout-page">
    <div class="line-vert"></div>
    <button type="button" class="back-button" @click="goBack">
      <img :src="icon_arrow_grey" alt="arrow back" />
      Назад
    </button>
    <div class="line-hor"></div>
    <!-- FORM -->
    <div v-if="mode==='form'" class="content">
      <div class="grid">
        <!-- Левая колонка -->
        <div class="left">
          <!-- 1. Контакты -->
          <div class="card">
            <label class="card-label">1. Контакты</label>
            <input class="info" v-model="form.first_name" placeholder="Имя*" />
            <input class="info" v-model="form.last_name" placeholder="Фамилия*" />
            <input class="info" v-model="form.email" placeholder="Почта*" type="email" />
            <input class="info" v-model="form.phone" placeholder="Телефон*" @input="onPhoneInput" />
          </div>
          <!-- 2. Способ доставки -->
          <div class="card">
            <label class="card-label">2. Способ доставки</label>
            <label class="radio-button">
              <input type="radio" value="courier_in_mkad" v-model="form.delivery" />
              Курьером по Москве (в пределах МКАД)
            </label>
            <label class="radio-button">
              <input type="radio" value="courier_out_mkad" v-model="form.delivery" />
              Курьером по Москве (за МКАД)
            </label>
            <label class="radio-button">
              <input type="radio" value="pvz" v-model="form.delivery" />
              Доставка до ПВЗ
            </label>
          </div>
          <!-- 3. Адрес доставки -->
          <div class="card">
            <label class="card-label">3. Адрес доставки</label>
            <select v-if="store.userStore.addresses.length" class="info" v-model="form.address_id">
              <option v-for="a in store.userStore.addresses" :key="a.id" :value="a.id">
                {{ a.label }}
              </option>
            </select>
            <button type="button" class="address-button" @click="goAddAddress">Добавить адрес</button>
          </div>
          <!-- 4. Способ оплаты -->
          <div class="card">
            <label class="card-label">4. Способ оплаты</label>
            <label class="radio-button">
              <input type="radio" value="card" v-model="form.payment" />
              Банковская карта
              <img :src="icon_pay_card" alt="pay_card" />
            </label>
            <label class="radio-button">
              <input type="radio" value="sbp" v-model="form.payment" />
              СБП
              <img :src="icon_pay_sbp" alt="pay_sbp" />
            </label>
          </div>
        </div>
        <!-- Правая колонка -->
        <div class="right">
          <div class="card">
            <label class="card-label">Товары</label>
            <div class="cart-items-frame">
              <div v-for="it in items" :key="it.variant_sku + (it.delivery_option?.label || '')" class="cart-item">
                <div class="item-image-container">
                  <img :src="it.image" alt="" />
                </div>
                <div class="item-details-div">
                  <div class="item-details">
                    <p class="item-brand">{{ it.brand }}</p>
                    <p class="item-name-price">{{ it.name }}</p>
                    <p class="item-name-price">{{ formatPrice(it.unit_price) }} ₽</p>
                  </div>
                  <div class="item-info-row">
                    <div class="item-info-div">
                      <p class="item-info">
                        Количество:
                        <span class="item-info-value">{{ it.quantity }}</span>
                      </p>
                      <p class="item-info">
                        Размер:
                        <span class="item-info-value">{{ it.size_label }}</span>
                      </p>
                      <p class="item-info">
                        Доставка:
                        <span class="item-info-value">{{ it.delivery_option?.label || '—' }}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="price-block">
              <div class="row">
                <p class="info-block-text">Стоимость:</p>
                <p class="info-block-text">{{ formatPrice(subtotal) }} ₽</p>
              </div>
              <div class="row">
                <p class="info-block-text">{{ deliveryTypeMap[form.delivery] }}:</p>
                <p class="info-block-text">{{ formatPrice(shipping) }} ₽</p>
              </div>
              <div class="row total">
                <p class="info-block-text black">Итог:</p>
                <p class="info-block-text price">{{ formatPrice(total) }} ₽</p>
              </div>
            </div>
            <label class="agree">
              <input type="checkbox" v-model="form.agree" />
              <span>Я согласен на обработку персональных данных</span>
            </label>
          </div>
        </div>
        <button type="button" class="action-button" :disabled="!canSubmit || loading" @click="submit">
          {{ loading ? 'Отправка...' : 'Перейти к оплате' }}
        </button>
      </div>
    </div>
    <!-- SUCCESS -->
    <div v-else class="content">
      <div class="card success-card">
        <p class="success-title">Поздравляем!</p>
        <p class="success-text">
          Твой заказ оформлен, мы выкупим его в ближайшее время. За статусом заказа можешь следить в личном кабинете.
        </p>
        <div class="success-illustration">
          <img :src="icon_default_avatar_grey" alt="bag" />
        </div>
        <button type="button" class="action-button" @click="goOrders">
          Посмотреть заказ
        </button>
      </div>
    </div>
  </div>
  <div class="line-hor"></div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store'

import icon_pay_sbp from '@/assets/images/pay_sbp.svg'
import icon_pay_card from '@/assets/images/pay_card.svg'
import icon_arrow_grey from '@/assets/images/arrow_grey.svg'
import icon_default_avatar_grey from '@/assets/images/default_avatar_grey.svg'

const router = useRouter()
const store = useStore()

const mode = ref('form') // 'form' | 'success'
const createdOrderId = ref(null)
const loading = ref(false)
const items = computed(() => store.cartStore.groupedCartItems)


const form = reactive({
  first_name: store.userStore.user.first_name || '',
  last_name:  store.userStore.user.last_name  || '',
  middle_name: store.userStore.user.middle_name || '',
  phone:      store.userStore.user.phone || '',
  email:      store.userStore.user.email || '',
  delivery:   'courier_in_mkad',
  payment:    'card',
  address_id: null,
  agree:      false,
})

// цена доставки и отображаемое имя
const deliveryPriceMap = { courier_in_mkad: 400, courier_out_mkad: 600, pvz: 0 }
const deliveryTypeMap  = {
  courier_in_mkad: 'Курьер по Москве (в пределах МКАД)',
  courier_out_mkad: 'Курьер по Москве (за МКАД)',
  pvz: 'Доставка до ПВЗ',
}

const shipping = computed(() => deliveryPriceMap[form.delivery] ?? 0)
const subtotal = computed(() => items.value.reduce((s, i) => s + Number(i.unit_price || 0) * Number(i.quantity || 0), 0))
const total    = computed(() => subtotal.value + shipping.value)

const canSubmit = computed(() =>
  items.value.length > 0 &&
  form.first_name && form.last_name && form.email && form.phone &&
  form.payment && (form.delivery === 'pvz' || form.address_id) && form.agree
)

function formatPrice(v) {
  return String(v).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

async function submit() {
  if (!canSubmit.value || loading.value) return
  loading.value = true
  const payload = {
    address_id:     form.delivery === 'pvz' ? null : form.address_id,
    payment_method: form.payment === 'card' ? 'Банковская карта' : 'СБП',
    delivery_type:  deliveryTypeMap[form.delivery],
    delivery_price: shipping.value,
    first_name:     form.first_name,
    last_name:      form.last_name,
    middle_name:    form.middle_name,
    phone:          form.phone,
    email:          form.email,
  }
  const orderId = await store.cartStore.placeOrder(payload)
  loading.value = false
  if (orderId) {
    createdOrderId.value = orderId
    mode.value = 'success'
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    alert('Не удалось оформить заказ. Попробуйте ещё раз.')
  }
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

function goOrders() {
  router.push({ name: "Profile", query: { section: "orders" } })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goAddAddress() {
  router.push({ name: "Profile", query: { section: "addresses" } })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ← Назад
function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({ name: 'Home' })
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  if (!store.userStore.addresses.length) await store.userStore.fetchAddresses()
  const primary = store.userStore.addresses.find(a => a.selected)
  form.address_id = primary ? primary.id : null
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

.checkout-page {
  margin-top: 120px;
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
  .content {
    display: flex;
    flex-direction: column;
  }
  .grid {
    display: flex;
    flex-direction: column;
    gap: 40px;
  }
  .card {
    display: flex;
    position: relative;
    flex-direction: column;
    margin-bottom: 10px;
    padding: 20px 10px;
    border-radius: 4px;
    background-color: $white-100;
    z-index: 20;
    .card-label {
      margin-bottom: 24px;
      color: $black-100;
      font-family: Bounded;
      font-size: 24px;
      font-weight: 250;
      line-height: 80%;
      letter-spacing: -1.2px;
    }
    .address-button {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 24px;
      width: 100%;
      height: 40px;
      border: none;
      border-radius: 4px;
      background-color: $grey-20;
      color: $white-100;
      font-size: 16px;
      letter-spacing: -0.64px;
      cursor: pointer;
    }
    .info {
      margin-bottom: 15px;
      padding: 21px 10px 8px;
      width: calc(100% - 20px);
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
  }
  .radio-button {
    display: flex;
    align-items: center;
    padding: 16px 10px;
    gap: 8px;
    border-radius: 4px;
    background-color: $grey-95;
    color: $black-100;
    font-size: 15px;
    line-height: 100%;
    letter-spacing: -0.6px;
    margin-bottom: 16px;
    &:last-child {
      margin-bottom: 0;
    }
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
    img {
      height: 20px;
      object-fit: cover;
    }
  }
  .right .card {
    position: sticky;
    top: 20px;
  }
  .cart-items-frame {
    display: flex;
    flex-direction: column;
    padding: 0 0 12px;
    .cart-item {
      display: flex;
      gap: 8px;
      align-items: center;
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
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 188px;
        gap: 12px;
      }
      .item-details {
        .item-brand {
          margin: 0 0 8px;
          color: $black-60;
          font-size: 12px;
          line-height: 100%;
          letter-spacing: -0.48px;
        }
        .item-name-price {
          margin: 0 0 16px;
          color: $black-100;
          font-family: Manrope-SemiBold;
          font-size: 15px;
          line-height: 100%;
          letter-spacing: -0.6px;
        }
      }
      .item-info-row .item-info {
        margin: 0;
        color: $black-40;
        font-size: 15px;
        line-height: 100%;
        letter-spacing: -0.6px;
      }
      .item-info-value {
        color: $grey-20;
      }
    }
  }
  .price-block {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 16px 0 12px;
    .row {
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
    .total {
      margin-top: 16px;
      .price {
        font-size: 18px;
      }
    }
  }
  .agree {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0 16px;
    color: $black-100;
    font-size: 14px;
    input[type="checkbox"] {
      -webkit-appearance: none;
      appearance: none;
      min-width: 16px;
      min-height: 16px;
      width: 16px;
      height: 16px;
      border: 1px solid $black-40;
      border-radius: 2px;
      cursor: pointer;
      vertical-align: middle;
      background-color: transparent;
    }
    input[type="checkbox"]:checked {
      border-color: $grey-20;
    }
    input[type="checkbox"]:checked::after {
      content: "";
      position: absolute;
      top: 5px;
      left: 9px;
      width: 5px;
      height: 8px;
      border: solid $grey-20;
      border-width: 0 1px 1px 0;
      transform: rotate(45deg);
    }
    span {
      color: $grey-20;
      font-size: 15px;
      line-height: 110%;
      letter-spacing: -0.6px;
    }
  }
  .action-button {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: -56px 0 96px;
    padding: 0 24px;
    width: 100%;
    height: 72px;
    border: none;
    border-radius: 4px;
    background-color: $grey-20;
    color: $white-100;
    font-size: 16px;
    letter-spacing: -0.64px;
    cursor: pointer;
    z-index: 50;
    &:disabled {
      cursor: default;
    }
  }
  .success-card {
    align-items: center;
    text-align: center;
    gap: 16px;
    margin: 40px 10px 0;
  }
  .success-title {
    margin: 0;
    color: $black-100;
    font-family: Bounded;
    font-size: 24px;
    font-weight: 250;
    line-height: 80%;
    letter-spacing: -1.2px;
  }
  .success-text {
    margin: 0;
    color: $grey-20;
    font-size: 15px;
    line-height: 110%;
    letter-spacing: -0.6px;
  }
  .success-illustration {
    display: flex;
    justify-content: center;
    padding: 8px 0 12px;
    img {
      width: 96px;
      height: 96px;
      object-fit: contain;
      opacity: 0.9;
    }
  }
}

@media (max-width: 600px) {
  .checkout-page {
    margin-top: 96px;
  }
}

</style>
