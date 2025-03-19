<template>
  <header :style="headerStyle" class="header">
    <div class="user-info">
      <img :src="user.photo_url" alt="User Avatar" class="avatar" />
      <div class="user-details">
        <div class="name">{{ user.first_name }} {{ user.last_name }}</div>
        <div class="username">@{{ user.username }}</div>
      </div>
    </div>
    <div class="cart" @click="goToCart">
      <!-- Для иконки корзины можно использовать FontAwesome или другой набор иконок -->
      <i class="fas fa-shopping-cart"></i>
      <span class="cart-count" v-if="cartCount > 0">{{ cartCount }}</span>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    user: {
        type: Object,
        required: true,
    },
    cartCount: {
        type: Number,
        default: 0,
    }
})

// Используем тему Telegram, если доступна, для стилей
const themeParams = (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.themeParams) || {
    bg_color: '#ffffff',
    text_color: '#000000',
}

const headerStyle = computed(() => ({
    backgroundColor: themeParams.bg_color,
    color: themeParams.text_color,
    padding: '10px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottom: '1px solid #ccc',
}))

function goToCart() {
    // Здесь можно реализовать переход к странице корзины или открыть модальное окно
    alert('Переход к корзине');
}
</script>

<style lang="scss" scoped>
.header {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    .user-info {
        display: flex;
        align-items: center;
        .avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 10px;
        }
        .user-details {
            display: flex;
            flex-direction: column;
            .name {
                font-weight: bold;
                font-size: 1.1em;
            }
            .username {
                font-size: 0.9em;
                color: #666;
            }
        }
    }
    .cart {
        position: relative;
        cursor: pointer;
        font-size: 1.5em;
        .cart-count {
            position: absolute;
            top: -5px;
            right: -10px;
            background: red;
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 0.8em;
        }
    }
}
</style>
