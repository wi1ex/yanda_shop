<template>
    <div v-if="user">
        <Header :user="user" :cartCount="cartCount" />
        <Navigation />
        <ProductGrid @update-cart="updateCart" />
        <Footer />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Header from './components/Header.vue';
import Navigation from './components/Navigation.vue';
import ProductGrid from './components/ProductGrid.vue';
import Footer from './components/Footer.vue';

const tg = ref(null);
const user = ref(null);
const cartCount = ref(0);

// Функция для накопления количества товаров в корзине
function updateCart(count) {
    cartCount.value += count;
}

onMounted(() => {
    // Если приложение запущено внутри Telegram, получаем данные пользователя
    if (window.Telegram && window.Telegram.WebApp) {
        tg.value = window.Telegram.WebApp;
        const initDataUnsafe = tg.value.initDataUnsafe
        if (initDataUnsafe && initDataUnsafe.user) {
            user.value = initDataUnsafe.user;
        }
    }
    if (user.value) {
        fetch("https://tgtest.twc1.net/save_user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id: user.value.id,
                first_name: user.value.first_name,
                last_name: user.value.last_name,
                username: user.value.username,
            })
        })
        .then(response => response.json())
        .then(data => console.log("Ответ сервера:", data));
    }
});
</script>

<style>
body {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    font-family: Arial, sans-serif;
}
</style>
