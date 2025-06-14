<template>
  <footer class="footer-content">
    <div class="footer-columns">
      <!-- Первая колонка -->
      <div class="column">
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">О нас</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Лайфстайл</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Доставка и оплата</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Возврат</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Telegram</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">WhatsApp</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Instagram</a>
      </div>
      <!-- Вторая колонка -->
      <div class="column">
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Договор публичной оферты</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Политика конфиденциальности</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Политика возврата и обмена</a>
        <a href="#" class="footer-link" @click.prevent="goHomeOrScroll">Условия оплаты и доставки</a>
      </div>
    </div>
    <!-- Логотип и © -->
    <div class="footer-bottom">
      <!-- здесь можно вставить логотип вместо текста -->
      <div class="logo">YANDA.SHOP</div>
      <div class="copyright">©2025</div>
    </div>
  </footer>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

function goHomeOrScroll() {
  if (route.name === 'Home') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    router.push({ name: 'Home' })
  }
}
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
.footer-columns {
  display: flex;
  width: 100%;
  max-width: 480px;
  margin-bottom: 16px;
}
.column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.footer-link {
  color: inherit;
  text-decoration: none;
  font-size: 14px;
  transition: opacity 0.2s;
}
.footer-link:hover {
  opacity: 0.7;
}
.footer-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.logo {
  font-weight: bold;
  font-size: 16px;
}
.copyright {
  font-size: 12px;
}

@media (max-width: 600px) {
  .footer-columns {
    flex-direction: column;
    align-items: center;
  }
  .column {
    align-items: center;
  }
}

</style>
