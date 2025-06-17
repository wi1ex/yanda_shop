<template>
  <div class="cart-container">
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
            <span class="item-info">Размер: {{ item.size_label || 'one size' }}</span>
            <span class="item-info">Доставка: {{ item.delivery_time }}</span>
            <button class="remove-btn" @click="removeItem(item)">
              <img :src="icon_trash" alt="Удалить" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="store.cart.items.length" class="cart-summary">
      <div class="summary-text">
        <p class="summary-label">Стоимость:</p>
        <p class="summary-note">Стоимость доставки рассчитывается при оформлении заказа</p>
      </div>
      <p class="summary-total">{{ formatPrice(store.cart.total) }} ₽</p>
    </div>

    <!-- Checkout button -->
    <button v-if="store.cart.items.length" class="checkout-button" @click="store.checkout">
      Оформить заказ
    </button>
  </div>
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
</script>

<style scoped lang="scss">
.cart-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 86px;
  padding: 0 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #fff;
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
  padding-bottom: 100px; /* Чтобы последний элемент не перекрывался кнопкой */
  position: relative;
}
.cart-items-frame::after {
  content: '';
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  height: 20px;
  background: linear-gradient(transparent, rgba(0,0,0,0.05));
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
  padding: 4px;
}

.cart-summary {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0 16px;
  border-top: 1px solid #e0e0e0;
}
.summary-text {
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

/* Адаптив для мобильных */
@media (max-width: 600px) {
  .cart-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .item-image-container {
    margin-bottom: 8px;
  }
  .item-quantity-controls {
    width: 100%;
    justify-content: space-between;
    margin-top: 12px;
  }
  .checkout-button {
    width: calc(100% - 32px);
    padding: 16px;
  }
}
</style>
