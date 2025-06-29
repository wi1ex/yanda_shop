<template>
  <footer class="footer-content">
    <!-- === Верхняя часть футера WEB === -->
    <div class="footer-top-web">
      <!-- Logo слева -->
      <div class="footer-logo">
        <a href="#" class="footer-logo-link" @click.prevent="goToPage('Home')">YANDA.SHOP</a>
      </div>

      <!-- Колонка “Категории” -->
      <nav class="footer-nav">
        <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Мужчинам</a>
        <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Женщинам</a>
        <a href="#" class="footer-link" @click.prevent="goToCategory('Аксессуары')">Аксессуары</a>
        <a href="#" class="footer-link" @click.prevent="goToCategory('Одежда')">Одежда</a>
        <a href="#" class="footer-link" @click.prevent="goToCategory('Обувь')">Обувь</a>
      </nav>

      <!-- Колонка “Информация” -->
      <nav class="footer-nav">
        <a href="#" class="footer-link" @click.prevent="goToPage('About')">О нас</a>
        <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Доставка и оплата</a>
        <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Возврат</a>
      </nav>

      <!-- Колонка “Соцсети” -->
      <nav class="footer-nav">
        <a v-if="store.socialUrls.url_telegram" :href="store.socialUrls.url_telegram"
           target="_blank" rel="noopener" class="footer-link">Telegram</a>
        <a v-if="store.socialUrls.url_instagram" :href="store.socialUrls.url_instagram"
           target="_blank" rel="noopener" class="footer-link">Instagram</a>
      </nav>
    </div>

    <!-- === Верхняя часть футера MOBILE === -->
    <div class="footer-top-mobile">
      <div class="footer-top-column">
        <!-- Logo слева -->
        <div class="footer-logo">
          <a href="#" class="footer-logo-link" @click.prevent="goToPage('Home')">YANDA.SHOP</a>
        </div>

        <!-- Колонка “Категории” -->
        <nav class="footer-nav">
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Мужчинам</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Женщинам</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Аксессуары')">Аксессуары</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Одежда')">Одежда</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Обувь')">Обувь</a>
        </nav>
      </div>

      <div class="footer-top-column">
        <!-- Колонка “Информация” -->
        <nav class="footer-nav">
          <a href="#" class="footer-link" @click.prevent="goToPage('About')">О нас</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Доставка и оплата</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Возврат</a>
        </nav>

        <!-- Колонка “Соцсети” -->
        <nav class="footer-nav">
          <a v-if="store.socialUrls.url_telegram" :href="store.socialUrls.url_telegram"
             target="_blank" rel="noopener" class="footer-link">Telegram</a>
          <a v-if="store.socialUrls.url_instagram" :href="store.socialUrls.url_instagram"
             target="_blank" rel="noopener" class="footer-link">Instagram</a>
        </nav>
      </div>
    </div>

    <router-link to="/">
      <img :src="icon_logo_orange" alt="Главная" class="logo-icon" />
    </router-link>

    <!-- === Нижняя часть футера для desktop: крупные цифры + подписи === -->
    <div class="footer-bottom-web">
      <span class="big-digit">©2025</span>
      <div class="footer-bottom-column">
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Договор публичной оферты</a>
        </div>
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Политика конфиденциальности</a>
        </div>
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Политика возврата и обмена</a>
        </div>
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Условия оплаты и доставки</a>
        </div>
      </div>
    </div>

    <!-- === Нижняя часть футера для мобильных (<600px): две колонки ссылок === -->
    <div class="footer-bottom-mobile">
      <span class="big-digit">©2025</span>
      <div class="footer-bottom-column">
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Договор публичной оферты</a>
        </div>
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Политика конфиденциальности</a>
        </div>
      </div>
      <div class="footer-bottom-column">
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Политика возврата и обмена</a>
        </div>
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Условия оплаты и доставки</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '@/store/index.js'

import icon_logo_orange from '@/assets/images/logo_orange.svg'

const store = useStore()
const router = useRouter()
const route = useRoute()

function goToPage(page) {
  if (route.name !== page) {
    router.push({ name: page })
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToCategory(cat) {
  store.changeCategory(cat)
  goToPage('Catalog')
}

onMounted(() => {
  store.loadSocialUrls()
})
</script>

<style scoped lang="scss">
.footer-content {
  display: flex;
  flex-direction: column;
  padding: 24px 10px;
  width: calc(100% - 20px);
}

/* === Верхний грид WEB === */
.footer-top-web {
  display: flex;
  align-items: start;
  width: 100%;
  max-width: 1200px;
  margin-bottom: 40px;
}
/* === Верхний грид MOBILE === */
.footer-top-mobile {
  display: none;
  align-items: start;
  width: 100%;
  max-width: 1200px;
  margin-bottom: 40px;
}

.footer-top-column {
  display: flex;
}

.footer-logo-link {
  font-size: 18px;
  font-weight: bold;
  text-decoration: none;
  color: inherit;
}

.footer-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-link {
  font-size: 14px;
  text-decoration: none;
  color: inherit;
  transition: opacity 0.2s;
  &:hover { opacity: 0.6; }
}

.logo-icon {
  width: 58px;
  height: 50px;
}

/* === Нижний грид WEB === */
.footer-bottom-web {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 1200px;
}
/* === Нижний блок MOBILE === */
.footer-bottom-mobile {
  display: none;
  width: 100%;
  max-width: 480px;
  margin-top: 24px;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.footer-bottom-column {
  display: flex;
}

.bottom-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
  .bottom-link {
    margin-top: -24px;
    font-size: 14px;
    text-decoration: none;
    color: inherit;
    text-align: center;
    &:hover { opacity: 0.6; }
  }
}

.big-digit {
  font-family: Bounded-250;
  font-size: 524px;
  line-height: 80%;
  letter-spacing: -26.2px;
}

/* === Адаптив === */
@media (max-width: 600px) {
  .footer-top-web {
    display: none;
  }
  .footer-top-mobile {
    display: flex;
  }
  .footer-bottom-web {
    display: none;
  }
  .footer-bottom-mobile {
    display: flex;
  }
}
</style>
