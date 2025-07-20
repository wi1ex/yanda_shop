<template>
  <div class="delivery-page">
    <div class="line-vert"></div>
    <h1 class="section-title">Доставка и оплата</h1>
    <div class="line-hor"></div>
    <div class="info-row">
      <!-- Доставка -->
      <div class="info-card">
        <h2 class="card-title">Доставка</h2>
        <p class="info-text">
          Доставка по РФ осуществляется через Яндекс.Доставку или СДЭК.
          <span class="info-text small">
            При выборе способа доставки необходимо указать желаемый способ доставки и адрес удобного для вас ПВЗ.
            В Москве и ближайшем Подмосковье есть возможность доставки курьером, если необходимо привезти сразу домой.
            В этом случае необходимо указать личный адрес в соответствующем выборе доставки.
          </span>
        </p>
        <ul class="list">
          <li>Доставка курьером в пределах МКАД —  до 800 ₽</li>
          <li>Доставка курьером за МКАД — до 1 500 ₽</li>
        </ul>
        <p class="info-note-div">
          <img :src="icon_info" alt=""/>
          <p class="info-note">
            Стоимость доставки может измениться в зависимости от тарифов выбранных служб доставки и времени оформления.
          </p>
        </p>
        <p class="info-warning">
          Внимание: любая доставка в день получения товара в Москве оплачивается отдельно.
        </p>
      </div>

      <!-- Способы оплаты -->
      <div class="info-card">
        <h2 class="card-title">Способы оплаты</h2>
        <div class="payment-box" style="margin-bottom: 24px;">
          <span>Оплата товара и доставки</span>
          <img :src="icon_ruble" alt=""/>
          <p class="info-text small">
            Мы работаем по 100% предоплате. Это гарантирует для вас закрепление курса юаня и возможность покупки товара по той стоимости, которую вы увидели на сайте.
            Также вы сразу оплачиваете доставку до ПВЗ или домой, чтобы после у вас не было скрытых и дополнительных платежей.
          </p>
        </div>
        <div class="payment-box">
          <span>Способы оплаты</span>
          <img :src="icon_card" alt=""/>
          <p class="info-text small">
            Посла оформления заказа с вами свяжется менеджер и уточнит реквизиты, по которым необходимо произвести оплату.
            Оплата может осуществляться с помощью переводов и СБП.
          </p>
        </div>
      </div>

      <!-- Возврат -->
      <div class="info-card">
        <h2 class="card-title">Возврат</h2>
        <p class="info-text default">
          Возврат товара возможен, только если вы получили не тот артикул, который заказывали изначально.
          При получении товара проверьте модель товара и размер, чтобы убедиться в правильности доставки.
        </p>
        <ul class="list">
          <li>Проверьте комплектность посылки</li>
          <li>Убедитесь в отсутствии видимых механических повреждений товара (не распространяется на упаковку)</li>
        </ul>
        <div class="info-note-block">
          <img :src="icon_info" alt=""/>
          <p>Для возврата напиши нам письмо на
            <a v-if="store.parameters.url_social_email" :href="`mailto:${store.parameters.url_social_email}`"
               rel="noopener" class="link">{{ store.parameters.url_social_email }}</a>
            с темой
            <span class="link">«Возврат товара по заказу №»</span>
            и пришли факт несовпадения размера или модели.<br><br>
            Мы обработаем запрос в в течении 2-х часов и вернемся с дальнейшими шагами.
          </p>
        </div>
      </div>
    </div>

    <!-- Сколько ждать доставку? -->
    <div class="timeline-div">
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
          <h3 class="card-period">2 - 3 дня</h3>
          <p class="card-desc">Доставка до нашего склада </p>
        </div>
        <div class="timeline-card">
          <h3 class="card-period">2 - 5 дней</h3>
          <p class="card-desc">Формирование заказов в один груз</p>
        </div>
        <div class="timeline-card">
          <h3 class="card-period">10 - 14 дней</h3>
          <p class="card-desc">Доставка до склада в Москве</p>
        </div>
        <div class="timeline-card">
          <h3 class="card-period">2 - 3 дня</h3>
          <p class="card-desc">Удобная для вас доставка по Москве и другим регионам</p>
        </div>
      </div>
    </div>

    <!-- FAQ -->
    <div class="faq">
      <h2 class="faq-title">FAQ</h2>
      <p class="faq-subtitle">
        Здесь ты найдёшь ответы на самые популярные вопросы о заказах, доставке, оплате и возврате. Мы собрали всю важную информацию, чтобы сделать
        твои покупки максимально простыми и прозрачными.
      </p>

      <div class="faq-list">
        <div v-for="item in faqItems" :key="item.id" class="faq-item" @click="toggleFaq(item.id)">
          <div class="faq-number">{{ String(item.id).padStart(2, '0') }}</div>
          <div class="faq-header">
            <div class="faq-question">{{ item.question }}</div>
            <div class="faq-toggle-icon" :class="{ open: openedFaq === item.id }">
              <img :src="openedFaq === item.id ? icon_minus_red : icon_faq_plus" alt="toggle" class="faq-icon"/>
            </div>
          </div>
          <transition name="faq-slide">
            <div v-if="openedFaq === item.id" class="faq-answer">
              {{ item.answer }}
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
  <div class="line-hor"></div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from '@/store/index.js'
import icon_info from '@/assets/images/info.svg'
import icon_card from '@/assets/images/card.svg'
import icon_ruble from '@/assets/images/ruble.svg'
import icon_minus_red from "@/assets/images/minus_red.svg";
import icon_faq_plus from "@/assets/images/faq_plus.svg";

const store = useStore()
const openedFaq = ref(null);

const faqItems = computed(() => {
  const items = []
  const allKeys = Object.keys(store.parameters)
  const faqNumbers = [ ...new Set(allKeys
      .filter(key => key.startsWith('faq_delivery_question_') || key.startsWith('faq_delivery_answer_'))
      .map(key => parseInt(key.replace(/\D+/g, '')))
    )
  ]
  faqNumbers.sort((a, b) => a - b).forEach(num => {
    items.push({
      id: num,
      question: store.parameters[`faq_delivery_question_${num}`] || `Вопрос ${num}`,
      answer: store.parameters[`faq_delivery_answer_${num}`] || 'Ответ не найден',
    })
  })
  return items
});

// закрывает все пункты кроме переданного
function toggleFaq(id) {
  openedFaq.value = openedFaq.value === id ? null : id;
}

</script>

<style lang="scss">


.line-vert {
  position: absolute;
  top: 0;
  left: calc(50% - 0.5px);
  width: 1px;
  height: 100%;
  background-color: $white-100;
  z-index: 10;
}
.line-hor {
  width: 100%;
  height: 1px;
  background-color: $white-100;
  z-index: 100;
}
.delivery-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  .section-title {
    margin: 96px 0 40px;
    text-align: center;
    font-family: Bounded;
    font-weight: 400;
    font-size: 32px;
    line-height: 90%;
    letter-spacing: -2.24px;
    z-index: 20;
  }
  .info-row {
    display: flex;
    z-index: 20;
    .info-card {
      display: flex;
      flex-direction: column;
      margin: 10px 0;
      padding: 20px 10px;
      width: calc(100% - 20px);
      border-radius: 4px;
      background-color: $white-100;
      .card-title {
        margin: 0 0 40px;
        font-family: Bounded;
        font-weight: 250;
        font-size: 24px;
        line-height: 80%;
        letter-spacing: -1.2px;
      }
      .info-text {
        margin: 0;
        font-family: Bounded;
        font-weight: 350;
        font-size: 14px;
        line-height: 110%;
        letter-spacing: -0.7px;
        &.default {
          font-family: Manrope-Medium;
          font-size: 15px;
          color: $black-100;
          line-height: 110%;
          letter-spacing: -0.6px;
        }
        &.small {
          font-family: Manrope-Medium;
          font-size: 15px;
          color: $black-40;
          line-height: 110%;
          letter-spacing: -0.6px;
        }
      }
      .list {
        margin: 0;
        padding: 24px 18px;
        li {
          font-size: 15px;
          line-height: 110%;
          letter-spacing: -0.6px;
        }
        li::marker {
          color: $red-active;
          font-size: 18px;
        }
      }
      .info-note-div {
        display: flex;
        margin: 0;
        padding: 20px 10px;
        gap: 8px;
        background-color: $grey-95;
        border-radius: 4px;
        img {
          width: 20px;
          height: 20px;
        }
        .info-note {
          margin: 0;
          font-size: 15px;
          line-height: 110%;
          letter-spacing: -0.6px;
        }
      }
      .info-warning {
        margin: 40px 0 0;
        color: $red-active;
        font-size: 14px;
        line-height: 100%;
        letter-spacing: -0.56px;
      }
      .payment-box {
        display: flex;
        position: relative;
        flex-direction: column;
        justify-content: space-between;
        padding: 20px 10px;
        gap: 44px;
        background-color: $grey-95;
        border-radius: 4px;
        font-family: Bounded;
        font-weight: 350;
        font-size: 14px;
        line-height: 80%;
        letter-spacing: -0.7px;
        img {
          position: absolute;
          top: 20px;
          right: 10px;
          width: 32px;
          height: 32px;
        }
      }
      .info-note-block {
        display: flex;
        align-items: flex-start;
        padding: 20px 10px;
        gap: 8px;
        background-color: $grey-95;
        border-radius: 4px;
        img {
          width: 20px;
          height: 20px;
        }
        p {
          margin: 0;
          font-size: 16px;
          line-height: 110%;
          letter-spacing: -0.64px;
          .link {
            color: $red-active;
            text-decoration: none;
          }
        }
      }
    }
  }
  .timeline-div {
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 20;
    .timeline-title {
      margin: 96px 0 40px;
      text-align: center;
      width: 75%;
      font-family: Bounded;
      font-weight: 500;
      font-size: 24px;
      line-height: 90%;
      letter-spacing: -0.72px;
    }
    .timeline-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 10px;
      width: 100%;
      .timeline-card {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 20px;
        height: 110px;
        background-color: $white-100;
        border-radius: 4px;
        &.highlight {
          background-color: $black-100;
          color: $white-100;
          .highlight-text {
            margin: 0;
            width: 75%;
            font-family: Bounded;
            font-weight: 250;
            font-size: 24px;
            line-height: 80%;
            letter-spacing: -1.2px;
          }
          .highlight-period {
            margin: 0 0 20px;
            color: $red-active;
            font-family: Bounded;
            font-weight: 500;
            font-size: 24px;
            line-height: 90%;
            letter-spacing: -0.72px;
          }
        }
        .card-period {
          margin: 0;
          font-family: Bounded;
          font-weight: 250;
          font-size: 24px;
          line-height: 80%;
          letter-spacing: -1.2px;
        }
        .card-desc {
          margin: 0;
          color: $grey-20;
          font-size: 16px;
          line-height: 110%;
          letter-spacing: -0.64px;
        }
      }
    }
  }
  .faq {
    padding: 48px 16px;
    text-align: center;
    z-index: 20;
    &-title {
      margin: 64px 0 40px;
      font-family: Bounded;
      font-weight: 500;
      font-size: 32px;
      line-height: 80%;
      letter-spacing: -0.96px;
    }
    &-subtitle {
      text-align: left;
      max-width: 600px;
      margin: 0 auto 32px;
      font-size: 16px;
      line-height: 110%;
      letter-spacing: -0.64px;
    }
    &-list {
      display: flex;
      flex-direction: column;
      margin: 0 0 64px;
      max-width: 800px;
      gap: 4px;
      border-radius: 4px;
    }
    &-item {
      background-color: $white-100;
      border-radius: 4px;
      overflow: hidden;
    }
    &-header {
      display: flex;
      align-items: center;
      padding: 18px 10px;
      cursor: pointer;
      user-select: none;
    }
    &-number {
      @include flex-e-c;
      width: 32px;
      height: 32px;
      background-color: $black-100;
      color: $white-100;
      border-radius: 4px;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
    }
    &-question {
      text-align: center;
      flex-grow: 1;
      font-family: Bounded;
      font-weight: 350;
      font-size: 20px;
      line-height: 80%;
      letter-spacing: -0.8px;
      color: $black-100;
    }
    &-toggle-icon {
      width: 24px;
      height: 24px;
      flex-shrink: 0;
      margin-left: 16px;
      transition: color 0.5s ease-in-out;
      .faq-icon {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
      }
    }
    &-answer {
      padding: 24px 48px;
      text-align: center;
      font-size: 16px;
      line-height: 110%;
      letter-spacing: -0.64px;
      color: $black-100;
    }
    .faq-slide-enter-active,
    .faq-slide-leave-active {
      transition: all 0.5s ease-in-out;
    }
    .faq-slide-enter-from,
    .faq-slide-leave-to {
      max-height: 0;
      opacity: 0;
      padding-top: 0;
    }
    .faq-slide-enter-to,
    .faq-slide-leave-from {
      max-height: 200px;
      opacity: 1;
    }
  }
}

@media (max-width: 768px) {
  .delivery-page {
    .info-row {
      flex-direction: column;
    }
    .timeline-div {
      .timeline-grid {
        grid-template-columns: 1fr;
      }
    }
    .faq {
      padding: 32px 10px;
      &-title {
        font-size: 24px;
        line-height: 90%;
        letter-spacing: -0.72px;
      }
      &-subtitle {
        margin-bottom: 24px;
        font-size: 15px;
        line-height: 110%;
        letter-spacing: -0.6px;
      }
      &-header {
        padding: 16px 10px;
      }
      &-number {
        width: 24px;
        height: 24px;
      }
      &-question {
        font-size: 16px;
        text-align: left;
      }
      &-answer {
        padding: 16px 10px;
        font-size: 15px;
        text-align: left;
      }
    }
  }
}
</style>
