<template>
  <footer class="footer-content">
    <!-- === Верхняя часть футера WEB === -->
    <div class="footer-top-web">
      <div class="footer-top-column">
        <!-- Logo слева -->
        <div class="footer-logo">
          <img :src="icon_logo_text" alt="Главная" class="footer-logo-icon" @click.prevent="goToPage('Home')" />
        </div>

        <!-- Колонка “Категории” -->
        <nav class="footer-nav" style="left: 18vw">
          <a href="#" class="footer-link" @click.prevent="goToGender('M')">Мужчинам</a>
          <a href="#" class="footer-link" @click.prevent="goToGender('F')">Женщинам</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Аксессуары')">Аксессуары</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Одежда')">Одежда</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Обувь')">Обувь</a>
        </nav>

        <!-- Колонка “Информация” -->
        <nav class="footer-nav" style="left: 49.7vw">
          <a href="#" class="footer-link" @click.prevent="goToPage('About')">О нас</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Лайфстайл</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Доставка и оплата</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Возврат</a>
        </nav>

        <!-- Колонка “Соцсети” -->
        <nav class="footer-nav" style="left: 81.5vw">
          <a v-if="store.parameters.url_telegram" :href="store.parameters.url_telegram"
             target="_blank" rel="noopener" class="footer-link">Telegram</a>
          <a v-if="store.parameters.url_instagram" :href="store.parameters.url_instagram"
             target="_blank" rel="noopener" class="footer-link">Instagram</a>
          <a v-if="store.parameters.url_email" :href="`mailto:${store.parameters.url_email}`"
             rel="noopener" class="footer-link">Mail</a>
        </nav>
      </div>
    </div>

    <!-- === Верхняя часть футера MOBILE === -->
    <div class="footer-top-mobile">
      <div class="footer-top-column">
        <!-- Logo слева -->
        <div class="footer-logo">
          <img :src="icon_logo_text" alt="Главная" class="footer-logo-icon" @click.prevent="goToPage('Home')" />
        </div>

        <!-- Колонка “Категории” -->
        <nav class="footer-nav">
          <a href="#" class="footer-link" @click.prevent="goToGender('M')">Мужчинам</a>
          <a href="#" class="footer-link" @click.prevent="goToGender('F')">Женщинам</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Аксессуары')">Аксессуары</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Одежда')">Одежда</a>
          <a href="#" class="footer-link" @click.prevent="goToCategory('Обувь')">Обувь</a>
        </nav>
      </div>

      <div class="footer-top-column">
        <!-- Колонка “Информация” -->
        <nav class="footer-nav">
          <a href="#" class="footer-link" @click.prevent="goToPage('About')">О нас</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Лайфстайл</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Доставка и оплата</a>
          <a href="#" class="footer-link" @click.prevent="goToPage('Home')">Возврат</a>
        </nav>

        <!-- Колонка “Соцсети” -->
        <nav class="footer-nav">
          <a v-if="store.parameters.url_telegram" :href="store.parameters.url_telegram"
             target="_blank" rel="noopener" class="footer-link">Telegram</a>
          <a v-if="store.parameters.url_instagram" :href="store.parameters.url_instagram"
             target="_blank" rel="noopener" class="footer-link">Instagram</a>
          <a v-if="store.parameters.url_email" :href="`mailto:${store.parameters.url_email}`"
             rel="noopener" class="footer-link">Mail</a>
        </nav>
      </div>
    </div>

    <div class="logo-icon-div">
      <img :src="icon_logo_orange" alt="Главная" class="logo-icon" />
    </div>

    <!-- === Нижняя часть футера для desktop: крупные цифры + подписи === -->
    <div class="footer-bottom-web">
      <img :src="icon_logo_2025" alt="Лого 2025" class="big-digit" />
      <div class="footer-bottom-column">
        <div class="bottom-cell">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Договор публичной оферты</a>
        </div>
        <div class="bottom-cell" style="left: 18vw">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Политика конфиденциальности</a>
        </div>
        <div class="bottom-cell" style="left: 49.7vw">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Политика возврата и обмена</a>
        </div>
        <div class="bottom-cell" style="left: 81.5vw">
          <a href="#" class="bottom-link" @click.prevent="goToPage('Home')">Условия оплаты и доставки</a>
        </div>
      </div>
    </div>

    <!-- === Нижняя часть футера для мобильных (<600px): две колонки ссылок === -->
    <div class="footer-bottom-mobile">
      <img :src="icon_logo_2025" alt="Лого 2025" class="big-digit" />
      <div class="footer-bottom-row">
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
    </div>
  </footer>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '@/store/index.js'

import icon_logo_orange from '@/assets/images/logo_orange.svg'
import icon_logo_text from '@/assets/images/logo_text.svg'
import icon_logo_2025 from '@/assets/images/logo_2025.svg'

const store = useStore()
const route = useRoute()
const router = useRouter()

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

function goToGender(gender) {
  store.selectedCategory = ''
  store.filterGender = gender
  router.push({
    name:  'Catalog',
    query: { gender }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

</script>

<style scoped lang="scss">
.footer-content {
  display: flex;
  flex-direction: column;
  padding: 24px 10px;
  width: calc(100% - 20px);
  color: $black-100;
}

/* === Верхний грид WEB === */
.footer-top-web {
  display: flex;
  width: 100%;
}
/* === Верхний грид MOBILE === */
.footer-top-mobile {
  display: none;
  width: 100%;
}

.footer-top-column {
  display: flex;
}

.footer-logo {
  display: flex;
}
.footer-logo-icon {
  width: 167px;
  height: 17px;
  cursor: pointer;
}

.footer-nav {
  display: flex;
  flex-direction: column;
  position: absolute;
  gap: 4px;
}

.footer-link {
  width: fit-content;
  text-decoration: none;
  color: inherit;
  font-size: 20px;
  line-height: 100%;
  letter-spacing: -0.8px;
}

.logo-icon-div {
  display: flex;
  align-self: center;
  margin: 80px 0;
}
.logo-icon {
  width: 58px;
  height: 50px;
  cursor: default;
}

/* === Нижний грид WEB === */
.footer-bottom-web {
  display: flex;
  flex-direction: column;
  width: 100%;
}
/* === Нижний блок MOBILE === */
.footer-bottom-mobile {
  display: none;
  flex-direction: column;
  width: 100%;
}

.footer-bottom-row {
  display: flex;
  gap: 10px;
}

.footer-bottom-column {
  display: flex;
}

.bottom-cell {
  display: flex;
  position: absolute;
}
.bottom-link {
  text-decoration: none;
  color: inherit;
  font-size: 20px;
  line-height: 100%;
  letter-spacing: -0.8px;
}

.big-digit {
  width: 100%;
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


  .footer-bottom-column {
    display: flex;
    flex-direction: column;
    width: 50%;
    gap: 8px;
  }
  .bottom-cell {
    position: relative;
  }
  .bottom-link {
    font-size: 16px;
    letter-spacing: -0.64px;
  }
  .footer-logo {
    margin-left: -6px;
  }
  .footer-logo-icon {
    width: 130px;
    height: 13px;
  }
  .footer-nav {
    position: relative;
    gap: 8px;
  }
  .footer-link {
    font-size: 16px;
    letter-spacing: -0.64px;
  }
  .footer-top-column {
    flex-direction: column;
    width: 50%;
    gap: 40px;
  }
  .logo-icon-div {
    margin: 60px 0;
  }
  .big-digit {
    margin-bottom: 16px;
  }
}
</style>
