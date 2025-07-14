<template>
  <div class="about-page">
    <!-- Cover Section -->
    <section class="cover-section">
      <div class="cover-bg">
        <img class="cover-image" :src="about_image1" alt="Главное изображение" />
      </div>
      <div class="cover-overlay">
        <img class="title" :src="about_text_logo" alt="Название" />
        <div class="subtitle-div">
          <div class="subtitle-column">
            <p class="subtitle" style="align-self: flex-start;">Оригинальность</p>
            <p class="subtitle" style="align-self: flex-end;">во всём.</p>
          </div>
          <div class="subtitle-column">
            <p class="subtitle" style="align-self: flex-end;">в деталях.</p>
            <p class="subtitle" style="align-self: flex-start;">Честность</p>
          </div>
        </div>
      </div>
      <div class="marquee-wrap">
        <div class="marquee-content">ЧЕСТНОСТЬ ОРИГИНАЛЬНОСТЬ СТИЛЬ ГАРАНТИИ ВЫГОДА</div>
      </div>
    </section>

    <!-- About Us Section -->
    <section class="section about-us">
      <h2 class="section-title">О нас</h2>
      <div class="about-content">
        <div class="text-main">
          <p>
            Мы запустили YANDA, потому что устали от шума, фейков и бессмысленных наценок.
          </p>
          <p style="width: 60%; left: 25%;">
            Мы знаем: можно одеваться стильно, честно и без лишних вещей. Мы только начали — и не боимся об этом сказать.
          </p>
          <p style="width: 40%; left: 50%;">
            Потому что мы строим не магазин, а культуру выбора.
          </p>
        </div>
        <div class="text-columns">
          <div class="column">
            <h3>Наше видение</h3>
            <div class="column-div">
              <p>В мире, где слишком много одинакового, мы помогаем тебе найти оригинал.</p>
              <p>Не то, что просто доступно, а то, что действительно тебе подойдет.</p>
            </div>
          </div>
          <div class="column">
            <h3>Наша миссия</h3>
            <div class="column-div">
              <p>Мы верим в осознанную моду, справедливое ценообразование и вещи, которые говорят за человека, а не вместо него.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Mosaic Section -->
    <section class="section mosaic">
      <div class="mosaic-grid">
        <div class="mosaic-item">
          <img :src="about_image2" alt="Изображение 1" />
        </div>
        <div class="mosaic-div">
          <div class="mosaic-item" style="width: 50%;">
            <img :src="about_image3" alt="Изображение 2" />
          </div>
          <div class="mosaic-text">
            <p>Мы закупаем товары напрямую, тщательно проверяем их и передаем дальше — с заботой, вниманием и уважением к твоему стилю.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Philosophy Section -->
    <section class="section philosophy">
      <div class="philosophy-image" style="justify-content: flex-end;">
        <img :src="about_image4" alt="Декоративное изображение философии" />
      </div>
      <div class="philosophy-div">
        <img :src="about_image13" alt="Философия иконка 1" />
        <h2 class="section-title">Философия</h2>
        <div class="philosophy-row">
          <img :src="about_image14" alt="Философия иконка 2" />
          <p class="philosophy-text">Мы выбираем путь, где качество важнее количества. Где честность — это не формат, а основа. Где одежда становится частью того, кто ты есть.</p>
          <img :src="about_image15" alt="Философия иконка 3" />
        </div>
        <img :src="about_image16" alt="Философия иконка 4" />
      </div>
      <div class="philosophy-image" style="justify-content: flex-start;">
        <img :src="about_image5" alt="Декоративное изображение философии" />
      </div>
    </section>

    <!-- Details Cards Section -->
    <section class="section details">
      <h2 class="section-title">Когда детали имеют значение</h2>
      <div class="cards">
        <div class="card">
          <div class="card-number">01</div>
          <div class="card-icon"><img :src="about_image6" alt="Иконка 1" /></div>
          <h3>Никаких подделок Никаких иллюзий</h3>
          <p>Только оригинальные товары, заказанные напрямую из Poizon и проверенных магазинов. Трижды проверяем товар, прежде чем он попадет к тебе в руки.</p>
        </div>
        <div class="card">
          <div class="card-number">02</div>
          <div class="card-icon"><img :src="about_image7" alt="Иконка 2" /></div>
          <h3>Дешевле, потому что честно</h3>
          <p>Наши товары на 20–45% дешевле, чем в российских магазинах. Не потому, что они хуже, а потому, что мы не играем с наценками и продаем по реальной цене.</p>
        </div>
        <div class="card">
          <div class="card-number">03</div>
          <div class="card-icon"><img :src="about_image8" alt="Иконка 3" /></div>
          <h3>Ты выбираешь — мы находим</h3>
          <p>Пришли нам фото, ссылку или просто описание — и мы подберем то, что тебе подойдет. Это не шаблонный каталог, это персональный подход.</p>
        </div>
        <div class="card">
          <div class="card-number">04</div>
          <div class="card-icon"><img :src="about_image9" alt="Иконка 4" /></div>
          <h3>Мы не бот</h3>
          <p>Пиши в Telegram: тебе ответит человек, а не автоответчик. Мы не просто консультируем — мы подскажем по-дружески, ведь нам действительно не все равно.</p>
        </div>
      </div>
    </section>

    <!-- Community Section -->
    <section class="section community">
      <h2 class="section-title">Сообщество</h2>
      <p class="community-text">Пиши нам в Телеграм — это самый быстрый и легкий способ для связи.</p>
      <a v-if="store.parameters.url_telegram" :href="store.parameters.url_telegram" target="_blank" rel="noopener" class="join-button">Присоединиться</a>
      <div class="community-images">
        <div class="img-item-div">
          <div class="img-item"><img :src="about_image11" alt=""/></div>
          <div class="img-item">
            <a v-if="store.parameters.url_telegram" :href="store.parameters.url_telegram" target="_blank" rel="noopener" class="link">Telegram</a>
            <a v-if="store.parameters.url_instagram" :href="store.parameters.url_instagram" target="_blank" rel="noopener" class="link">Instagram</a>
            <a v-if="store.parameters.url_email" :href="`mailto:${store.parameters.url_email}`" rel="noopener" class="link">E-mail</a>
          </div>
        </div>
        <div class="img-item-div">
          <div class="img-item"><img :src="about_image10" alt=""/></div>
          <div class="img-item"><img :src="about_image12" alt=""/></div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useStore } from '@/store/index.js'
import about_image1 from '@/assets/images/about_image1.png'
import about_image2 from '@/assets/images/about_image2.png'
import about_image3 from '@/assets/images/about_image3.png'
import about_image4 from '@/assets/images/about_image4.png'
import about_image5 from '@/assets/images/about_image5.png'
import about_image6 from '@/assets/images/about_image6.svg'
import about_image7 from '@/assets/images/about_image7.svg'
import about_image8 from '@/assets/images/about_image8.svg'
import about_image9 from '@/assets/images/about_image9.svg'
import about_image10 from '@/assets/images/about_image10.png'
import about_image11 from '@/assets/images/about_image11.png'
import about_image12 from '@/assets/images/about_image12.png'
import about_image13 from '@/assets/images/about_image13.png'
import about_image14 from '@/assets/images/about_image14.png'
import about_image15 from '@/assets/images/about_image15.png'
import about_image16 from '@/assets/images/about_image16.png'
import about_text_logo from '@/assets/images/about_text_logo.svg'

const store = useStore()
</script>

<style scoped lang="scss">
.about-page {
  width: 100%;
  background-color: $grey-87;
  color: $black-100;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.link {
  color: inherit;
  text-decoration: none;
  font-size: 14px;
  transition: opacity 0.2s;
}

.section {
  width: 100%;
  max-width: 1200px;
  padding: 80px 32px;
  box-sizing: border-box;
}

.cover-section {
  position: relative;
  width: 100%;
  height: 1000px;
  overflow: hidden;
}
.cover-bg {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
.cover-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cover-overlay {
  display: flex;
  flex-direction: column;
  position: absolute;
  top: 66px;
  width: 100%;
}
.title {
  position: relative;
  top: 94px;
  width: 100%;
  mix-blend-mode: exclusion;
}
.subtitle-div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 94px;
  padding: 10px;
}
.subtitle-column {
  display: flex;
  flex-direction: column;
  width: 35%;
}
.subtitle {
  margin: 0;
  font-size: 20px;
  color: $white-100;
  line-height: 110%;
  letter-spacing: -0.4px;
}
.marquee-wrap {
  position: absolute;
  bottom: 0;
  padding: 10px;
  width: 100%;
  background-color: $white-100;
  overflow: hidden;
}
.marquee-content {
  display: inline-block;
  white-space: nowrap;
  padding-left: 100%;
  animation: marquee 15s linear infinite;
  color: $grey-20;
  font-size: 16px;
  line-height: 110%;
  letter-spacing: -0.6px;
  word-spacing: 50px;
}
@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-100%); } }

.about-us{
  padding: 56px 16px;
}

.section-title {
  margin: 40px;
  font-family: Bounded-500;
  text-align: center;
  font-size: 32px;
  line-height: 90%;
  letter-spacing: -0.72px;
}

.about-content {
  display: flex;
  flex-direction: column;
}
.text-main {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.text-main p {
  position: relative;
  margin: 0;
  color: $grey-20;
  font-size: 20px;
  font-family: Bounded-300;
  line-height: 110%;
  letter-spacing: -1px;
}

.text-columns {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin: 32px 0;
}
.column {
  display: flex;
  width: 100%;
  gap: 10px;
}
.column-div {
  display: flex;
  flex-direction: column;
  width: 50%;
}
.column h3 {
  margin: 0;
  width: 50%;
  text-align: end;
  color: $black-40;
  font-size: 15px;
  line-height: 110%;
  letter-spacing: -0.6px;
}
.column p {
  margin: 0;
  color: $black-100;
  font-size: 15px;
  line-height: 110%;
  letter-spacing: -0.6px;
}

.mosaic {
  padding: 0;
}
.mosaic-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 96px;
}
.mosaic-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}
.mosaic-div {
  display: flex;
  gap: 5px;
}
.mosaic-text {
  display: flex;
  width: 50%;
}
.mosaic-text p {
  margin: 0;
  align-self: flex-end;
  color: $grey-20;
  font-size: 14px;
  line-height: 100%;
  letter-spacing: -0.56px;
}

.philosophy {
  background-color: $black-100;
  color: $white-100;
  text-align: center;
  padding: 80px 32px;
}
.philosophy-div {
  display: flex;
  flex-direction: column;
  padding: 56px 0;
}
.philosophy-row {
  display: flex;
}
.philosophy-text {
  margin: 0;
  font-family: Bounded-300;
  font-size: 20px;
  line-height: 90%;
  letter-spacing: -1px;
}
.philosophy-image {
  display: flex;
  width: 100%;
}
.philosophy-div img {
  width: 50%;
}
.philosophy-row img {
  width: 50%;
}
.philosophy-image img {
  width: 50%;
}

.details {
  padding: 56px 10px 0;
}
.details .cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.card {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: relative;
  background-color: $white-100;
  gap: 16px;
  height: 300px;
  padding: 20px 10px;
}
.card-number {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: absolute;
  top: 0;
  left: 0;
  width: 50px;
  height: 50px;
  border-radius: 4px;
  background-color: $black-100;
  color: $white-100;
  font-size: 32px;
  line-height: 90%;
  letter-spacing: -1.28px;
}
.card-icon img {
  position: absolute;
  top: 20px;
  right: 10px;
  width: 50px;
  height: 50px;
}
.card h3 {
  display: flex;
  margin: 0;
  font-family: Bounded-300;
  font-size: 28px;
  line-height: 90%;
  letter-spacing: -1.4px;
}
.card p {
  display: flex;
  margin: 0;
  font-size: 15px;
  line-height: 110%;
  letter-spacing: -0.6px;
}

.community-text {
  text-align: center;
  font-size: 20px;
  max-width: 600px;
  margin: 0 auto 24px;
}
.join-button {
  display: flex;
  justify-content: center;
  justify-self: center;
  padding: 8px 32px;
  width: fit-content;
  border-radius: 999px;
  background-color: $black-100;
  color: $white-100;
  font-size: 18px;
  cursor: pointer;
  text-decoration: none;
}

.community {
  padding: 56px 0;
}
.community-images {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 10px;
}
.community-images .img-item-div{
  display: flex;
  width: 100%;
  gap: 10px;
}
.community-images .img-item {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  width: 50%;
}
.community-images .img-item img {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 4px;
}

@media (max-width: 600px) {
  .section-title {
    font-size: 24px;
  }
  .cover-section {
    height: 739px;
  }
  .cover-image {
    position: relative;
    top: -24px;
  }
  .subtitle {
    font-size: 16px;
    letter-spacing: -0.64px;
  }
  .marquee-content {
    font-size: 15px;
  }
}
</style>
