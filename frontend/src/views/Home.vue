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
          <div @click="goToCatalog('')" class="btn-catalog">В каталог →</div>
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
      <div class="steps">
        <div v-for="step in workSteps" :key="step.step" class="step">
          <div class="icon-placeholder">Иконка {{ step.step }}</div>
          <p class="text-step">ШАГ {{ step.step }}</p>
          <p class="text-title">{{ step.title }}</p>
          <p class="text-description">{{ step.text }}</p>
        </div>
      </div>
    </section>

    <!-- CATEGORIES -->
    <section class="categories">
      <h2>Категории</h2>
      <div class="cat-slider">
        <div class="cat-slider-div">
          <button @click="prevCat" aria-label="Назад">←</button>
          <button @click="nextCat" aria-label="Вперёд">→</button>
        </div>
        <div class="cat-slide">
          <!-- вставить картинку категории -->
          <div class="image-placeholder">Изображение {{ categorySlides[currentCat].title }}</div>
          <h3>{{ categorySlides[currentCat].title }}</h3>
          <p>{{ categorySlides[currentCat].desc }}</p>
          <div @click="goToCatalog(categorySlides[currentCat].title)" class="btn-catalog">Каталог</div>
        </div>
      </div>
    </section>

    <!-- PRINCIPLES -->
    <section class="principles">
      <div class="principle-div">
        В YANDA.SHOP мы делаем ставку на оригинальность, честность и индивидуальный подход.<br><br>
        Наши принципы просты: только популярные бренды, прозрачные условия и забота о вашем выборе. Здесь ценят  стиль, время и доверие.
      </div>
      <div v-for="block in origBlocks" :key="block.title" class="principle">
        <h3 class="principle-header">
          {{ block.title }}
          <span class="principle-icon">+</span>
        </h3>
        <p class="principle-text">{{ block.text }}</p>
      </div>
    </section>

    <!-- BESTSELLERS -->
    <section class="bestsellers" v-if="bests.length">
      <h2>Бестселлеры</h2>
      <div class="best-slider">
        <div class="best-items">
          <div class="best-item" v-for="p in visibleBests" :key="p.variant_sku" @click="goToProduct(p)">
            <button class="fav-btn" @click.stop="toggleFav(p)">
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
          <button @click="prevBest" aria-label="Назад" :disabled="bestIndex === 0">
            <img :src="bestIndex === 0 ? icon_arrow_grey : icon_arrow_red" alt="Arrow"/>
          </button>
          <button @click="nextBest" aria-label="Вперёд">
            <img :src="icon_arrow_red" alt="Arrow" style="transform: rotate(180deg)"/>
          </button>
        </div>
      </div>
      <div @click="goToCatalogSales" class="btn-catalog">
        Смотреть все
      </div>
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
      <div v-if="!store.reviews.length" class="no-reviews">
        Отзывов пока нет.
      </div>
      <div v-else class="carousel">
        <transition name="slide" mode="out-in">
          <div class="slide" :key="current.created_at">
            <div class="review">
              <p class="user-text">{{ current.client_text1 }}</p>
              <div class="photos">
                <img v-for="url in current.photo_urls" :key="url" :src="url" alt="photo"/>
              </div>
              <p class="shop-text">{{ current.shop_response }}</p>
              <p v-if="current.client_text2?.trim()" class="user-text">{{ current.client_text2 }}</p>
              <div class="meta">
                <div class="review-header">
                  <img class="avatar" :src="icon_default_avatar_white" alt="аватар"/>
                  <span class="client-name">{{ current.client_name }},</span>
                  <span class="review-date">{{ new Date(current.created_at).toLocaleDateString('ru-RU', { month:'2-digit', year:'numeric' }) }}</span>
                </div>
                <a :href="current.link_url" target="_blank">
                  Смотреть
                  <img :src="icon_arrow_black" alt="Arrow" style="transform: rotate(180deg)"/>
                </a>
              </div>
            </div>
          </div>
        </transition>
        <div class="carousel-div">
          <button @click="prev" aria-label="Назад">
            <img :src="icon_arrow_red" alt="Arrow"/>
          </button>
          <button @click="next" aria-label="Вперёд">
            <img :src="icon_arrow_red" alt="Arrow" style="transform: rotate(180deg)"/>
          </button>
        </div>
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
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

import icon_default_avatar_white from '@/assets/images/default_avatar_white.svg'
import icon_faq_plus from '@/assets/images/faq_plus.svg'
import icon_minus_red from '@/assets/images/minus_red.svg'
import icon_arrow_red from '@/assets/images/arrow_red.svg'
import icon_arrow_grey from '@/assets/images/arrow_grey.svg'
import icon_arrow_black from '@/assets/images/arrow_black.svg'
import icon_favorites_grey from "@/assets/images/favorites_grey.svg";
import icon_favorites_black from "@/assets/images/favorites_black.svg";

const store = useStore()
const router = useRouter()

const idx = ref(0)
const heroIndex = ref(0)
const openedFaq = ref(null);
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
  { step: 1, title: 'Ты выбираешь',             text: 'Найди товар в каталоге или пришли нам фотографию желаемой модели.' },
  { step: 2, title: 'Мы проверяем на оригинал', text: 'Мы проверяем наличие, подлинность и цену в официальных источниках.' },
  { step: 3, title: 'Покупаем напрямую',        text: 'Мы заказываем товары в официальных магазинах без посредников и наценок.' },
  { step: 4, title: 'Доставляем тебе',          text: 'Мы организуем доставку в твой город быстро и безопасно.' },
]

// Categories
const currentCat = ref(0)

const categorySlides = [
  { title: 'Аксессуары', desc: 'Сумки, ремни и игрушки от Max Mara, Coach, Pop Mart и других официальных брендов.' },
  { title: 'Одежда',     desc: 'Только оригинальные вещи от Nike, Adidas, Supreme и т.д.' },
  { title: 'Обувь',      desc: 'Хиты от New Balance, Jacquemus и других.' },
]

function prevCat() {
  currentCat.value = (currentCat.value + categorySlides.length - 1) % categorySlides.length
}

function nextCat() {
  currentCat.value = (currentCat.value + 1) % categorySlides.length
}

// Principles
const origBlocks = [
  { title: 'Только оригиналы',           text: 'Работаем напрямую с официальными магазинами. Никаких подделок, никаких посредников.' },
  { title: 'Честные цены',               text: 'Прямая закупка без посредников. Цены на 20-45% ниже, чем в розничных магазинах — без переплат и комиссий.' },
  { title: 'Индивидуальный подход',      text: 'Не нашел нужную модель? Присылай фото — найдем и доставим именно то, что тебе нужно.' },
  { title: 'Прозрачность и уверенность', text: 'Простые и открытые условия на каждом этапе. Ты точно знаешь, что покупаешь, и получаешь только актуальные, аутентичные коллекции — никаких сюрпризов.' },
]

// Bestsellers
const perSlide  = 2
const bestIndex = ref(0)

// 1) Группируем по color_sku, суммируем count_sales, берём «представительный» вариант и сортируем
const bests = computed(() => {
  // сгруппировать
  const groups = {}
  store.products.forEach(p => {
    if (!groups[p.color_sku]) {
      groups[p.color_sku] = { variants: [], totalSales: 0 }
    }
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
  return arr.sort((a, b) =>
    (b.totalSales - a.totalSales) || (b.price - a.price)
  )
})

// 2) Товары для текущей «страницы»
const visibleBests = computed(() => {
  const start = bestIndex.value * perSlide
  return bests.value.slice(start, start + perSlide)
})

function prevBest() {
  if (bestIndex.value > 0) bestIndex.value--
}

function nextBest() {
  const maxPage = Math.ceil(bests.value.length / perSlide) - 1
  if (bestIndex.value < maxPage) bestIndex.value++
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
  request.value.file = e.target.files[0]
}

function onSubmitRequest() {
  alert('Запрос отправлен!')
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

</script>

<style scoped lang="scss">

.home {
  /* HERO */
  .hero {
    position: relative;
    overflow: hidden;
    padding: 0;
    &-slide {
      position: relative;
    }
    .image-placeholder {
      background-color: $grey-30;
      height: 300px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .hero-text {
      position: absolute;
      top: 20%;
      left: 10%;
      h1 {
        font-size: 32px;
        line-height: 90%;
        letter-spacing: -1.28px;
      }
      .hero-controls {
        button {
          margin-right: 8px;
          background-color: $black-40;
          border: none;
          color: $white-100;
          padding: 8px;
        }
      }
      .btn-catalog {
        display: inline-block;
        margin-top: 12px;
        padding: 8px 16px;
        background-color: $black-100;
        color: $white-100;
        border-radius: 4px;
        text-decoration: none;
      }
    }
    .marquee {
      overflow: hidden;
      white-space: nowrap;
      background-color: $black-100;
      color: $white-100;
      .marquee-content {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 10s linear infinite;
      }
    }
  }

  @keyframes marquee {
    from { transform: translateX(0); }
    to   { transform: translateX(-100%); }
  }

  /* HOW IT WORKS */
  .how-it-works {
    display: flex;
    flex-direction: column;
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
        .icon-placeholder {
          width: 60px;
          height: 60px;
          object-fit: cover;
        }
        .text-step {
          font-family: Manrope-SemiBold;
          font-size: 16px;
          line-height: 80%;
          letter-spacing: -0.64px;
        }
        .text-title {
          font-family: Bounded;
          font-size: 26px;
          font-weight: 250;
          line-height: 90%;
          letter-spacing: -1.56px;
        }
        .text-description {
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
      gap: 8px;
      .cat-slider-div {
        display: flex;
        padding: 0 10px;
        button {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 8px 12px;
          width: calc((100% - 30px)/2);
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
      .cat-slide {
        padding: 0 10px;
        text-align: center;
        .image-placeholder {
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
    .btn-catalog {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-top: 24px;
      padding: 0 24px;
      height: 56px;
      background-color: $grey-20;
      color: $white-100;
      border-radius: 4px;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      text-decoration: none;
      cursor: pointer;
    }
  }

  /* PRINCIPLES */
  .principles {
    display: flex;
    flex-direction: column;
    margin-top: 96px;
    .principle-div {
      background-color: $grey-30;
      color: $white-100;
      font-size: 16px;
      line-height: 110%;
      letter-spacing: -0.64px;
    }
    .principle {
      display: flex;
      flex-direction: column;
      .principle-header {
        display: flex;
        align-items: center;
        margin: 0;
        font-family: Bounded;
        font-size: 26px;
        font-weight: 250;
        line-height: 90%;
        letter-spacing: -1.56px;
        .principle-icon {
          font-size: 30px;
          color: $red-active;
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
    h2 {
      margin: 96px 0 0;
      text-align: center;
      font-family: Bounded;
      font-weight: 500;
      font-size: 24px;
      line-height: 90%;
      letter-spacing: -0.72px;
    }
    .best-slider {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;
      .best-items {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        margin-top: 40px;
        transition: filter 0.25s ease-in-out;
        .best-item {
          display: flex;
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
      height: 56px;
      background-color: $grey-20;
      color: $white-100;
      border-radius: 4px;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      text-decoration: none;
      cursor: pointer;
    }
  }

  /* REQUEST FORM */
  .request-form {
    display: flex;
    flex-direction: column;
    margin-top: 96px;
    padding: 24px 16px;
    background-color: $grey-30;
    h2 {
      margin: 0;
      text-align: center;
      font-family: Bounded;
      font-weight: 500;
      font-size: 24px;
      line-height: 90%;
      letter-spacing: -0.72px;
    }
    form {
      display: flex;
      flex-direction: column;
      padding: 0 16px;
      gap: 8px;
      max-width: 320px;
      margin: 0 auto;
      .or-sep {
        text-align: center;
        margin: 12px 0;
      }
      .btn-submit {
        padding: 8px;
        background-color: $black-100;
        color: $white-100;
        border: none;
        border-radius: 4px;
      }
    }
  }

  /* TESTIMONIALS */
  .testimonials {
    padding: 32px 0;
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
      gap: 32px;
      overflow: hidden;
      .slide {
        display: flex;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
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
      .carousel-div {
        display: flex;
        align-items: center;
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
      .slide-enter-from {
        transform: translateX(100%);
      }
      .slide-enter-active {
        transition: transform 0.25s ease-in-out;
      }
      .slide-enter-to {
        transform: translateX(0%);
      }

      /* Выход */
      .slide-leave-from {
        transform: translateX(0%);
      }
      .slide-leave-active {
        transition: transform 0.25s ease-in-out;
      }
      .slide-leave-to {
        transform: translateX(-100%);
      }
    }
  }

  /* FAQ */
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
