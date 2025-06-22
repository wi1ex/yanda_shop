<template>
  <div class="about-page">
    <!-- Cover Section -->
    <section class="cover-section">
      <div class="cover-bg">
        <img class="cover-image" :src="about_image1" alt="Главное изображение" />
      </div>
      <div class="cover-overlay">
        <img class="title" :src="about_text_logo" alt="Название" />
        <p class="subtitle">Оригинальность</p>
        <p class="subtitle">во всём.</p>
        <p class="subtitle">Честность</p>
        <p class="subtitle">в деталях.</p>
      </div>
      <div class="marquee-wrap">
        <div class="marquee-content">{{ runningText }}</div>
      </div>
    </section>

    <!-- About Us Section -->
    <section class="section about-us">
      <h2 class="section-title">О нас</h2>
      <div class="about-content">
        <div class="text-main">
          <p>Мы запустили YANDA, потому что устали от шума, фейков и бессмысленных наценок.</p>
          <p>Мы знаем: можно одеваться стильно, честно и без лишних вещей. Мы только начали — и не боимся об этом сказать.</p>
          <p>Потому что мы строим не магазин, а культуру выбора.</p>
        </div>
        <div class="text-columns">
          <div class="column">
            <h3>Наше видение</h3>
            <p>В мире, где слишком много одинакового, мы помогаем тебе найти оригинал.</p>
            <p>Не то, что просто доступно, а то, что действительно тебе подойдет.</p>
          </div>
          <div class="column">
            <h3>Наша миссия</h3>
            <p>Мы верим в осознанную моду, справедливое ценообразование и вещи, которые говорят за человека, а не вместо него.</p>
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
        <div class="mosaic-item">
          <img :src="about_image3" alt="Изображение 2" />
        </div>
        <div class="mosaic-text">
          <p>Мы закупаем товары напрямую, тщательно проверяем их и передаем дальше — с заботой, вниманием и уважением к твоему стилю.</p>
        </div>
      </div>
    </section>

    <!-- Philosophy Section -->
    <section class="section philosophy">
      <div class="philosophy-image">
        <img :src="about_image4" alt="Декоративное изображение философии" />
      </div>
      <h2 class="section-title">Философия</h2>
      <p class="philosophy-text">Мы выбираем путь, где качество важнее количества. Где честность — это не формат, а основа. Где одежда становится частью того, кто ты есть.</p>
      <div class="philosophy-image">
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
          <h3>Никаких подделок</h3>
          <p>Только оригинальные товары, заказанные напрямую из Poizon и проверенных магазинов.</p>
        </div>
        <div class="card">
          <div class="card-number">02</div>
          <div class="card-icon"><img :src="about_image7" alt="Иконка 2" /></div>
          <h3>Дешевле, потому что честно</h3>
          <p>Наши товары на 20–45% дешевле, чем в российских магазинах — по реальной цене без накруток.</p>
        </div>
        <div class="card">
          <div class="card-number">03</div>
          <div class="card-icon"><img :src="about_image8" alt="Иконка 3" /></div>
          <h3>Ты выбираешь — мы находим</h3>
          <p>Пришли нам фото, ссылку или просто описание — и мы подберем то, что тебе подойдет.</p>
        </div>
        <div class="card">
          <div class="card-number">04</div>
          <div class="card-icon"><img :src="about_image9" alt="Иконка 4" /></div>
          <h3>Мы не бот</h3>
          <p>Пиши в Telegram: тебе ответит человек, а не автоответчик — мы действительно хотим помочь.</p>
        </div>
      </div>
    </section>

    <!-- Community Section -->
    <section class="section community">
      <h2 class="section-title">Сообщество</h2>
      <p class="community-text">Пиши нам в Телеграм — это самый быстрый и легкий способ для связи.</p>
      <button class="join-button" @click="joinTelegram">Присоединиться</button>
      <div class="community-images">
        <div class="img-item"><img :src="about_image11" alt="" /></div>
        <div class="img-item">
          <a v-if="store.adminSettings.url_telegram" :href="store.adminSettings.url_telegram" target="_blank" rel="noopener" class="link">Telegram</a>
          <a v-if="store.adminSettings.url_instagram" :href="store.adminSettings.url_instagram" target="_blank" rel="noopener" class="link">Instagram</a>
          <a v-if="store.adminSettings.url_email" :href="`mailto:${store.adminSettings.url_email}`" rel="noopener" class="link">E-mail</a>
        </div>
        <div class="img-item"><img :src="about_image10" alt="" /></div>
        <div class="img-item"><img :src="about_image12" alt="" /></div>
      </div>
    </section>
  </div>
</template>

<script setup>
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
import about_text_logo from '@/assets/images/about_text_logo.svg'

const runningText = 'ЧЕСТНОСТЬ ОРИГИНАЛЬНОСТЬ СТИЛЬ ГАРАНТИИ ВЫГОДА'

function joinTelegram() {
  window.open('https://t.me/yanda_shop', '_blank');
}
</script>

<style scoped lang="scss">
.about-page {
  width: 100%;
  background: #f5f5f5;
  color: #000;
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
  height: 60vh;
  overflow: hidden;
}
.cover-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cover-overlay {
  position: absolute;
  top: 20%;
  left: 10%;
  transform: translateY(-20%);
}
.title {
  width: 100%;
}
.subtitle {
  font-size: 24px;
  color: #fff;
  margin-top: 16px;
}
.marquee-wrap {
  position: absolute;
  bottom: 0;
  width: 100%;
  background: rgba(0,0,0,0.6);
  overflow: hidden;
}
.marquee-content {
  display: inline-block;
  white-space: nowrap;
  padding-left: 100%;
  animation: marquee 15s linear infinite;
  color: #fff;
  font-size: 24px;
  line-height: 1.5;
  word-spacing: 50px;
}
@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-100%); } }

.about-us .section-title,
.philosophy .section-title,
.details .section-title,
.community .section-title {
  text-align: center;
  font-size: 36px;
  margin-bottom: 48px;
}

.about-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}
.text-main p {
  font-size: 18px;
  margin-bottom: 16px;
}
.text-columns {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.text-columns .column h3 {
  font-size: 20px;
  margin-bottom: 12px;
}

.mosaic {
  background: #fff;
}
.mosaic-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: auto auto;
  gap: 16px;
}
.mosaic-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.mosaic-text {
  grid-column: 1 / -1;
  font-size: 18px;
  line-height: 1.6;
}

.philosophy {
  background: #000;
  color: #fff;
  text-align: center;
  padding: 80px 32px;
}
.philosophy-text {
  max-width: 800px;
  margin: 0 auto 40px;
  font-size: 18px;
  line-height: 1.6;
}
.philosophy-image img {
  width: 100%;
  max-width: 400px;
  display: block;
  margin: 0 auto;
}

.details .cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}
.card {
  background: #fff;
  padding: 24px;
  position: relative;
}
.card-number {
  position: absolute;
  top: 16px;
  left: 16px;
  background: #000;
  color: #fff;
  padding: 4px 8px;
  font-size: 14px;
}
.card-icon img {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 24px;
  height: 24px;
}
.card h3 {
  margin-top: 48px;
  font-size: 20px;
  margin-bottom: 12px;
}
.card p {
  font-size: 16px;
  line-height: 1.5;
}

.community-text {
  text-align: center;
  font-size: 20px;
  max-width: 600px;
  margin: 0 auto 24px;
}
.join-button {
  display: block;
  margin: 0 auto 32px;
  background: #000;
  color: #fff;
  padding: 16px 32px;
  border-radius: 24px;
  font-size: 18px;
  cursor: pointer;
}
.community-images {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.community-images .img-item img {
  width: 100%;
  height: auto;
  object-fit: cover;
}

/* Mobile (<600px) */
@media (max-width: 600px) {
  .section {
    padding: 40px 16px;
  }
  .cover-section {
    height: 40vh;
  }
  .subtitle {
    font-size: 16px;
  }
  .marquee-content {
    font-size: 14px;
  }
  .about-content {
    grid-template-columns: 1fr;
  }
  .details .cards {
    grid-template-columns: 1fr;
  }
  .mosaic-grid {
    grid-template-columns: 1fr;
  }
  .community-images {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
