<template>
  <div class="home">
    <div class="line-vert"></div>
    <!-- HERO -->
    <section class="hero">
      <div class="hero-slide" :style="{ backgroundImage: `url(${ heroSlides[heroIndex].image })` }">
        <div class="hero-content">
          <h1 class="hero-text">Оригинальные бренды<br>и ничего лишнего</h1>
          <img class="hero-title" :src="heroSlides[heroIndex].title" alt="Название" />
          <div class="hero-controls">
            <div class="slide-div">
              <div class="slide-counter">
                {{ String(heroIndex + 1).padStart(2, '0') }}/{{ String(heroSlides.length).padStart(2, '0') }}
              </div>
              <div class="arrows">
                <button type="button" class="arrow-btn" @click="prevHero" aria-label="Назад">
                  <img :src="icon_arrow_red" alt="Arrow"/>
                </button>
                <button type="button" class="arrow-btn" @click="nextHero" aria-label="Вперёд"
                        style="width: 49px; border-left: 1px solid white;">
                  <img :src="icon_arrow_red" alt="Arrow" style="transform: rotate(180deg)"/>
                </button>
              </div>
            </div>
            <button type="button" class="btn-catalog" @click="goToCatalog('')">
              В каталог
              <img :src="icon_arrow_white" alt="Arrow"/>
            </button>
          </div>
        </div>
      </div>
      <div class="marquee">
        <div class="marquee-content">{{ runningText }}</div>
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section class="how-it-works">
      <h2>Как мы работаем</h2>
      <p>Выбирай нужные тебе товары - мы проверим их оригинальность, купим напрямую в официальных магазинах
        и доставим тебе без переплат и подделок. Все просто, прозрачно и быстро.</p>
      <div class="line-hor"></div>
      <div class="steps">
        <div v-for="step in workBlocks" :key="step.step" class="step">
          <div class="step-div-up">
            <div class="step-div">
              <p class="text-step">ШАГ {{ step.step }}</p>
              <img :src="step.img" alt="block img" />
            </div>
            <p class="text-title">{{ step.title }}</p>
          </div>
          <p class="text-description">{{ step.text }}</p>
        </div>
      </div>
    </section>

    <!-- CATEGORIES -->
    <section class="categories">
      <h2>Категории</h2>
      <div class="cat-slider">
        <div class="cat-slider-div">
          <button type="button" @click="prevCat" aria-label="Назад">
            <img :src="icon_arrow_red" alt="Arrow"/>
          </button>
          <button type="button" @click="nextCat" aria-label="Вперёд">
            <img :src="icon_arrow_red" alt="Arrow" style="transform: rotate(180deg)"/>
          </button>
        </div>
        <div class="cat-items" :style="{ transform: `translateX(calc(-${catIdx * 100}% + ${catIdx * 40}px + 30px))` }">
          <div class="cat-slide" v-for="block in catBlocks" :key="block.title">
            <img :src="block.img" alt="" />
            <h3>{{ block.title }}</h3>
            <p>{{ block.desc }}</p>
          </div>
        </div>
        <button type="button" class="btn-catalog" @click="goToCatalog(catBlocks[catIdx].title)">Каталог</button>
      </div>
    </section>

    <!-- PRINCIPLES -->
    <section class="principles">
      <div class="principle-div">
        <p class="principle-text">В YANDA.SHOP мы<br>делаем ставку на<br>оригинальность,<br>честность<br>и индивидуальный<br>подход.<br><br>
          Наши принципы просты:<br>только популярные<br>бренды, прозрачные<br>условия и забота о<br>вашем выборе. Здесь<br>ценят стиль, время и<br>доверие.</p>
      </div>
      <div v-for="block in origBlocks" :key="block.title" class="principle">
        <div class="principle-header">
          <h3>{{ block.title }}</h3>
          <img :src="block.img" alt="block img" />
        </div>
        <p class="principle-text">{{ block.text }}</p>
      </div>
    </section>

    <!-- BESTSELLERS -->
    <section class="bestsellers" v-if="bests.length">
      <h2>Бестселлеры</h2>
      <div class="best-slider">
        <div class="best-items" :style="{ transform: `translateX(-${bestIndex * 100}%)` }">
          <div class="best-item" v-for="p in bests" :key="p.variant_sku" @click="goToProduct(p)">
            <button type="button" class="fav-btn" @click.stop="toggleFav(p)">
              <img :src="store.isFavorite(p.color_sku) ? icon_favorites_black : icon_favorites_grey" alt="" />
            </button>
            <div class="product-image">
              <img :src="p.image" alt="product" />
            </div>
            <div class="product-info">
              <p class="product-brand">{{ p.brand }}</p>
              <p class="product-name">{{ p.name }}</p>
              <p class="product-price">от {{ formatPrice(p.price) }} ₽</p>
            </div>
          </div>
        </div>
        <div class="best-slider-div">
          <button type="button" @click="prevBest" aria-label="Назад" :disabled="bestIndex === 0">
            <img :src="bestIndex === 0 ? icon_arrow_grey : icon_arrow_red" alt="Arrow"/>
          </button>
          <button type="button" @click="nextBest" aria-label="Вперёд" :disabled="bestIndex === maxPage">
            <img :src="bestIndex === maxPage ? icon_arrow_grey : icon_arrow_red" alt="Arrow" style="transform: rotate(180deg)"/>
          </button>
        </div>
      </div>
      <button type="button" class="btn-catalog" @click="goToCatalogSales">Смотреть все</button>
    </section>

    <!-- REQUEST FORM -->
    <section class="request-form">
      <form @submit.prevent="onSubmitRequest">
        <div class="request-div">
          <h2>Не нашел что хотел?</h2>
          <p style="margin-bottom: 24px;">Загрузи изображение или добавь артикул товара, и мы выкупим это из официального магазина.</p>

          <input class="input-field" type="text" v-model="request.name" placeholder="Имя *" required/>
          <input class="input-field" type="email" v-model="request.email" placeholder="Почта *" required/>
          <input class="input-field" type="text" v-model="request.sku" placeholder="Артикул товара"/>

          <p>или</p>

          <label class="file-upload">
            <input type="file" @change="onFileChange" hidden />
            <div class="file-div">
              <div class="file-div-button">
                <img :src="icon_paper_clip" alt="paper clip" />
                <span class="file-text">{{ uploadedFileName || 'Приложи файл' }}</span>
              </div>
              <span class="file-size">макс. 10 MB</span>
            </div>
          </label>

          <label class="checkbox-label">
            <input type="checkbox" v-model="request.agree"/>
            <span>Я согласен на <u>обработку персональных данных</u></span>
          </label>
        </div>
        <button type="submit" class="btn-submit">Отправить запрос</button>
      </form>
    </section>

    <!-- TESTIMONIALS -->
    <section class="testimonials">
      <h2>Твой стиль, твои отзывы</h2>
      <div v-if="!store.reviews.length" class="no-reviews">
        Отзывов пока нет.
      </div>
      <div v-else class="carousel" ref="carousel">
        <div class="review-items" :style="{width: `${store.reviews.length * 100}%`,
                                           transform: `translateX(${offsetPercent}% )`,
                                           height: carouselHeight + 'px'}">
          <div class="slide" v-for="(rev, i) in store.reviews" :key="i" :style="{ flex: `0 0 ${100 / store.reviews.length}%` }">
            <div class="review">
              <p class="user-text">{{ rev.client_text1 }}</p>
              <div class="photos">
                <img v-for="url in rev.photo_urls" :key="url" :src="url" alt="photo" @load="updateCarouselHeight"/>
              </div>
              <p class="shop-text">{{ rev.shop_response }}</p>
              <p v-if="rev.client_text2?.trim()" class="user-text">{{ rev.client_text2 }}</p>
              <div class="meta">
                <div class="review-header">
                  <img class="avatar" :src="icon_default_avatar_white" alt="аватар"/>
                  <span class="client-name">{{ rev.client_name }},</span>
                  <span class="review-date">{{ new Date(rev.created_at).toLocaleDateString('ru-RU', { month:'2-digit', year:'numeric' }) }}</span>
                </div>
                <a :href="rev.link_url" target="_blank">
                  Смотреть
                  <img :src="icon_arrow_black" alt="Arrow" style="transform: rotate(180deg)"/>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="carousel-div">
        <button type="button" @click="prev" aria-label="Назад">
          <img :src="icon_arrow_red" alt="Arrow"/>
        </button>
        <button type="button" @click="next" aria-label="Вперёд">
          <img :src="icon_arrow_red" alt="Arrow" style="transform: rotate(180deg)"/>
        </button>
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
    </section>
  </div>
  <div class="line-hor"></div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

import icon_default_avatar_white from '@/assets/images/default_avatar_white.svg'
import icon_work_1 from '@/assets/images/work_1.svg'
import icon_work_2 from '@/assets/images/work_2.svg'
import icon_work_3 from '@/assets/images/work_3.svg'
import icon_work_4 from '@/assets/images/work_4.svg'
import icon_cat_1 from '@/assets/images/cat_1.png'
import icon_cat_2 from '@/assets/images/cat_2.png'
import icon_cat_3 from '@/assets/images/cat_3.png'
import icon_plus_1 from '@/assets/images/plus_1.svg'
import icon_plus_2 from '@/assets/images/plus_2.svg'
import icon_plus_3 from '@/assets/images/plus_3.svg'
import icon_plus_4 from '@/assets/images/plus_4.svg'
import icon_faq_plus from '@/assets/images/faq_plus.svg'
import icon_minus_red from '@/assets/images/minus_red.svg'
import icon_arrow_red from '@/assets/images/arrow_red.svg'
import icon_arrow_grey from '@/assets/images/arrow_grey.svg'
import icon_arrow_black from '@/assets/images/arrow_black.svg'
import icon_arrow_white from '@/assets/images/arrow_white.svg'
import icon_favorites_grey from "@/assets/images/favorites_grey.svg";
import icon_favorites_black from "@/assets/images/favorites_black.svg";
import icon_paper_clip from "@/assets/images/paper_clip.svg";
import icon_hero1_text from "@/assets/images/hero1_text.svg";
import icon_hero2_text from "@/assets/images/hero2_text.svg";
import icon_hero3_text from "@/assets/images/hero3_text.svg";
import icon_hero4_text from "@/assets/images/hero4_text.svg";
import icon_hero1 from "@/assets/images/hero1.png";
import icon_hero2 from "@/assets/images/hero2.png";
import icon_hero3 from "@/assets/images/hero3.png";
import icon_hero4 from "@/assets/images/hero4.png";
import about_text_logo from "@/assets/images/about_text_logo.svg";


const store = useStore()
const router = useRouter()

const heroIndex = ref(0)
const openedFaq = ref(null);
const idx = ref(0)
const carousel = ref(null)
const carouselHeight = ref(0)
const uploadedFileName = ref('')

const offsetPercent = computed(() =>
  ((store.reviews.length - 1) / 2 - idx.value) * (100 / store.reviews.length)
)

function prev() {
  if (!store.reviews.length) return
  idx.value = (idx.value + store.reviews.length - 1) % store.reviews.length
}

function next() {
  if (!store.reviews.length) return
  idx.value = (idx.value + 1) % store.reviews.length
}

function updateCarouselHeight() {
  nextTick(() => {
    const reviews = carousel.value?.querySelectorAll('.review') || []
    const current = reviews[idx.value]
    if (current) {
      carouselHeight.value = current.offsetHeight
    }
  })
}

// Hero
const heroSlides = [
  { image: icon_hero1, title: icon_hero1_text },
  { image: icon_hero2, title: icon_hero2_text },
  { image: icon_hero3, title: icon_hero3_text },
  { image: icon_hero4, title: icon_hero4_text }
]

const runningText = 'Puma //_Future_Vintage_Capsule     • sale'

function prevHero() {
  heroIndex.value = (heroIndex.value - 1 + heroSlides.length) % heroSlides.length
}

function nextHero() {
  heroIndex.value = (heroIndex.value + 1) % heroSlides.length
}

// How it works
const workBlocks = [
  { step: 1, img: icon_work_1, title: 'Ты выбираешь',             text: 'Найди товар в каталоге или пришли нам фотографию желаемой модели.' },
  { step: 2, img: icon_work_2, title: 'Мы проверяем на оригинал', text: 'Мы проверяем наличие, подлинность и цену в официальных источниках.' },
  { step: 3, img: icon_work_3, title: 'Покупаем напрямую',        text: 'Мы заказываем товары в официальных магазинах без посредников и наценок.' },
  { step: 4, img: icon_work_4, title: 'Доставляем тебе',          text: 'Мы организуем доставку в твой город быстро и безопасно.' },
]

// Categories
const catIdx = ref(0)

const catBlocks = [
  { img: icon_cat_1, title: 'Аксессуары', desc: 'Сумки, ремни и игрушки от Max Mara, Coach, Pop Mart и других официальных брендов.' },
  { img: icon_cat_2, title: 'Обувь',      desc: 'Кроссовки, лоферы и сапоги от New Balance, Clarks, Nike и других официальных брендов.' },
  { img: icon_cat_3, title: 'Одежда',     desc: 'Базовая и акцентная одежда от Jacquemus, Fear of God и других официальных брендов.' },
]

function prevCat() {
  catIdx.value = (catIdx.value + catBlocks.length - 1) % catBlocks.length
}

function nextCat() {
  catIdx.value = (catIdx.value + 1) % catBlocks.length
}

// Principles
const origBlocks = [
  { img: icon_plus_1, title: 'Только оригиналы',           text: 'Работаем напрямую с официальными магазинами. Никаких подделок, никаких посредников.' },
  { img: icon_plus_2, title: 'Честные цены',               text: 'Прямая закупка без посредников. Цены на 20-45% ниже, чем в розничных магазинах — без переплат и комиссий.' },
  { img: icon_plus_3, title: 'Индивидуальный подход',      text: 'Не нашел нужную модель? Присылай фото — найдем и доставим именно то, что тебе нужно.' },
  { img: icon_plus_4, title: 'Прозрачность и уверенность', text: 'Простые и открытые условия на каждом этапе. Ты точно знаешь, что покупаешь, и получаешь только актуальные, аутентичные коллекции — никаких сюрпризов.' },
]

// Bestsellers
const bests = computed(() => {
  // сгруппировать
  const groups = {}
  store.products.forEach(p => {
    if (!groups[p.color_sku]) groups[p.color_sku] = { variants: [], totalSales: 0 }
    groups[p.color_sku].variants.push(p)
    groups[p.color_sku].totalSales += p.count_sales || 0
  })
  // собрать массив групп с «репрезентативным» вариантом
  const arr = Object.values(groups).map(({ variants, totalSales }) => {
    // выбираем вариант с минимальной ценой (или любой другой логику)
    const rep = variants.reduce((prev, cur) => prev.price <= cur.price ? prev : cur)
    return { ...rep, totalSales }
  })
  // сортируем по сумме продаж ↓, при равных — по цене ↓
  const sorted = arr.sort((a, b) => (b.totalSales - a.totalSales) || (b.price - a.price))
  // оставляем только топ-24
  return sorted.slice(0, 24)
})

const maxPage = computed(() => Math.ceil(bests.value.length / 2) - 1)
const bestIndex = ref(0)

function prevBest() {
  if (bestIndex.value > 0) bestIndex.value--
}

function nextBest() {
  if (bestIndex.value < maxPage.value) bestIndex.value++
}

// 3) Переход на страницу товара
function goToProduct(p) {
  router.push({
    name: 'ProductDetail',
    params: { variant_sku: p.variant_sku },
    query: { category: p.category }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 4) Переход на страницу каталога
function goToCatalog(cat) {
  store.selectedCategory = cat
  router.push({ name: 'Catalog' })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 4) Переход на страницу бестселлеров каталога
function goToCatalogSales() {
  store.selectedCategory = ''
  router.push({ name: 'Catalog', query: { sort: 'sales_desc' } })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Сохранение в избранное оставляем, но вешаем .stop на клик, чтобы не перегружать маршрут
function toggleFav(p) {
  store.isFavorite(p.color_sku) ? store.removeFromFavorites(p.color_sku) : store.addToFavorites(p.color_sku)
}

// Request form
const request = ref({ name:'', email:'', sku:'', file:null, agree:false })

function onFileChange(e) {
  const file = e.target.files[0];
  if (file) {
    request.value.file = file
    uploadedFileName.value = file.name;
  } else {
    uploadedFileName.value = '';
  }
}

function onSubmitRequest() {
  if (!request.value.agree) {
    alert("Нужно согласиться с обработкой данных")
    return
  }
  const file = request.value.file
  if (file && file.size > 10 * 1024 * 1024) {
    alert("Файл не должен быть больше 10 МБ")
    return
  }

  const fd = new FormData()
  fd.append("name",  request.value.name)
  fd.append("email", request.value.email)
  fd.append("sku",   request.value.sku)
  if (file) fd.append("file", file)

  store.createRequest(fd)
    .then(() => {
      alert("Запрос успешно отправлен")
      // сброс формы
      request.value = { name:'', email:'', sku:'', file:null, agree:false }
      uploadedFileName.value = ''
    })
    .catch(err => {
      alert(err.response?.data?.error || err.message)
    })
}

// FAQ
const faqItems = computed(() => {
  const items = []
  const allKeys = Object.keys(store.parameters)
  const faqNumbers = [ ...new Set(allKeys
      .filter(key => key.startsWith('faq_question_') || key.startsWith('faq_answer_'))
      .map(key => parseInt(key.replace(/\D+/g, '')))
    )
  ]
  faqNumbers.sort((a, b) => a - b).forEach(num => {
    items.push({
      id: num,
      question: store.parameters[`faq_question_${num}`] || `Вопрос ${num}`,
      answer: store.parameters[`faq_answer_${num}`] || 'Ответ не найден',
    })
  })
  return items
});

// закрывает все пункты кроме переданного
function toggleFaq(id) {
  openedFaq.value = openedFaq.value === id ? null : id;
}

function formatPrice(val) {
  return String(val).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

watch(idx, updateCarouselHeight)

let intervalId = null
onMounted(() => {
  // каждую 5-ю секунду переключаем слайд
  intervalId = setInterval(() => {
    nextHero()
  }, 5_000)
})

onBeforeUnmount(() => {
  clearInterval(intervalId)
})

</script>

<style scoped lang="scss">

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
.home {
  /* HERO */
  .hero {
    position: relative;
    height: 739px;
    overflow: hidden;
    z-index: 20;
    .hero-slide {
      position: relative;
      width: 100%;
      height: 100%;
      background-size: cover;
      background-position: center;
      transition: background-image 0.5s ease-in-out;
    }
    .hero-content {
      position: absolute;
      top: 66px;
      width: 100%;
      height: calc(100% - 108px);
      color: $white-100;
      .hero-text {
        margin: 0;
        padding: 16px 10px 8px;
        border-bottom: 1px solid $white-100;
        font-size: 32px;
        font-weight: 500;
        line-height: 90%;
        letter-spacing: -1.28px;
      }
      .hero-title {
        position: absolute;
        height: 64px;
        bottom: 50%;
        mix-blend-mode: exclusion;
      }
      .hero-controls {
        display: flex;
        position: absolute;
        align-items: center;
        justify-content: center;
        bottom: 0;
        width: 100%;
        height: 150px;
        border-top: 1px solid $white-100;
        .slide-div {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          width: 50%;
          .slide-counter {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100px;
            height: 50px;
            background: $black-100;
            border-radius: 4px 4px 0 0;
            border-bottom: 1px solid $white-100;
            font-family: Bounded;
            font-size: 20px;
            font-weight: 300;
            line-height: 90%;
            letter-spacing: -1px;
          }
          .arrows {
            display: flex;
            background: $black-100;
            border-radius: 0 0 4px 4px;
            .arrow-btn {
              display: flex;
              align-items: center;
              justify-content: center;
              border: none;
              background: none;
              width: 50px;
              height: 50px;
              cursor: pointer;
              img {
                width: 24px;
                height: 24px;
                object-fit: cover;
              }
            }
          }
        }
        .btn-catalog {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          width: calc(50% - 1px);
          height: 100%;
          gap: 8px;
          border: none;
          border-left: 1px solid $white-100;
          background: $black-25;
          backdrop-filter: blur(8px);
          color: $white-100;
          font-size: 16px;
          line-height: 100%;
          letter-spacing: -0.64px;
          cursor: pointer;
          img {
            width: 24px;
            height: 24px;
            object-fit: cover;
          }
        }
      }
    }
    .marquee {
      position: absolute;
      bottom: 0;
      width: 100%;
      background: $black-100;
      overflow: hidden;
      .marquee-content {
        display: inline-block;
        padding: 12px 0;
        color: $grey-90;
        font-family: Bounded;
        font-size: 18px;
        font-weight: 250;
        line-height: 100%;
        letter-spacing: -0.9px;
        animation: marquee 15s linear infinite;
      }
    }
    @keyframes marquee {
      from { transform: translateX(150%); }
      to   { transform: translateX(-100%); }
    }
  }

  /* HOW IT WORKS */
  .how-it-works {
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 20;
    h2 {
      margin: 96px 0 40px;
      text-align: center;
      font-family: Bounded;
      font-weight: 500;
      font-size: 24px;
      line-height: 90%;
      letter-spacing: -0.72px;
    }
    p {
      margin: 0 0 24px;
      padding: 0 10px;
      font-size: 15px;
      line-height: 110%;
      letter-spacing: -0.6px;
    }
    .steps {
      display: flex;
      flex-direction: column;
      .step {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 10px;
        height: 280px;
        border-bottom: 1px solid $white-100;
        background-color: $grey-90;
        .step-div-up {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          .step-div {
            display: flex;
            flex-direction: column;
            gap: 24px;
            .text-step {
              margin: 0;
              padding: 0;
              font-family: Manrope-SemiBold;
              font-size: 16px;
              line-height: 80%;
              letter-spacing: -0.64px;
            }
            img {
              width: 60px;
              height: 60px;
              object-fit: cover;
            }
          }
          .text-title {
            margin: 0;
            padding: 0;
            width: 50%;
            font-family: Bounded;
            font-size: 26px;
            font-weight: 250;
            line-height: 90%;
            letter-spacing: -1.56px;
          }
        }
        .text-description {
          margin: 0;
          padding: 0;
          font-size: 16px;
          line-height: 110%;
          letter-spacing: -0.64px;
        }
      }
    }
  }

  /* CATEGORIES */
  .categories {
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 20;
    h2 {
      margin: 96px 0 40px;
      text-align: center;
      font-family: Bounded;
      font-weight: 500;
      font-size: 24px;
      line-height: 90%;
      letter-spacing: -0.72px;
    }
    .cat-slider {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      padding: 24px 0 0;
      gap: 24px;
      border-radius: 4px;
      background-color: $grey-95;
      overflow: hidden;
      .cat-slider-div {
        display: flex;
        align-items: center;
        padding: 0 10px;
        width: calc(100% - 20px);
        gap: 10px;
        button {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 8px 12px;
          width: 100%;
          height: 30px;
          border: none;
          background-color: $white-100;
          border-radius: 64px;
          cursor: pointer;
          img {
            width: 16px;
            height: 16px;
            object-fit: cover;
          }
        }
      }
      .cat-items {
        display: grid;
        grid-auto-flow: column;
        grid-auto-columns: calc(100% - 60px);
        gap: 20px;
        transition: transform 0.25s ease-in-out;
        .cat-slide {
          display: flex;
          flex-direction: column;
          padding: 0 10px;
          gap: 8px;
          text-align: center;
          img {
            margin-bottom: 8px;
            width: 100%;
            height: auto;
          }
          h3 {
            margin: 0;
            font-family: Bounded;
            font-size: 24px;
            font-weight: 250;
            line-height: 80%;
            letter-spacing: -1.2px;
          }
          p {
            margin: 0;
            color: $black-60;
            font-size: 15px;
            line-height: 110%;
            letter-spacing: -0.6px;
          }
        }
      }
    }
    .btn-catalog {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 24px;
      width: 100%;
      height: 56px;
      border: none;
      background-color: $grey-20;
      color: $white-100;
      border-radius: 4px;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      cursor: pointer;
    }
  }

  /* PRINCIPLES */
  .principles {
    display: flex;
    flex-direction: column;
    position: relative;
    margin-top: 96px;
    z-index: 20;
    .principle-div {
      display: flex;
      padding: 20px 10px;
      height: 280px;
      background-image: url('@/assets/images/principle.png');
      background-size: 125% auto;
      background-position: top;
      background-repeat: no-repeat;
      .principle-text {
        margin: 0;
        width: 50%;
        color: $grey-95;
        font-size: 16px;
        line-height: 110%;
        letter-spacing: -0.64px;
      }
    }
    .principle {
      display: flex;
      flex-direction: column;
      padding: 24px 10px;
      background-color: $grey-87;
      border-bottom: 1px solid $white-100;
      .principle-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin: 0 0 40px;
        h3 {
          margin: 0;
          width: 210px;
          font-family: Bounded;
          font-size: 26px;
          font-weight: 250;
          line-height: 90%;
          letter-spacing: -1.56px;
        }
        img {
          width: 30px;
          height: 30px;
          object-fit: cover;
        }
      }
      .principle-text {
        margin: 0;
        font-size: 16px;
        line-height: 110%;
        letter-spacing: -0.64px;
      }
    }
  }

  /* BESTSELLERS */
  .bestsellers {
    display: flex;
    flex-direction: column;
    position: relative;
    h2 {
      margin: 96px 0 0;
      text-align: center;
      font-family: Bounded;
      font-weight: 500;
      font-size: 24px;
      line-height: 90%;
      letter-spacing: -0.72px;
      z-index: 20;
    }
    .best-slider {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;
      overflow: hidden;
      .best-items {
        display: grid;
        grid-auto-flow: column;
        grid-auto-columns: 50%;
        margin-top: 40px;
        transition: all 0.25s ease-in-out;
        .best-item {
          display: flex;
          box-sizing: border-box;
          flex-direction: column;
          position: relative;
          min-width: 0;
          background-color: $grey-89;
          cursor: pointer;
          transition: transform 0.25s ease-in-out;
          .fav-btn {
            display: flex;
            position: absolute;
            padding: 0;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            width: 24px;
            height: 24px;
            cursor: pointer;
            img {
              width: 24px;
              height: 24px;
              object-fit: cover;
            }
          }
          .product-image {
            display: flex;
            padding: 40px 24px;
            height: 100%;
            img {
              width: 100%;
              object-fit: cover;
            }
          }
          .product-info {
            display: flex;
            flex-direction: column;
            padding: 10px 10px 16px;
            background-color: $grey-87;
            .product-brand {
              margin: 0;
              font-size: 12px;
              line-height: 100%;
              letter-spacing: -0.48px;
              color: $black-60;
            }
            .product-name {
              margin: 4px 0 12px;
              font-family: Manrope-SemiBold;
              font-size: 15px;
              line-height: 100%;
              letter-spacing: -0.6px;
              color: $black-100;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }
            .product-price {
              margin: 0;
              font-size: 15px;
              line-height: 80%;
              letter-spacing: -0.6px;
              color: $grey-20;
            }
          }
        }
      }
      .best-slider-div {
        display: flex;
        align-items: center;
        padding: 0 10px;
        width: calc(100% - 20px);
        gap: 10px;
        button {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 8px 12px;
          width: 100%;
          height: 30px;
          border: none;
          background-color: $white-100;
          border-radius: 64px;
          cursor: pointer;
          img {
            width: 16px;
            height: 16px;
            object-fit: cover;
          }
        }
        button[disabled] {
          cursor: default;
          img {
            opacity: 0.4;
          }
        }
      }
    }
    .btn-catalog {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-top: 32px;
      padding: 0 24px;
      width: 100%;
      height: 56px;
      border: none;
      background-color: $grey-20;
      color: $white-100;
      border-radius: 4px;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      cursor: pointer;
      z-index: 20;
    }
  }

  /* REQUEST FORM */
  .request-form {
    display: flex;
    flex-direction: column;
    position: relative;
    margin-top: 96px;
    padding: 203px 10px 40px;
    background-image: url('@/assets/images/request-form.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    z-index: 20;
    form {
      display: flex;
      flex-direction: column;
      .request-div {
        display: flex;
        flex-direction: column;
        padding: 24px 10px;
        border-radius: 4px;
        background-color: $black-70;
        backdrop-filter: blur(10px);
        h2 {
          margin: 0 0 16px;
          text-align: center;
          color: $grey-95;
          font-family: Bounded;
          font-weight: 500;
          font-size: 24px;
          line-height: 90%;
          letter-spacing: -0.72px;
        }
        p {
          margin: 0 0 16px;
          text-align: center;
          color: $grey-90;
          font-size: 15px;
          line-height: 110%;
          letter-spacing: -0.6px;
        }
        .input-field {
          margin-bottom: 15px;
          padding: 21px 10px 8px;
          border: none;
          background-color: transparent;
          outline: none;
          border-bottom: 1px solid $white-60;
          color: $white-100;
          font-size: 15px;
          line-height: 100%;
          letter-spacing: -0.6px;
          &::placeholder {
            color: $white-40;
          }
        }
        .file-upload {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 10px;
          border: 1px solid $white-40;
          border-radius: 4px;
          background-color: transparent;
          cursor: pointer;
          .file-div {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            .file-div-button {
              display: flex;
              align-items: center;
              width: calc(100% - 62px);
              gap: 8px;
              img {
                width: 24px;
                height: 24px;
                object-fit: cover;
              }
              .file-text {
                width: calc(100% - 40px);
                color: $white-60;
                font-family: Bounded;
                font-size: 18px;
                font-weight: 250;
                line-height: 100%;
                letter-spacing: -0.9px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
              }
            }
            .file-size {
              color: $white-40;
              font-size: 12px;
              line-height: 100%;
              letter-spacing: -0.48px;
            }
          }
        }
        .checkbox-label {
          display: flex;
          align-items: center;
          margin-top: 24px;
          gap: 5px;
          color: $white-60;
          font-size: 16px;
          line-height: 100%;
          letter-spacing: -0.64px;
          cursor: pointer;
          input[type="checkbox"] {
            appearance: none;
            margin: 0;
            width: 20px;
            height: 20px;
            border: 1px solid $white-40;
            background-color: transparent;
            border-radius: 2px;
            cursor: pointer;
            position: relative;
          }
          input[type="checkbox"]:checked::after {
            content: "";
            position: absolute;
            top: 0;
            left: 5px;
            width: 6px;
            height: 10px;
            border: solid $white-100;
            border-width: 0 2px 2px 0;
            transform: rotate(45deg);
          }
          u {
            text-decoration: underline;
          }
        }
      }
      .btn-submit {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 24px;
        width: 100%;
        height: 56px;
        border: none;
        background-color: $white-80;
        color: $black-100;
        border-radius: 4px;
        font-size: 16px;
        line-height: 100%;
        letter-spacing: -0.64px;
        cursor: pointer;
      }
    }
  }

  /* TESTIMONIALS */
  .testimonials {
    display: flex;
    flex-direction: column;
    position: relative;
    padding: 32px 0;
    z-index: 20;
    h2 {
      margin: 64px 0 40px;
      text-align: center;
      font-family: Bounded;
      font-weight: 500;
      font-size: 24px;
      line-height: 90%;
      letter-spacing: -0.72px;
    }
    .no-reviews {
      font-style: italic;
    }
    .carousel {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      width: 100%;
      gap: 32px;
      overflow: hidden;
      transition: height 0.25s ease-in-out;
      .review-items {
        display: flex;
        transition: transform 0.25s ease-in-out;
        .slide {
          flex: 0 0 100%;
          box-sizing: border-box;
          background-color: $grey-90;
          .review {
            display: flex;
            flex-direction: column;
            padding: 20px;
            gap: 20px;
            border-radius: 4px;
            .user-text, .shop-text {
              margin: 0;
              padding: 8px;
              border-radius: 4px;
              font-size: 16px;
              line-height: 110%;
              letter-spacing: -0.64px;
            }
            .user-text {
              background-color: $black-100;
              color: $white-100;
            }
            .shop-text {
              background-color: $white-100;
              color: $black-100;
            }
            .photos {
              img {
                width: 155px;
                height: auto;
                margin-right: 10px;
                border-radius: 4px;
              }
            }
            .meta {
              display: flex;
              align-items: center;
              justify-content: space-between;
              .review-header {
                display: flex;
                align-items: center;
                gap: 8px;
                .avatar {
                  width: 56px;
                  height: 56px;
                  border-radius: 56px;
                  object-fit: cover;
                }
                .client-name {
                  color: $red-active;
                  font-family: Manrope-SemiBold;
                  font-size: 16px;
                  line-height: 100%;
                  letter-spacing: -0.64px;
                }
                .review-date {
                  color: $black-100;
                  font-family: Manrope-SemiBold;
                  font-size: 16px;
                  line-height: 100%;
                  letter-spacing: -0.64px;
                }
              }
              a {
                display: flex;
                align-items: center;
                gap: 4px;
                text-decoration: none;
                color: inherit;
                font-size: 16px;
                line-height: 100%;
                letter-spacing: -0.64px;
                img {
                  width: 24px;
                  height: 24px;
                  object-fit: cover;
                }
              }
            }
          }
        }
      }
    }
    .carousel-div {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-top: 32px;
      gap: 10px;
      button {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 8px 12px;
        width: 30px;
        height: 30px;
        border: none;
        background-color: $white-100;
        border-radius: 100%;
        cursor: pointer;
        img {
          width: 16px;
          height: 16px;
          object-fit: cover;
        }
      }
    }
  }

  /* FAQ */
  .faq {
    display: flex;
    flex-direction: column;
    position: relative;
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
      margin: 0 auto 32px;
      font-size: 16px;
      line-height: 110%;
      letter-spacing: -0.64px;
    }
    &-list {
      display: flex;
      flex-direction: column;
      margin: 0 0 64px;
      gap: 4px;
      border-radius: 4px;
    }
    &-item {
      background-color: $white-100;
      border-radius: 4px;
      overflow: hidden;
      cursor: pointer;
    }
    &-header {
      display: flex;
      align-items: center;
      padding: 18px 10px;
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

  /* RESPONSIVE */
  @media (max-width: 600px) {
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
