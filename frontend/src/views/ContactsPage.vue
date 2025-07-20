<template>
  <div class="contacts-page">
    <h1 class="section-title">Контакты для связи</h1>
    <div class="contacts-cards">
      <div class="card">
        <h2 class="card-title">Вопросы по заказам</h2>
        <div class="card-div">
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
        </div>
        <p class="card-note">
          Подпишитесь на
          <a v-if="store.parameters.url_social_telegram" :href="store.parameters.url_social_telegram"
             target="_blank" rel="noopener" class="black-link">наш телеграм-канал</a>
          , там вся самая свежая информация о товарах и акциях
        </p>
      </div>
      <div class="card">
        <h2 class="card-title">Остальные вопросы</h2>
        <div class="card-div">
          <p class="card-item">
            <span>Телеграм:</span>
            <a v-if="store.parameters.url_social_telegram_user2" :href="store.parameters.url_social_telegram_user2" target="_blank" rel="noopener" class="link">
              @{{ store.parameters.url_social_telegram_user2.split('/').pop() }}
            </a>
          </p>
        </div>
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
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  .section-title {
    margin: 96px 0 40px;
    color: $black-100;
    font-family: Bounded-400;
    font-size: 64px;
    line-height: 90%;
    letter-spacing: -5.12px;
  }
  .contacts-cards {
    display: flex;
    width: 100%;
    .card {
      display: flex;
      flex-direction: column;
      margin-top: 10px;
      padding: 20px 10px;
      gap: 40px;
      background-color: $white-100;
      border-radius: 4px;
      .card-title {
        margin: 0;
        color: $black-100;
        font-family: Bounded-250;
        font-size: 32px;
        line-height: 80%;
        letter-spacing: -1.6px;
      }
      .card-div {
        display: flex;
        flex-direction: column;
        gap: 8px;
        .card-item {
          display: flex;
          align-items: center;
          margin: 0;
          span {
            margin-right: 4px;
            color: $grey-20;
            font-size: 16px;
            line-height: 110%;
            letter-spacing: -0.64px;
          }
          .link {
            color: $red-active;
            font-family: Bounded-350;
            font-size: 16px;
            line-height: 80%;
            letter-spacing: -0.8px;
            text-decoration: none;
          }
        }
      }
      .card-note {
        color: $grey-20;
        font-size: 14px;
        line-height: 100%;
        letter-spacing: -0.56px;
        .black-link {
          color: inherit;
          text-decoration: underline;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .contacts-page {
    .section-title {
      font-size: 32px;
      letter-spacing: -2.24px;
    }
    .contacts-cards {
      flex-direction: column;
      .card {
        gap: 24px;
        .card-title {
          font-size: 24px;
          letter-spacing: -1.2px;
        }
        .card-div {
          gap: 8px;
          .card-item {
            span {
              font-size: 15px;
              letter-spacing: -0.6px;
            }
            .link {
              font-size: 14px;
              letter-spacing: -0.7px;
            }
          }
        }
      }
    }
  }
}
</style>
