<template>
  <div class="home">

    <!-- HERO -->
    <section class="hero">
      <div class="hero-slide">
        <!-- вставить фон из макета -->
        <div class="image-placeholder">Изображение героя</div>
        <div class="hero-text">
          <h1>Оригинальные бренды<br>и ничего лишнего</h1>
          <div class="hero-controls">
            <button @click="prevHero" aria-label="Назад">←</button>
            <button @click="nextHero" aria-label="Вперёд">→</button>
          </div>
          <router-link to="/catalog" class="btn-catalog">В каталог →</router-link>
        </div>
      </div>
      <div class="marquee">
        <div class="marquee-content">{{ runningText }}</div>
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section class="how-it-works">
      <h2>Как мы работаем</h2>
      <div class="steps">
        <div v-for="step in workSteps" :key="step.step" class="step">
          <div class="icon-placeholder">Иконка {{ step.step }}</div>
          <h3>Шаг {{ step.step }}: {{ step.title }}</h3>
          <p>{{ step.text }}</p>
        </div>
      </div>
    </section>

    <!-- CATEGORIES -->
    <section class="categories">
      <h2>Категории</h2>
      <div class="cat-slider">
        <button @click="prevCat" aria-label="Назад">←</button>
        <div class="cat-slide">
          <!-- вставить картинку категории -->
          <div class="image-placeholder">Изображение {{ categorySlides[currentCat].title }}</div>
          <h3>{{ categorySlides[currentCat].title }}</h3>
          <p>{{ categorySlides[currentCat].desc }}</p>
          <router-link to="/catalog" class="btn-catalog">Каталог</router-link>
        </div>
        <button @click="nextCat" aria-label="Вперёд">→</button>
      </div>
    </section>

    <!-- PRINCIPLES -->
    <section class="principles">
      <div v-for="block in origBlocks" :key="block.title" class="principle">
        <h3 @click="toggleOrig(block)" class="principle-header">
          {{ block.title }} <span>{{ block.open ? '−' : '+' }}</span>
        </h3>
        <transition name="fade">
          <p v-if="block.open" class="principle-text">{{ block.text }}</p>
        </transition>
      </div>
    </section>

    <!-- BESTSELLERS -->
    <section class="bestsellers" v-if="bests.length">
      <h2>Бестселлеры</h2>
      <div class="best-slider">
        <button @click="prevBest" aria-label="Назад">←</button>
        <div class="best-item" v-for="(p, i) in bests" :key="p.variant_sku" v-show="i === bestIndex">
          <button class="fav-btn" @click="toggleFav(p)">
            {{ store.isFavorite(p.color_sku) ? '❤️' : '♡' }}
          </button>
          <img :src="p.image" alt="" class="product-image"/>
          <p class="brand">{{ p.brand }}</p>
          <p class="name">{{ p.name }}</p>
          <p class="price">от {{ p.price }} ₽</p>
        </div>
        <button @click="nextBest" aria-label="Вперёд">→</button>
      </div>
      <router-link to="/catalog" class="btn-catalog">Смотреть все</router-link>
    </section>

    <!-- REQUEST FORM -->
    <section class="request-form">
      <h2>Не нашел что хотел?</h2>
      <p>Загрузите изображение или добавьте артикул товара, и мы выкупим его из официального магазина.</p>
      <form @submit.prevent="onSubmitRequest">
        <input type="text" v-model="request.name" placeholder="Имя" required/>
        <input type="email" v-model="request.email" placeholder="Почта" required/>
        <input type="text" v-model="request.sku" placeholder="Артикул товара" />
        <div class="or-sep">или</div>
        <input type="file" @change="onFileChange" />
        <label><input type="checkbox" v-model="request.agree"/> Я согласен на обработку персональных данных</label>
        <button type="submit" class="btn-submit">Отправить запрос</button>
      </form>
    </section>

    <!-- TESTIMONIALS -->
    <section class="testimonials">
      <h2>Твой стиль, твои отзывы</h2>
      <div v-if="store.reviews.length === 0" class="no-reviews">
        Отзывов пока нет.
      </div>
      <div v-else class="carousel">
        <button @click="prev" aria-label="Назад">←</button>
        <div class="slide">
          <div class="review">
            <p class="user-text">{{ current.client_text1 }}</p>
            <div class="photos">
              <img v-for="url in current.photo_urls" :key="url" :src="url" alt="photo"/>
            </div>
            <p class="shop-text">{{ current.shop_response }}</p>
            <p class="user-text">{{ current.client_text2 }}</p>
            <div class="meta">
              <div class="review-header">
<!--                <img class="avatar" :src="current.avatar_url" alt="аватар"/>-->
                <img class="avatar" :src="icon_default_avatar_white" alt="аватар"/>
                <span class="client-name">{{ current.client_name }}</span>
                <span class="review-date">{{ new Date(current.created_at).toLocaleDateString('ru-RU', { month:'2-digit', year:'numeric' }) }}</span>
              </div>
              <a :href="current.link_url" target="_blank">→</a>
            </div>
          </div>
        </div>
        <button @click="next" aria-label="Вперёд">→</button>
      </div>
    </section>

    <!-- FAQ -->
    <section class="faq">
      <h2 class="faq-title">FAQ</h2>
      <p class="faq-subtitle">
        Здесь ты найдёшь ответы на самые популярные вопросы о заказах, доставке, оплате и возврате. Мы собрали всю важную информацию, чтобы сделать
        твои покупки максимально простыми и прозрачными.
      </p>

      <div class="faq-list">
        <div v-for="item in faqs" :key="item.id" class="faq-item">
          <!-- чёрный квадрат с номером -->
          <div class="faq-number">{{ String(item.id + 1).padStart(2, '0') }}</div>
          <div class="faq-header" @click="toggleFaq(item.id)">
            <!-- текст вопроса -->
            <div class="faq-question">{{ item.question }}</div>
            <!-- иконка: место под svg -->
            <div class="faq-toggle-icon" :class="{ open: item.open }">
              <!-- placeholder для вашей иконки -->
              <img :src="item.open ? icon_faq_minus : icon_faq_plus" alt="toggle" class="faq-icon"/>
            </div>
          </div>
          <!-- ответ с плавным выезжанием -->
          <transition name="faq-slide">
            <div v-if="item.open" class="faq-answer">
              {{ item.answer }}
            </div>
          </transition>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from '@/store/index.js'

import icon_default_avatar_white from '@/assets/images/default_avatar_white.svg'
import icon_faq_plus from '@/assets/images/faq_plus.svg'
import icon_faq_minus from '@/assets/images/faq_minus.svg'

const store   = useStore()

const idx = ref(0)
const faqs = ref([])
const heroIndex = ref(0)
const current = computed(() => store.reviews[idx.value] || {})

function prev() {
  if (!store.reviews.length) return
  idx.value = (idx.value + store.reviews.length - 1) % store.reviews.length
}

function next() {
  if (!store.reviews.length) return
  idx.value = (idx.value + 1) % store.reviews.length
}

// Hero
const runningText = 'Puma //_Future_Vintage_Capsule • sale'

function prevHero() {
  heroIndex.value = (heroIndex.value + 1) % 1
}

function nextHero() {
  heroIndex.value = (heroIndex.value + 1) % 1
}

// How it works
const workSteps = [
  { step:1, title:'Ты выбираешь', text:'Найди товар в каталоге или пришли нам фотографию желаемой модели.' },
  { step:2, title:'Мы проверяем на оригинал', text:'Мы проверяем наличие, подлинность и цену в официальных источниках.' },
  { step:3, title:'Покупаем напрямую', text:'Мы заказываем товары в официальных магазинах без посредников и наценок.' },
  { step:4, title:'Доставляем тебе', text:'Мы организуем доставку в твой город быстро и безопасно.' },
]

// Categories
const categorySlides = [
  { title:'Аксессуары', desc:'Сумки, ремни и игрушки от Max Mara, Coach, Pop Mart и других официальных брендов.' },
  { title:'Одежда',     desc:'Только оригинальные вещи от Nike, Adidas, Supreme и т.д.' },
  { title:'Обувь',      desc:'Хиты от New Balance, Jacquemus и других.' },
]
const currentCat = ref(0)

function prevCat() {
  currentCat.value = (currentCat.value + categorySlides.length - 1) % categorySlides.length
}

function nextCat() {
  currentCat.value = (currentCat.value + 1) % categorySlides.length
}

// Principles
const origBlocks = [
  { title:'Только оригиналы', text:'Работаем напрямую с официальными магазинами. Никаких подделок, никаких посредников.', open:false },
  { title:'Честные цены', text:'Прямая закупка без посредников. Цены на 20–45% ниже, чем в розницах.', open:false },
  { title:'Индивидуальный подход', text:'Не нашел нужную модель? Пришли фото — мы найдём и доставим.', open:false },
  { title:'Прозрачность и уверенность', text:'Открытые условия на каждом этапе без сюрпризов.', open:false },
]
function toggleOrig(block) {
  block.open = !block.open
}

// Bestsellers
const bestIndex = ref(0)
const bests     = computed(() =>
  store.displayedProducts.slice(0, 2).map(g => g.minPriceVariant)
)

function prevBest() {
  bestIndex.value = (bestIndex.value + bests.value.length - 1) % bests.value.length
}

function nextBest() {
  bestIndex.value = (bestIndex.value + 1) % bests.value.length
}

function toggleFav(p) {
  store.isFavorite(p.color_sku) ? store.removeFromFavorites(p.color_sku) : store.addToFavorites(p.color_sku)
}

// Request form
const request = ref({ name:'', email:'', sku:'', file:null, agree:false })

function onFileChange(e) {
  request.value.file = e.target.files[0]
}

function onSubmitRequest() {
  alert('Запрос отправлен!')
}

// FAQ
const QUESTIONS = [
  'Как оформить заказ?',
  'Сколько по времени длится доставка?',
  'Как происходит оплата?',
  'Как я могу быть уверен(а) в качестве товара?',
  'Можно ли вернуть или обменять товар?',
  'Как выбрать правильный размер?',
  'Хочу купить одну вещь, но не нашёл её у вас на сайте. Что делать?',
  'Как отследить мой заказ?'
]

// Подтягиваем ответы из store.settings и собираем финальный массив
function buildFaqs() {
  faqs.value = QUESTIONS.map((q, idx) => {
    // ищем в settings запись с key = `faq_answer_${i+1}`
    const setting = store.settings.find(s => s.key === `faq_answer_${idx+1}`)
    return {
      id: idx,
      question: q,
      answer: setting ? setting.value : 'Нет ответа',
      open: false
    }
  })
}

// закрывает все пункты кроме переданного
function toggleFaq(i) {
  faqs.value = faqs.value.map((item, idx) => ({ ...item, open: idx === i ? !item.open : false}))
}

onMounted(async () => {
  await store.fetchAllProducts()
  await store.fetchSettings()
  await store.fetchReviews()
  buildFaqs()
})

</script>

<style scoped lang="scss">
.home {
  color: #000;
}

/* HERO */
.hero {
  position: relative;
  overflow: hidden;
  padding: 0;
}
.hero-slide {
  position: relative;
}
.image-placeholder {
  background: #ffc;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hero-text {
  position: absolute;
  top: 20%;
  left: 10%;
}
.hero-text h1 {
  font-size: 24px;
  margin-bottom: 16px;
}
.hero-controls button {
  margin-right: 8px;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: #fff;
  padding: 8px;
}
.btn-catalog {
  display: inline-block;
  margin-top: 12px;
  padding: 8px 16px;
  background: #000;
  color: #fff;
  border-radius: 4px;
  text-decoration: none;
}
.marquee {
  overflow: hidden;
  white-space: nowrap;
  background: #000;
  color: #fff;
}
.marquee-content {
  display: inline-block;
  padding-left: 100%;
  animation: marquee 10s linear infinite;
}
@keyframes marquee {
  from { transform: translateX(0); }
  to   { transform: translateX(-100%); }
}

/* HOW IT WORKS */
.how-it-works {
  padding: 24px 16px;
}
.how-it-works h2 {
  text-align: center;
  margin-bottom: 16px;
}
.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}
.step {
  text-align: center;
}
.icon-placeholder {
  background: #ffc;
  width: 60px;
  height: 60px;
  margin: 0 auto 8px;
}

/* CATEGORIES */
.categories {
  padding: 24px 16px;
  background: #f8f8f8;
}
.categories h2 {
  text-align: center;
  margin-bottom: 16px;
}
.cat-slider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.cat-slide {
  text-align: center;
}
.cat-slide .image-placeholder {
  height: 120px;
  margin-bottom: 8px;
}
.cat-slide h3 {
  margin-bottom: 8px;
}

/* PRINCIPLES */
.principles {
  padding: 24px 16px;
}
.principle {
  margin-bottom: 12px;
}
.principle-header {
  display: flex;
  justify-content: space-between;
  cursor: pointer;
  font-weight: bold;
}
.principle-text {
  margin: 8px 0 16px;
  font-size: 16px;
  line-height: 1.5;
}

/* fade-transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* BESTSELLERS */
.bestsellers {
  padding: 24px 16px;
  background: #f8f8f8;
  text-align: center;
}
.bestsellers h2 {
  margin-bottom: 16px;
}
.best-slider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.best-item {
  position: relative;
  width: 150px;
}
.fav-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: transparent;
  border: none;
  font-size: 18px;
}
.product-image {
  width: 100%;
  height: 100px;
  object-fit: cover;
  margin-bottom: 8px;
}
.brand, .name, .price {
  margin: 4px 0;
}
.brand {
  font-weight: 600;
}
.name  {
  font-size: 14px;
}
.price {
  font-size: 14px;
  color: #333;
}

/* REQUEST FORM */
.request-form {
  padding: 24px 16px;
}
.request-form h2 {
  text-align: center;
  margin-bottom: 8px;
}
.request-form form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 320px;
  margin: 0 auto;
}
.or-sep {
  text-align: center;
  margin: 12px 0;
  font-weight: bold;
}
.btn-submit {
  padding: 8px;
  background: #000;
  color: #fff;
  border: none;
  border-radius: 4px;
}

/* TESTIMONIALS */
.testimonials {
  background: #f7f7f7;
  padding: 24px;
  border-radius: 12px;
}
.no-reviews {
  font-style: italic;
}
.carousel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.slide {
  width: 300px;
}
.review {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
}
.user-text {
  background: #000;
  color: #fff;
  padding: 12px;
  border-radius: 8px;
  display: inline-block;
  max-width: 100%;
  margin: 8px 0;
}
.shop-text {
  background: #fff;
  color: #000;
  padding: 12px;
  border-radius: 8px;
  display: inline-block;
  max-width: 100%;
  margin: 8px 0;
}
.photos {
  margin: 8px 0;
}
.photos img {
  width: 120px;
  height: auto;
  margin-right: 8px;
  border-radius: 4px;
}
.meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}
.review-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 12px;
  border: 2px solid #ddd;
}
.client-name {
  color: #E94F37;
  font-weight: 600;
  margin-right: 8px;
}
.review-date {
  color: #888;
  font-size: 14px;
}

/* FAQ */
.faq {
  padding: 48px 16px;
  background: #f0f0f0;
  text-align: center;

  &-title {
    margin-bottom: 40px;
    font-family: Bounded-500;
    font-size: 24px;
    line-height: 90%;
    letter-spacing: -0.72px;
  }
  &-subtitle {
    max-width: 600px;
    margin: 0 auto 32px;
    font-size: 15px;
    line-height: 110%;
    letter-spacing: -0.6px;
  }
  &-list {
    display: flex;
    flex-direction: column;
    margin: 0 auto;
    max-width: 800px;
    gap: 4px;
    border-radius: 4px;
  }
  &-item {
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
  }
  &-header {
    display: flex;
    align-items: center;
    padding: 16px 24px;
    cursor: pointer;
    user-select: none;
  }
  &-number {
    background: $black-100;
    color: $white-100;
    width: 24px;
    height: 24px;
    text-align: center;
    border-radius: 4px;
    flex-shrink: 0;
    margin-right: 16px;
    font-size: 16px;
    line-height: 100%;
    letter-spacing: -0.64px;
  }
  &-question {
    text-align: left;
    flex-grow: 1;
    font-family: Bounded-250;
    font-size: 16px;
    line-height: 80%;
    letter-spacing: -0.8px;
  }
  &-toggle-icon {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
    margin-left: 16px;
    transition: color 0.5s ease-in-out;
    color: #000;
    &.open {
      color: #E94F37;
    }
    .faq-icon {
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }
  }
  &-answer {
    padding: 16px 24px;
    text-align: left;
    font-family: Bounded-250;
    font-size: 16px;
    line-height: 80%;
    letter-spacing: -0.8px;
  }

  /* плавное «slide down» */
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

/* RESPONSIVE */
@media (max-width: 600px) {
  .hero .image-placeholder {
    height: 200px;
  }
  .hero {
    padding: 0 8px;
  }
  .hero-text h1 {
    font-size: 18px;
    top: 15%;
    left: 5%;
  }
  .marquee-content {
    font-size: 12px;
  }
  .hero-controls {
    position: absolute;
    bottom: 8px;
    left: 5%;
  }
  .btn-catalog {
    padding: 6px 12px;
    font-size: 14px;
    margin-left: 100px;
  }
  .how-it-works .steps {
    gap: 12px;
  }
  .categories .cat-slider {
    flex-direction: column;
    gap: 12px;
  }
  .categories .cat-slider button {
    width: 100%;
  }
  .principles {
    padding: 16px 8px;
  }
  .principle {
    font-size: 14px;
  }
  .bestsellers .best-slider {
    flex-direction: column;
  }
  .best-item {
    width: 100%;
    max-width: 250px;
    margin: 0 auto 16px;
  }
  .request-form form {
    padding: 0 16px;
  }
  .request-form input,
  .request-form .btn-submit {
    width: 100%;
  }
  .or-sep {
    text-align: center;
  }

  .faq {
    padding: 32px 10px;
    &-title {
      font-size: 28px;
    }
    &-subtitle {
      font-size: 16px;
      margin-bottom: 24px;
    }
    &-header {
      padding: 12px 16px;
    }
    &-question {
      font-size: 16px;
    }
    &-answer {
      font-size: 14px;
    }
  }
}
</style>
