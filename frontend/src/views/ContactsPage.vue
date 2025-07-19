<template>
  <div class="contacts-page">
    <h1 class="section-title">Контакты для связи</h1>
    <div class="contacts-cards">
      <div class="card">
        <h2 class="card-title">Вопросы по заказам</h2>
        <p class="card-item">
          <span>Телеграм:</span>
          <a v-if="store.parameters.url_social_telegram_user1"
             :href="store.parameters.url_social_telegram_user1" target="_blank" rel="noopener" class="link">
            @{{ store.parameters.url_social_telegram_user1.split('/').pop() }}
          </a>
        </p>
        <p class="card-item">
          <span>E-mail:</span>
          <a v-if="store.parameters.url_social_email"
             :href="`mailto:${store.parameters.url_social_email}`" rel="noopener" class="link">
            {{ store.parameters.url_social_email }}
          </a>
        </p>
        <p class="card-note">
          Подпишитесь на наш телеграм-канал, там вся самая свежая информация о товарах и акциях
        </p>
      </div>
      <div class="card">
        <h2 class="card-title">Остальные вопросы</h2>
        <p class="card-item">
          <span>Телеграм:</span>
          <a v-if="store.parameters.url_social_telegram_user2" :href="store.parameters.url_social_telegram_user2" target="_blank" rel="noopener" class="link">
            @{{ store.parameters.url_social_telegram_user2.split('/').pop() }}
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useStore } from '@/store/index.js'

const store = useStore()
</script>

<style lang="scss">
.contacts-page {
  width: 100%;
  padding: 80px 32px;
  background-color: $grey-95;
  color: $black-100;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  .section-title {
    margin-bottom: 40px;
    font-family: Bounded-500;
    font-size: 32px;
    line-height: 90%;
    letter-spacing: -0.72px;
    text-align: center;
  }
  .contacts-cards {
    display: flex;
    gap: 32px;
    width: 100%;
    max-width: 1200px;
    .card {
      flex: 1;
      min-width: 300px;
      background-color: $white-100;
      border-radius: 8px;
      padding: 32px;
      box-sizing: border-box;
      .card-title {
        margin: 0 0 24px;
        font-family: Bounded-500;
        font-size: 28px;
        line-height: 110%;
        letter-spacing: -0.6px;
        color: $black-100;
      }
      .card-item {
        margin: 8px 0;
        font-size: 16px;
        line-height: 110%;
        letter-spacing: -0.64px;
        span {
          margin-right: 8px;
          color: $black-60;
        }
      }
      .link {
        color: $red-active;
        text-decoration: underline;
      }
      .card-note {
        margin-top: 24px;
        font-size: 14px;
        line-height: 120%;
        color: $black-60;
      }
    }
  }
}

@media (max-width: 768px) {
  .contacts-page {
    padding: 48px 16px;
    .section-title {
      font-size: 24px;
      margin-bottom: 24px;
    }
    .contacts-cards {
      flex-direction: column;
      gap: 16px;
      .card {
        padding: 16px;
        .card-title {
          font-size: 24px;
          margin-bottom: 16px;
        }
      }
    }
  }
}
</style>
