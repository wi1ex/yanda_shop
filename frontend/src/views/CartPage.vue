<template>
  <transition name="fade">
    <div class="cart-drawer-overlay" @click.self="store.closeCartDrawer()">
      <div class="cart-drawer">
        <!-- Header -->
        <div class="cart-header">
          <h2>Корзина [{{ store.cart.count }}]</h2>
          <button class="close-btn" @click="store.closeCartDrawer()">
            <img :src="icon_close" alt="Закрыть" />
          </button>
        </div>

        <!-- Empty state -->
        <div v-if="store.cart.items.length === 0" class="empty-cart">
          Корзина пуста
        </div>

        <!-- Items list -->
        <div v-else class="cart-items-frame">
          <div v-for="item in store.groupedCartItems" :key="item.variant_sku" class="cart-item">
            <div class="item-image-container">
              <img :src="item.image" alt="" />
            </div>
            <div class="item-details">
              <p class="item-brand">{{ item.brand }}</p>
              <p class="item-name">{{ item.name }}</p>
              <p class="item-price">{{ formatPrice(item.price) }} ₽</p>

              <div class="item-quantity-controls">
                <button class="qty-btn" @click="store.decreaseQuantity(item)">
                  <img :src="icon_minus" alt="Минус" />
                </button>
                <span class="qty">{{ item.quantity }}</span>
                <button class="qty-btn" @click="store.increaseQuantity(item)">
                  <img :src="icon_plus" alt="Плюс" />
                </button>
              </div>

              <div class="item-info-row">
                <span class="item-info">
                  Размер: {{ item.size_label || 'one size' }}
                </span>
                <span class="item-info">
                  Доставка: {{ item.delivery_time }}
                </span>
                <button class="remove-btn" @click="removeItem(item)">
                  <img :src="icon_trash" alt="Удалить" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div v-if="store.cart.items.length" class="cart-summary">
          <div class="summary-block">
            <p class="summary-label">Стоимость:</p>
            <p class="summary-note">Стоимость доставки рассчитывается при оформлении заказа</p>
          </div>
          <p class="summary-total">{{ formatPrice(store.cart.total) }} ₽</p>
        </div>

        <!-- Checkout button -->
        <div class="cart-action" v-if="store.cart.items.length">
          <button v-if="store.isTelegramUserId(store.user.id)" class="checkout-button" @click="store.checkout">
            Оформить заказ (очистить корзину)
          </button>
          <button v-else class="register-button" @click="onRegister">
            Зарегистрироваться
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { useStore } from '@/store/index.js'
import icon_trash from '@/assets/images/trash.svg'
import icon_close from '@/assets/images/close.svg'
import icon_minus from '@/assets/images/minus.svg'
import icon_plus from '@/assets/images/plus.svg'
const store = useStore()

function removeItem(item) {
  const qty = store.getProductQuantity(item)
  for (let i = 0; i < qty; i++) {
    store.decreaseQuantity(item)
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

</script>

<style scoped lang="scss">

.cart-drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
  z-index: 2000;
}

.cart-drawer {
  position: relative;
  height: 100vh;
  width: 100vw;
  max-width: 400px;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.cart-header {
  height: 86px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e0e0e0;
  background: #fff;
  flex-shrink: 0;
}
.cart-header h2 {
  font-size: 32px;
  font-weight: 500;
  margin: 0;
}
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}
.close-btn img {
  width: 24px;
  height: 24px;
}

.empty-cart {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  font-size: 16px;
}

.cart-items-frame {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  position: relative;
}
.cart-items-frame::after {
  content: '';
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  height: 20px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.1));
  pointer-events: none;
}

.cart-item {
  display: flex;
  margin-bottom: 16px;
}

.item-image-container {
  width: 80px;
  height: 80px;
  background: #f4f4f4;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.item-image-container img {
  max-width: 100%;
  max-height: 100%;
}

.item-details {
  flex: 1;
  margin-left: 12px;
  display: flex;
  flex-direction: column;
}

.item-brand {
  font-size: 12px;
  color: #858697;
  margin: 0;
}
.item-name {
  font-size: 16px;
  font-weight: 500;
  margin: 4px 0;
}
.item-price {
  font-size: 16px;
  font-weight: 500;
  margin: 4px 0 8px;
}

.item-quantity-controls {
  display: flex;
  align-items: center;
}
.qty-btn {
  width: 32px;
  height: 24px;
  background: #f4f4f4;
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
  align-items: center;
  margin-top: 8px;
}
.item-info {
  font-size: 12px;
  color: #858697;
  margin-right: 12px;
}
.remove-btn {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
}

.cart-summary {
  height: 170px;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-shrink: 0;
}
.summary-block {
  display: flex;
  flex-direction: column;
}
.summary-label {
  font-size: 24px;
  font-weight: 500;
  margin: 16px 0 4px;
}
.summary-note {
  font-size: 12px;
  color: #858697;
  margin: 0 0 16px;
}
.summary-total {
  font-size: 24px;
  font-weight: 500;
  margin: 16px;
}

.cart-action {
  padding: 0 16px 16px;
  background: #fff;
  flex-shrink: 0;
}
.register-button {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  background: #000;
  color: #fff;
}
.checkout-button {
  margin: 0 16px 16px;
  padding: 14px;
  background: #000;
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .cart-drawer {
    max-width: 100vw;
  }
}

</style>
