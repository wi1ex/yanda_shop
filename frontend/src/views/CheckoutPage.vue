<template>
  <div class="checkout-page">
    <div class="line-vert"></div>
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
            <input class="info" v-model="form.last_name"  placeholder="Фамилия*" />
            <input class="info" v-model="form.email"      placeholder="Почта*" type="email" />
            <input class="info" v-model="form.phone"      placeholder="Телефон*" />
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
            <select class="info" v-model="form.address_id">
              <option v-for="a in store.userStore.addresses" :key="a.id" :value="a.id">
                {{ a.label }}
              </option>
            </select>
            <button type="button" class="action-button" @click="goAddAddress">Добавить адрес</button>
            <p v-if="!store.userStore.addresses.length" class="hint">Добавьте адрес в личном кабинете.</p>
          </div>
          <!-- 4. Способ оплаты -->
          <div class="card">
            <label class="card-label">3. Способ оплаты</label>
            <label class="radio-button">
              <input type="radio" value="card" v-model="form.payment" />
              Банковская карта
            </label>
            <label class="radio-button">
              <input type="radio" value="sbp" v-model="form.payment" />
              СБП
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
                <p class="info-block-text">Доставка:</p>
                <p class="info-block-text">{{ formatPrice(shipping) }} ₽</p>
              </div>
              <div class="row total">
                <p class="info-block-text black">Итог:</p>
                <p class="info-block-text price">{{ formatPrice(total) }} ₽</p>
              </div>
            </div>
            <label class="agree">
              <input type="checkbox" v-model="form.agree" />
              Я согласен на обработку персональных данных
            </label>
            <button type="button" class="action-button" :disabled="!canSubmit || loading" @click="submit">
              {{ loading ? 'Отправка...' : 'Перейти к оплате' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- SUCCESS -->
    <div v-else class="content">
      <div class="card success-card">
        <p class="success-title">Поздравляем!</p>
        <p class="success-text">
          Твой заказ оформлен, мы выкупим его в ближайшее время.
          За статусом заказа можешь следить в личном кабинете.
        </p>
        <div class="success-illustration">
          <img :src="icon_default_avatar_grey" alt="bag" />
        </div>
        <button type="button" class="action-button" @click="goOrders">
          Перейти к оплате
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/store'

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
const deliveryPriceMap = { courier_in_mkad: 400, courier_out_mkad: 400, pvz: 0 }
const deliveryTypeMap  = {
  courier_in_mkad: 'Курьер по Москве (в пределах МКАД)',
  courier_out_mkad: 'Курьер по Москве (за МКАД)',
  pvz: 'Доставка до ПВЗ',
}

const shipping = computed(() => deliveryPriceMap[form.delivery] ?? 0)
const subtotal = computed(() => store.cartStore.items.reduce((s, i) => s + i.unit_price * i.quantity, 0))
const total    = computed(() => subtotal.value + shipping.value)

const canSubmit = computed(() =>
  store.cartStore.items.length > 0 &&
  form.first_name && form.last_name && form.email && form.phone &&
  form.payment &&
  (form.delivery === 'pvz' || form.address_id) &&
  form.agree
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

function goOrders() {
  router.push({ name: "Profile", query: { section: "orders" } })
}

function goAddAddress() {
  router.push({ name: "Profile", query: { section: "addresses" } })
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
  .content {
    display: flex;
    flex-direction: column;
  }
  .grid {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 0 10px;
  }
  .card {
    display: flex;
    flex-direction: column;
    margin-bottom: 10px;
    padding: 20px 10px;
    border-radius: 4px;
    background-color: $white-100;
    .card-label {
      margin-bottom: 24px;
      color: $grey-20;
      font-size: 16px;
      line-height: 110%;
      letter-spacing: -0.64px;
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
    .hint {
      margin-top: 8px;
      color: $black-40;
      font-size: 12px;
    }
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
  .right .card {
    position: sticky;
    top: 20px;
  }
  .cart-items-frame {
    display: flex;
    flex-direction: column;
    padding: 0 0 12px;
    gap: 12px;
    .cart-item {
      display: flex;
      gap: 8px;
      align-items: center;
      padding: 12px 0;
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
        gap: 12px;
      }
      .item-details {
        .item-brand {
          margin: 0 0 12px;
          color: $black-60;
          font-size: 15px;
        }
        .item-name-price {
          margin: 0;
          color: $black-100;
          font-family: Bounded;
          font-size: 16px;
          font-weight: 375;
          line-height: 90%;
          letter-spacing: -0.8px;
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
    gap: 6px;
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
          font-weight: 375;
          line-height: 80%;
          letter-spacing: -0.8px;
        }
      }
    }
    .total .price {
      font-size: 18px;
    }
  }
  .agree {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0 16px;
    color: $black-100;
    font-size: 14px;
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
    letter-spacing: -0.64px;
    cursor: pointer;
    &:disabled {
      opacity: 0.6;
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
