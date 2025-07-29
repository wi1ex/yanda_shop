<template>
  <transition name="drawer">
    <div v-if="store.cartStore.showCartDrawer" class="cart-drawer-overlay" @click.self="store.cartStore.closeCartDrawer()">
      <div class="cart-drawer">

        <div class="cart-header">
          <h2 v-if="store.cartStore.cart.items.length === 0">Корзина</h2>
          <h2 v-else>Корзина [ {{ store.cartStore.cart.count }} ]</h2>
          <button type="button" class="close-btn" @click="store.cartStore.closeCartDrawer()">
            <img :src="icon_close" alt="Закрыть" />
          </button>
        </div>

        <div v-if="store.cartStore.cart.items.length === 0" class="empty-cart">
          В корзине пока что ничего нет...
          <button type="button" class="action-button" @click="goToCatalog">
            Перейти в каталог
          </button>
        </div>

        <div v-else class="cart-items-frame">
          <div v-for="item in store.cartStore.groupedCartItems" :key="item.variant_sku" class="cart-item">
            <div class="item-image-container">
              <img :src="item.image" alt="" />
            </div>
            <div class="item-details">
              <p class="item-brand">{{ item.brand }}</p>
              <div class="item-title-price">
                <p class="item-name">{{ item.name }}</p>
                <p class="item-price">{{ formatPrice(item.unit_price) }} ₽</p>
              </div>

              <div class="item-quantity-controls">
                <button type="button" class="qty-btn" @click="store.cartStore.decreaseQuantity(item)">
                  <img :src="icon_minus_grey" alt="Минус" />
                </button>
                <span class="qty">{{ item.quantity }}</span>
                <button type="button" class="qty-btn" @click="store.cartStore.increaseQuantity(item)">
                  <img :src="icon_plus_grey" alt="Плюс" />
                </button>
              </div>

              <div class="item-info-row">
                <p class="item-info">
                  Размер:
                  <span class="item-info-value">{{ item.size_label }}</span>
                </p>
                <p class="item-info">
                  Доставка:
                  <span class="item-info-value">{{ item.delivery_option?.label || '—' }}</span>
                </p>
                <button type="button" class="remove-btn" @click="removeItem(item)">
                  <span class="remove-text">Удалить</span>
                  <img :src="icon_trash" alt="Удалить" class="remove-icon" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="store.cartStore.cart.items.length" class="cart-summary">
          <div class="summary-block">
            <p class="summary-label">Стоимость:</p>
            <p class="summary-total">{{ formatPrice(store.cartStore.cart.total) }} ₽</p>
          </div>
          <p class="summary-note">Стоимость доставки рассчитывается при оформлении заказа</p>
        </div>

        <div class="cart-action" v-if="store.cartStore.cart.items.length">
          <button type="button" v-if="store.userStore.isTelegramUserId(store.userStore.user?.id)" class="action-button" @click="store.cartStore.checkout">
            Оформить заказ
          </button>
          <button type="button" v-else class="action-button" @click="onRegister">
            Зарегистрироваться
          </button>
        </div>

      </div>
    </div>
  </transition>
</template>

<script setup>
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'
import icon_trash from '@/assets/images/trash.svg'
import icon_close from '@/assets/images/close.svg'
import icon_minus_grey from '@/assets/images/minus_grey.svg'
import icon_plus_grey from '@/assets/images/plus_grey.svg'

const store = useStore()
const router = useRouter()

function removeItem(item) {
  const qty = store.cartStore.getProductQuantity(item)
  for (let i = 0; i < qty; i++) {
    store.cartStore.decreaseQuantity(item)
  }
}

function formatPrice(val) {
  return String(val).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

function onRegister() {
  if (store.tg && store.tg.open) {
    store.tg.open();
  } else {
    alert('Пожалуйста, авторизуйтесь');
  }
}

function goToCatalog() {
  store.cartStore.closeCartDrawer()
  store.productStore.selectedCategory = ''
  router.push({ name: 'Catalog' })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

</script>

<style scoped lang="scss">

.cart-drawer-overlay {
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
  position: fixed;
  inset: 0;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  z-index: 2000;
}

.cart-drawer {
  position: relative;
  height: 100vh;
  width: 100vw;
  background-color: $white-100;
  display: flex;
  flex-direction: column;
}

.cart-header {
  height: 86px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: $white-100;
  flex-shrink: 0;
}
.cart-header h2 {
  margin: 0;
  font-size: 32px;
  font-family: Bounded;
  font-weight: 250;
  line-height: 80%;
  letter-spacing: -1.6px;
}
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
}
.close-btn img {
  width: 24px;
  height: 24px;
}

.empty-cart {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  gap: 40px;
  color: $grey-20;
  font-size: 16px;
  line-height: 110%;
  letter-spacing: -0.64px;
}

.cart-items-frame {
  flex: 1;
  overflow-y: auto;
  padding: 10px 10px 0 20px;
  position: relative;
  line-height: 100%;
  letter-spacing: -0.04em;
  scrollbar-width: thin;
  scrollbar-color: $black-25 transparent;
}
.cart-items-frame::after {
  content: '';
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  height: 20px;
  background: linear-gradient(transparent, $black-10);
  pointer-events: none;
}
.cart-items-frame::-webkit-scrollbar {
  width: 6px;
}
.cart-items-frame::-webkit-scrollbar-track {
  background: transparent;
}
.cart-items-frame::-webkit-scrollbar-thumb {
  background-color: $black-40;
  border-radius: 3px;
}

.cart-item {
  display: flex;
  padding: 20px 0;
  border-top: 1px solid $grey-87;
}
.cart-item:last-child {
  border-bottom: 1px solid $grey-87;
}

.item-image-container {
  padding: 10px;
  width: 150px;
  height: 200px;
  background-color: $grey-95;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.item-image-container img {
  width: 100%;
  height: 100%;
}

.item-details {
  flex: 1;
  margin-left: 8px;
  display: flex;
  flex-direction: column;
}
.item-brand {
  font-size: 12px;
  color: $grey-20;
  margin: 0 0 8px;
  line-height: 100%;
  letter-spacing: -0.48px;
}
.item-title-price {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 24px;
}
.item-name {
  font-size: 15px;
  font-family: Manrope-SemiBold;
  margin: 0;
  color: $black-100;
  line-height: 100%;
  letter-spacing: -0.6px;
}
.item-price {
  font-size: 15px;
  font-family: Manrope-SemiBold;
  margin: 0;
  color: $black-100;
  line-height: 100%;
  letter-spacing: -0.6px;
}

.item-quantity-controls {
  display: flex;
  align-items: center;
  width: fit-content;
  background-color: $grey-95;
  border-radius: 4px;
}
.qty-btn {
  @include flex-c-c;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
.qty-btn img {
  width: 16px;
  height: 16px;
}
.qty {
  width: 24px;
  text-align: center;
  font-size: 16px;
  margin: 0 8px;
}

.item-info-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 80px;
  font-size: 12px;
}
.item-info {
  flex: 0 0 80%;
  font-size: 14px;
  color: $black-40;
  margin: 0;
}
.item-info-value {
  color: $grey-20;
}
.remove-btn {
  margin-left: auto;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  height: 24px;
}
.remove-text {
  display: inline-block;
  font-size: 12px;
  color: $black-40;
  border-bottom: 1px solid $black-40;
}
.remove-icon {
  display: none;
}

.cart-summary {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  flex-shrink: 0;
  padding: 0 20px 10px;
  background-color: $white-100;
}
.summary-block {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
.summary-label {
  font-size: 20px;
  margin: 18px 0 4px;
  color: $grey-20;
  line-height: 110%;
  letter-spacing: -0.4px;
}
.summary-total {
  font-size: 20px;
  font-family: Bounded;
  font-weight: 250;
  color: $black-100;
  margin: 18px 0 4px;
  line-height: 80%;
  letter-spacing: -1px;
}
.summary-note {
  font-size: 12px;
  color: $black-60;
  margin: 0 0 16px;
  line-height: 100%;
  letter-spacing: -0.48px;
}

.cart-action {
  padding: 0 20px 20px;
  background-color: $white-100;
  flex-shrink: 0;
}
.action-button {
  width: 100%;
  height: 72px;
  padding: 0 14px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: $grey-20;
  color: $white-100;
  line-height: 100%;
  letter-spacing: -0.64px;
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease, transform 0.3s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
.drawer-enter-to,
.drawer-leave-from {
  opacity: 1;
  transform: translateX(0);
}

@media (max-width: 600px) {
  .cart-header {
    padding: 0 10px;
  }
  .cart-items-frame {
    padding: 10px 0 10px 10px;
  }
  .item-title-price {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 24px;
    gap: 16px;
  }
  .item-info-row {
    margin-top: 28px;
  }
  .action-button {
    height: 56px;
  }
  .summary-label {
    font-size: 16px;
    letter-spacing: -0.64px;
  }
  .summary-total {
    font-family: Bounded;
    font-weight: 375;
    font-size: 16px;
    letter-spacing: -0.8px;
  }
  .item-image-container {
    padding: 5px;
    width: 134px;
    height: 178px;
  }
  .cart-summary {
    padding: 0 10px 10px;
  }
  .cart-action {
    padding: 0 10px 20px;
    background-color: $white-100;
    flex-shrink: 0;
  }
  .remove-text {
    display: none;
  }
  .remove-icon {
    display: inline-block;
    width: 24px;
    height: 24px;
  }
}

</style>
