<template>
  <div class="about-page">
    <!-- Cover Section -->
    <section class="cover-section">
      <!-- здесь будет фон-изображение (пока желтый блок) -->
      <div class="cover-image placeholder"></div>
      <div class="cover-overlay">
        <h1 class="cover-title">YANDA.SHOP</h1>
        <p class="cover-tagline">Оригинальность во всём. Честность в деталях.</p>
      </div>
      <!-- Running marquee of 5 words -->
      <div class="marquee">
        <div class="marquee-content">Слово1 Слово2 Слово3 Слово4 Слово5</div>
      </div>
    </section>

    <!-- Categories Navigation -->
    <section class="categories-section">
      <div class="category">Честность</div>
      <div class="category">Оригинальность</div>
      <div class="category">Стиль</div>
    </section>

    <!-- About Us Section -->
    <section class="about-section">
      <h2>О нас</h2>
      <div class="about-content">
        <div class="about-main">
          <p>Мы запустили YANDA, потому что устали от шума, фейков и бессмысленных наценок.</p>
          <p>Мы знаем: можно одеваться стильно, честно и без лишних вещей. Мы только начали — и не боимся об этом сказать.</p>
        </div>
        <div class="about-columns">
          <div class="vision">
            <h3>Наше видение</h3>
            <p>В мире, где слишком много одинакового, мы помогаем тебе найти оригинал.</p>
            <p>Не то, что просто доступно, а то, что действительно тебе подойдет.</p>
          </div>
          <div class="mission">
            <h3>Наша миссия</h3>
            <p>Мы верим в осознанную моду, справедливое ценообразование и вещи, которые говорят за человека, а не вместо него.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Mosaic Image/Text Section -->
    <section class="mosaic-section">
      <div class="mosaic-row">
        <div class="placeholder image-block"></div>
        <div class="placeholder image-block"></div>
      </div>
      <div class="mosaic-row">
        <div class="placeholder image-block"></div>
        <div class="mosaic-text">
          <p>Мы закупаем товары напрямую, тщательно проверяем их и передаем дальше — с заботой, вниманием и уважением к твоему стилю.</p>
        </div>
      </div>
    </section>

    <!-- Philosophy Section -->
    <section class="philosophy-section">
      <h2>Философия</h2>
      <p>Мы выбираем путь, где качество важнее количества. Где честность — это не формат, а основа. Где одежда становится частью того, кто ты есть.</p>
      <!-- здесь будет декоративное изображение или фон (желтый блок) -->
      <div class="placeholder philosophy-graphic"></div>
    </section>

    <!-- Details Cards Section -->
    <section class="details-section">
      <h2>Когда детали имеют значение</h2>
      <div class="cards">
        <div class="card">
          <div class="number">01</div>
          <div class="icon placeholder"></div>
          <h3>Никаких подделок</h3>
          <p>Только оригинальные товары, заказанные напрямую из Poizon и проверенных магазинов.</p>
        </div>
        <div class="card">
          <div class="number">02</div>
          <div class="icon placeholder"></div>
          <h3>Дешевле, потому что честно</h3>
          <p>Наши товары на 20–45% дешевле, чем в российских магазинах — по реальной цене без накруток.</p>
        </div>
        <div class="card">
          <div class="number">03</div>
          <div class="icon placeholder"></div>
          <h3>Ты выбираешь — мы находим</h3>
          <p>Пришли нам фото, ссылку или просто описание — и мы подберем то, что тебе подойдет.</p>
        </div>
        <div class="card">
          <div class="number">04</div>
          <div class="icon placeholder"></div>
          <h3>Мы не бот</h3>
          <p>Пиши в Telegram: тебе ответит человек, а не автоответчик — мы действительно хотим помочь.</p>
        </div>
      </div>
    </section>

    <!-- Community Section -->
    <section class="community-section">
      <h2>Сообщество</h2>
      <p>Пиши нам в Телеграм — это самый быстрый и легкий способ для связи.</p>
      <button class="join-button" @click="joinTelegram">Присоединиться</button>
      <div class="social-images">
        <div class="placeholder image-block"></div>
        <div class="placeholder image-block"></div>
        <div class="placeholder image-block"></div>
        <div class="placeholder image-block"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
function joinTelegram() {
  window.open('https://t.me/yanda_shop', '_blank')
}
</script>

<style scoped lang="scss">
.about-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  color: #000;
  background: #f5f5f5;
}

section {
  width: 100%;
  max-width: 480px;
  margin-bottom: 24px;
}

.placeholder {
  background: yellow;
}

.cover-section {
  position: relative;
  height: 60vh;
}
.cover-image {
  width: 100%;
  height: 100%;
}
.cover-overlay {
  position: absolute;
  top: 20%;
  left: 10%;
  color: white;
}
.marquee {
  overflow: hidden;
  white-space: nowrap;
  background: rgba(0,0,0,0.6);
}
.marquee-content {
  display: inline-block;
  padding-left: 100%;
  animation: marquee 10s linear infinite;
  color: #fff;
}
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100%); }
}

.categories-section {
  display: flex;
  justify-content: space-around;
  background: #ddd;
  padding: 16px 0;
}

.about-section h2,
.philosophy-section h2,
.details-section h2,
.community-section h2 {
  font-size: 24px;
  text-align: center;
  margin-bottom: 16px;
}

.about-content .about-main p,
.about-columns h3,
.about-columns p {
  margin-bottom: 8px;
}

.about-columns {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mosaic-section .mosaic-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.mosaic-text {
  flex: 1;
  background: #fff;
  padding: 16px;
}
.image-block {
  flex: 1;
  height: 120px;
}

.philosophy-section {
  background: #000;
  color: #fff;
  text-align: center;
  padding: 32px 16px;
}
.philosophy-graphic {
  height: 100px;
  margin-top: 16px;
}

.details-section .cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.card {
  background: #fff;
  padding: 16px;
  position: relative;
}
.number {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #000;
  color: #fff;
  padding: 4px 8px;
}
.icon {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
}

.community-section .join-button {
  background: #000;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 24px;
  cursor: pointer;
  margin-bottom: 16px;
}
.social-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.image-block {
  width: calc(50% - 4px);
  height: 100px;
}

@media (max-width: 600px) {
  .cover-section {
    height: 40vh;
  }
  .cover-overlay {
    top: 15%;
    left: 5%;
  }
  .cover-title {
    font-size: 20px;
  }
  .cover-tagline {
    font-size: 14px;
  }
  .marquee {
    font-size: 12px;
    padding: 4px 0;
  }
  .categories-section {
    flex-direction: column;
    gap: 12px;
    padding: 12px 0;
  }
  .category {
    font-size: 16px;
  }
  .about-section h2,
  .philosophy-section h2,
  .details-section h2,
  .community-section h2 {
    font-size: 20px;
  }
  .about-content {
    padding: 0 8px;
  }
  .mosaic-section .mosaic-row {
    flex-direction: column;
  }
  .image-block, .mosaic-text {
    width: 100%;
  }
  .image-block {
    height: 160px;
  }
  .philosophy-section {
    padding: 16px 8px;
  }
  .philosophy-graphic {
    height: 80px;
  }
  .details-section .cards {
    gap: 12px;
  }
  .card {
    padding: 12px;
  }
  .number {
    top: 4px;
    left: 4px;
    font-size: 12px;
  }
  .join-button {
    width: 100%;
    font-size: 14px;
    padding: 10px;
  }
  .social-images {
    gap: 4px;
  }
  .social-images .image-block {
    width: calc(50% - 2px);
    height: 80px;
  }
}

</style>
