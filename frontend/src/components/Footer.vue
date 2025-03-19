<template>
    <footer :style="footerStyle" class="footer">
        <div class="footer-content">
            <p>Магазин "Телеграм Магазин"</p>
            <p>Телефон: +7 (123) 456-78-90</p>
            <p>Email: info@example.com</p>
            <p>Адрес: г. Москва, ул. Примерная, д.1</p>
        </div>
    </footer>
</template>

<script setup>
import { computed } from 'vue';

const themeParams = (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.themeParams) || {
    bg_color: '#ffffff',
    text_color: '#000000',
}

const footerStyle = computed(() => ({
    backgroundColor: themeParams.bg_color,
    color: themeParams.text_color,
    padding: '20px',
    textAlign: 'center',
    borderTop: '1px solid #ccc',
}))
</script>

<style lang="scss" scoped>
.footer {
    margin-top: auto;
    .footer-content {
        p {
            margin: 5px 0;
        }
    }
}
</style>
