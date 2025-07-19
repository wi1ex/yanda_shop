<template>
  <div class="delivery-page">
    <h1 class="section-title">Доставка и оплата</h1>

    <!-- Доставка и оплата -->
    <div class="info-row">
      <!-- Доставка -->
      <div class="info-card">
        <h2 class="card-title">Доставка</h2>
        <p class="info-text">
          Доставка по РФ осуществляется через Яндекс.Доставку или СДЭК. При выборе способа доставки
          необходимо указать желаемый способ доставки и адрес: удобного для ПВЗ. В Москве и ближайшем
          Подмосковье есть возможность доставки курьером, если необходимо привезти сразу домой. В этом
          случае необходимо указать полный адрес в соответствующем выборе доставки.
        </p>
        <ul class="list">
          <li>Доставка курьером в пределах МКАД — до 800 ₽.</li>
          <li>Доставка курьером за МКАД — до 1500 ₽.</li>
        </ul>
        <p class="info-note">
          Стоимость доставки может измениться в зависимости от тарифов выбранных служб доставки и времени оформления.
        </p>
        <p class="info-warning">
          Внимание: любая доставка в день получения товара в Москве оплачивается отдельно.
        </p>
      </div>

      <!-- Способы оплаты -->
      <div class="info-card">
        <h2 class="card-title">Способы оплаты</h2>
        <div class="payment-box">
          <span>Оплата товара и доставки</span>
          <span class="icon">₽</span>
        </div>
        <p class="info-text small">
          Мы работаем по 100% предоплате. Это гарантирует для вас закрепление курса юаня и возможность
          покупки товара по той стоимости, которую вы увидели на сайте. Также вы сразу оплачиваете доставку
          до ПВЗ или домой, чтобы после у вас не было скрытых и дополнительных платежей.
        </p>
        <div class="payment-box">
          <span>Способы оплаты</span>
          <span class="icon">💳</span>
        </div>
        <p class="info-text small">
          После оформления заказа с вами свяжется менеджер и уточнит реквизиты, по которым необходимо
          произвести оплату. Оплата может осуществляться с помощью переводов и СБП.
        </p>
      </div>
    </div>

    <!-- Возврат -->
    <div class="info-row">
      <div class="info-card">
        <h2 class="card-title">Возврат</h2>
        <p class="info-text">
          Возврат товара возможен, только если вы получили не тот артикул, который заказывали изначально.
          При получении товара проверьте модель товара и размер, чтобы убедиться в правильности доставки.
        </p>
        <ul class="list">
          <li>Проверьте комплектность посылки;</li>
          <li>Убедитесь в отсутствии видимых механических повреждений товара (не распространяется на упаковку).</li>
        </ul>
      </div>
      <div class="info-card">
        <div class="info-note-block">
          <span class="icon">ℹ️</span>
          <p>Для возврата напишите нам письмо на
            <a v-if="store.parameters.url_social_email" :href="`mailto:${store.parameters.url_social_email}`"
               rel="noopener" class="link">{{ store.parameters.url_social_email }}</a>
            с темой «Возврат товара по заказу №» и пришлите факт несоответствия размера или модели.
          </p>
          <p>Мы обработаем запрос в течении 2-х часов и вернемся с дальнейшими шагами.</p>
        </div>
      </div>
    </div>

    <!-- Сколько ждать доставку? -->
    <h2 class="timeline-title">Сколько ждать доставку?</h2>
    <div class="timeline-grid">
      <div class="timeline-card highlight">
        <p class="highlight-text">Рекомендуем закладывать срок</p>
        <p class="highlight-period">~3 недели</p>
      </div>
      <div class="timeline-card">
        <h3 class="card-period">1 день</h3>
        <p class="card-desc">Выкуп с площадки</p>
      </div>
      <div class="timeline-card">
        <h3 class="card-period">2–3 дня</h3>
        <p class="card-desc">Доставка до нашего склада</p>
      </div>
      <div class="timeline-card">
        <h3 class="card-period">2–5 дней</h3>
        <p class="card-desc">Формирование заказов в один груз</p>
      </div>
      <div class="timeline-card">
        <h3 class="card-period">10–14 дней</h3>
        <p class="card-desc">Доставка до склада в Москве</p>
      </div>
      <div class="timeline-card">
        <h3 class="card-period">2–3 дня</h3>
        <p class="card-desc">Удобная доставка по Москве и регионам</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useStore } from '@/store/index.js'

const store = useStore()
</script>

<style lang="scss">
.delivery-page {
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
  .info-row {
    display: flex;
    gap: 32px;
    width: 100%;
    max-width: 1200px;
    margin-bottom: 48px;
    flex-wrap: wrap;
    .info-card {
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
      }
      .info-text {
        font-size: 16px;
        line-height: 140%;
        letter-spacing: -0.4px;
        margin-bottom: 16px;
        &.small {
          font-size: 14px;
          color: $black-60;
        }
      }
      .list {
        margin: 16px 0;
        padding-left: 20px;
        color: $black-100;
        li {
          margin-bottom: 8px;
        }
      }
      .info-note {
        margin-top: 16px;
        font-size: 14px;
        color: $black-60;
        background-color: $white-10;
        padding: 12px;
        border-radius: 4px;
      }
      .info-warning {
        margin-top: 16px;
        font-size: 14px;
        color: $red-error;
      }
      .payment-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: $grey-90;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 16px;
        .icon {
          font-size: 24px;
        }
      }
      .info-note-block {
        display: flex;
        gap: 16px;
        align-items: flex-start;
        background-color: $white-10;
        padding: 16px;
        border-radius: 4px;
        .icon {
          font-size: 20px;
          color: $red-active;
        }
        p {
          margin: 0 0 8px;
          font-size: 14px;
          line-height: 140%;
          a.link {
            color: $red-active;
            text-decoration: underline;
          }
        }
      }
    }
  }
  .timeline-title {
    margin: 40px 0 24px;
    font-family: Bounded-500;
    font-size: 28px;
    line-height: 110%;
    letter-spacing: -0.6px;
    text-align: center;
  }
  .timeline-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    width: 100%;
    max-width: 1200px;
    .timeline-card {
      background-color: $white-100;
      border-radius: 8px;
      padding: 16px;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      &.highlight {
        background-color: $black-100;
        color: $white-100;
        padding: 32px 16px;
        .highlight-text {
          font-size: 16px;
          line-height: 110%;
          letter-spacing: -0.4px;
          margin-bottom: 8px;
        }
        .highlight-period {
          font-family: Bounded-500;
          font-size: 24px;
          line-height: 110%;
          letter-spacing: -0.6px;
          color: $red-active;
        }
      }
      .card-period {
        margin: 0 0 8px;
        font-family: Bounded-500;
        font-size: 20px;
      }
      .card-desc {
        margin: 0;
        font-size: 14px;
        color: $black-60;
        line-height: 140%;
      }
    }
  }
}

@media (max-width: 768px) {
  .delivery-page {
    padding: 48px 16px;
    .section-title {
      font-size: 24px;
      margin-bottom: 24px;
    }
    .info-row {
      flex-direction: column;
      gap: 16px;
      .info-card {
        padding: 16px;
        .card-title {
          font-size: 24px;
          margin-bottom: 16px;
        }
      }
    }
    .timeline-title {
      font-size: 24px;
      margin: 24px 0 16px;
    }
    .timeline-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
