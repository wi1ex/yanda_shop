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
        <div
          class="best-item"
          v-for="(p, i) in bests"
          :key="p.variant_sku"
          v-show="i === bestIndex"
        >
          <button class="fav-btn" @click="toggleFav(p)">
            {{ store.isFavorite(p) ? '❤️' : '♡' }}
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
      <div class="messages">
        <div v-for="msg in testimonials" :key="msg.id" :class="['message', msg.from==='user'?'user':'shop']">
          {{ msg.text }}
        </div>
      </div>
      <div class="author">
        <img :src="testimonialsAuthor.avatar" alt="" class="avatar"/>
        <div>{{ testimonialsAuthor.name }}, {{ testimonialsAuthor.year }}</div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="faq">
      <h2>FAQ</h2>
      <p>Здесь ты найдёшь ответы на самые популярные вопросы о заказах, доставке и возврате.</p>
      <div class="questions">
        <div v-for="(q, idx) in faqs" :key="idx" class="question">
          <div class="q-header" @click="toggleFaq(idx)">
            <span class="q-num">{{ String(idx+1).padStart(2,'0') }}.</span>
            {{ q.question }}
            <span class="toggle">{{ q.open ? '−' : '+' }}</span>
          </div>
          <transition name="fade">
            <p v-if="q.open" class="q-answer">{{ q.answer }}</p>
          </transition>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

// HERO
const heroIndex = ref(0)
function prevHero(){ heroIndex.value = (heroIndex.value + 1) % 1 }
function nextHero(){ heroIndex.value = (heroIndex.value + 1) % 1 }
const runningText = 'Puma //_Future_Vintage_Capsule • sale'

// HOW IT WORKS
const workSteps = [
  { step:1, title:'Ты выбираешь', text:'Найди товар в каталоге или пришли нам фотографию желаемой модели.' },
  { step:2, title:'Мы проверяем на оригинал', text:'Мы проверяем наличие, подлинность и цену в официальных источниках.' },
  { step:3, title:'Покупаем напрямую', text:'Мы заказываем товары в официальных магазинах без посредников и наценок.' },
  { step:4, title:'Доставляем тебе', text:'Мы организуем доставку в твой город быстро и безопасно.' },
]

// CATEGORIES
const categorySlides = [
  { title:'Аксессуары', desc:'Сумки, ремни и игрушки от Max Mara, Coach, Pop Mart и других официальных брендов.' },
  { title:'Одежда', desc:'Только оригинальные вещи от Nike, Adidas, Supreme и т.д.' },
  { title:'Обувь', desc:'Хиты от New Balance, Jacquemus и других.' },
]
const currentCat = ref(0)
function prevCat(){ currentCat.value = (currentCat.value + categorySlides.length -1) % categorySlides.length }
function nextCat(){ currentCat.value = (currentCat.value +1) % categorySlides.length }

// PRINCIPLES
const origBlocks = [
  { title:'Только оригиналы', text:'Работаем напрямую с официальными магазинами. Никаких подделок, никаких посредников.', open:false },
  { title:'Честные цены', text:'Прямая закупка без посредников. Цены на 20-45% ниже, чем в розницах.', open:false },
  { title:'Индивидуальный подход', text:'Не нашел нужную модель? Пришли фото — мы найдём и доставим.', open:false },
  { title:'Прозрачность и уверенность', text:'Открытые условия на каждом этапе без сюрпризов.', open:false },
]
function toggleOrig(b){ b.open = !b.open }

// BESTSELLERS
const bests = computed(() => store.filteredProducts.slice(0,2))
const bestIndex = ref(0)
function prevBest(){ bestIndex.value = (bestIndex.value + bests.value.length -1) % bests.value.length }
function nextBest(){ bestIndex.value = (bestIndex.value +1) % bests.value.length }
function toggleFav(p){ /* вызвать store.addToFavorites/remove... */ }

// REQUEST FORM
const request = ref({ name:'', email:'', sku:'', file:null, agree:false })
function onFileChange(e){ request.value.file = e.target.files[0] }
function onSubmitRequest(){ alert('Запрос отправлен!') }

// TESTIMONIALS
const testimonials = [
  { id:1, from:'user', text:'Привет! Я получил заказ, все отлично 🔥 Спасибо большое!' },
  { id:2, from:'shop', text:'Привет! Круто! Мы очень рады 🙌 Как вам продукт и доставка?' },
  { id:3, from:'user', text:'Кроссовки оригинальные, упаковка отличная.' },
  { id:4, from:'shop', text:'Спасибо большое за ваш отзыв! 🙏' },
]
const testimonialsAuthor = { avatar:'', name:'Борис Шепелев', year:'2025' }

// FAQ
const faqs = [
  { question:'Как я могу быть уверен, что товар оригинальный?', answer:'Все товары мы закупаем только в официальных магазинах.', open:false },
  { question:'Как заказать товар, которого нет на сайте?', answer:'Отправьте фото или артикул в запросе выше.', open:false },
  { question:'Какие способы оплаты доступны?', answer:'Мы принимаем карты, Apple Pay, Google Pay.', open:false },
  { question:'Сколько времени занимает доставка?', answer:'Обычно 2–10 дней в зависимости от региона.', open:false },
  { question:'Могу ли я вернуть товар, если он не подходит?', answer:'Да, в течение 14 дней после получения.', open:false },
  { question:'Какие бренды представлены на сайте?', answer:'Nike, Adidas, New Balance, Jacquemus и др.', open:false },
  { question:'Какие гарантии я получаю при заказе?', answer:'Гарантия оригинальности и возврат в течение 14 дней.', open:false },
  { question:'Как я могу посмотреть статус моего заказа?', answer:'В личном кабинете или через Telegram-бота.', open:false },
]
function toggleFaq(i){ faqs[i].open = !faqs[i].open }

onMounted(() => {
  store.fetchProducts()
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
  color: #fff;
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
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-100%);
  }
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

.btn-submit {
  padding: 8px;
  background: #000;
  color: #fff;
  border: none;
  border-radius: 4px;
}

/* TESTIMONIALS */
.testimonials {
  padding: 24px 16px;
  background: #f8f8f8;
}

.testimonials h2 {
  text-align: center;
  margin-bottom: 16px;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 320px;
  margin: 0 auto;
}

.message {
  padding: 8px;
  border-radius: 4px;
  max-width: 80%;
}

.message.user {
  background: #000;
  color: #fff;
  align-self: flex-end;
}

.message.shop {
  background: #fff;
  color: #000;
  align-self: flex-start;
}

.author {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
}

.author .avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

/* FAQ */
.faq {
  padding: 24px 16px;
}

.faq h2 {
  text-align: center;
  margin-bottom: 8px;
}

.questions {
  max-width: 480px;
  margin: 0 auto;
}

.question {
  margin-bottom: 8px;
}

.q-header {
  display: flex;
  justify-content: space-between;
  cursor: pointer;
  font-weight: bold;
}

.q-answer {
  padding: 8px 0;
}

/* адаптив */
@media (max-width: 600px) {
  .steps {
    grid-template-columns: 1fr;
  }
  .best-slider {
    flex-direction: column;
  }
}

</style>
