<template>
    <nav :style="navStyle" class="navigation">
        <ul>
            <li><a href="#" @click.prevent="navigate('home')">Главная</a></li>
            <li><a href="#" @click.prevent="navigate('catalog')">Каталог</a></li>
            <li><a href="#" @click.prevent="navigate('orders')">Заказы</a></li>
            <li><a href="#" @click.prevent="navigate('contacts')">Контакты</a></li>
        </ul>
    </nav>
</template>

<script setup>
import { computed } from 'vue';

const themeParams = (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.themeParams) || {
    button_color: '#0088cc',
    text_color: '#000000',
}

const navStyle = computed(() => ({
    backgroundColor: themeParams.button_color,
    color: '#fff',
    padding: '10px 20px',
}))

function navigate(page) {
    // Здесь можно реализовать логику перехода или смены состояния страницы
    alert('Навигация к ' + page);
}
</script>

<style lang="scss" scoped>
.navigation {
    ul {
        list-style: none;
        display: flex;
        gap: 15px;
        margin: 0;
        padding: 0;
        li {
            a {
                color: #fff;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
        }
    }
}
</style>
