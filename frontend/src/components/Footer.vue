<template>
  <footer class="footer-content">
    <!-- === Верхняя часть футера: логотип + навигация + соцсети === -->
    <div class="footer-top">
      <!-- Logo слева -->
      <div class="footer-logo">
        <a href="#" class="footer-logo-link" @click.prevent="goHomeOrScroll">YANDA.SHOP</a>
      </div>

      <!-- Колонка “Категории” -->
      <nav class="footer-nav">
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Мужчинам</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Женщинам</a>
        <a href="#" class="footer-link" @click.prevent="goToCategory('Аксессуары')">Аксессуары</a>
        <a href="#" class="footer-link" @click.prevent="goToCategory('Одежда')">Одежда</a>
        <a href="#" class="footer-link" @click.prevent="goToCategory('Обувь')">Обувь</a>
      </nav>

      <!-- Колонка “Информация” -->
      <nav class="footer-nav">
        <router-link to="/about" class="footer-link">О нас</router-link>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Доставка и оплата</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Возврат</a>
      </nav>

      <!-- Колонка “Соцсети” -->
      <nav class="footer-nav">
        <a v-if="store.socialUrls.url_telegram" :href="store.socialUrls.url_telegram"
           target="_blank" rel="noopener" class="footer-link">Telegram</a>
        <a v-if="store.socialUrls.url_instagram" :href="store.socialUrls.url_instagram"
           target="_blank" rel="noopener" class="footer-link">Instagram</a>
      </nav>
    </div>

    <!-- === Нижняя часть футера для desktop: крупные цифры + подписи === -->
    <div class="footer-bottom-grid">
      <div class="bottom-cell">
        <span class="big-digit">©</span>
        <a href="#" class="bottom-link" @click.prevent="goHomeOrScroll">Договор публичной оферты</a>
      </div>
      <div class="bottom-cell">
        <span class="big-digit">2</span>
        <a href="#" class="bottom-link" @click.prevent="goHomeOrScroll">Политика конфиденциальности</a>
      </div>
      <div class="bottom-cell">
        <span class="big-digit">0</span>
        <a href="#" class="bottom-link" @click.prevent="goHomeOrScroll">Политика возврата и обмена</a>
      </div>
      <div class="bottom-cell">
        <span class="big-digit">2</span>
        <a href="#" class="bottom-link" @click.prevent="goHomeOrScroll">Условия оплаты и доставки</a>
      </div>
      <div class="bottom-cell">
        <span class="big-digit">5</span>
      </div>
    </div>

    <!-- === Нижняя часть футера для мобильных (<600px): две колонки ссылок === -->
    <div class="footer-bottom-mobile">
      <div class="mobile-group">
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Договор публичной оферты</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Политика конфиденциальности</a>
      </div>
      <div class="mobile-group">
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Политика возврата и обмена</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Условия оплаты и доставки</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '@/store/index.js'

const store = useStore()
const router = useRouter()
const route = useRoute()

function goToCategory(cat) {
  store.changeCategory(cat)
  if (route.name === 'Catalog') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    router.push({ name: 'Catalog' })
  }
}

function goHomeOrScroll() {
  if (route.name === 'Home') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    router.push({ name: 'Home' })
  }
}

onMounted(() => {
  store.loadSocialUrls()
})
</script>

<style scoped lang="scss">
.footer-content {
  background: #f0f0f0;
  color: #000;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* === Верхний грид === */
.footer-top {
  display: grid;
  grid-template-columns: auto 1fr 1fr 1fr auto;
  align-items: start;
  column-gap: 32px;
  width: 100%;
  max-width: 1200px;
  margin-bottom: 40px;
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

/* === Нижний грид для desktop === */
.footer-bottom-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  align-items: center;
  width: 100%;
  max-width: 1200px;
}

.bottom-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
  .big-digit {
    font-size: 200px;
    line-height: 1;
    margin: 0;
    display: block;
  }
  .bottom-link {
    margin-top: -24px;
    font-size: 14px;
    text-decoration: none;
    color: inherit;
    text-align: center;
    &:hover { opacity: 0.6; }
  }
}

/* === Нижний блок для mobile (<600px) === */
.footer-bottom-mobile {
  display: none;
  width: 100%;
  max-width: 480px;
  margin-top: 24px;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.mobile-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* === Адаптив === */
@media (max-width: 600px) {
  .footer-top {
    grid-template-columns: 1fr;
    row-gap: 24px;
    justify-items: center;
    text-align: center;
  }
  .footer-bottom-grid {
    display: none;
  }
  .footer-bottom-mobile {
    display: grid;
  }
}
</style>
