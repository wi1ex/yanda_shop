<template>
  <div class="brands-page">
    <div class="line-vert"></div>
    <h1 class="brands-title">Бренды</h1>
    <div class="line-hor"></div>
    <div class="brands-content">
      <!-- Левая колонка: полный список брендов, сгруппированных по букве -->
      <div class="brands-list">
        <section class="brands-section" v-for="(items, letter) in groupedByLetter" :key="letter" :id="letter">
          <h2 class="brands-letter">{{ letter }}</h2>
          <ul class="brands-ul">
            <li class="brands-li" v-for="brand in items" :key="brand">
              <button type="button" class="brands-button" @click="onBrandClick(brand)">
                {{ brand }}
              </button>
            </li>
          </ul>
        </section>
      </div>
      <!-- Правая колонка: якорный алфавит -->
      <nav class="alf-nav">
        <ul class="alf-ul">
          <li class="alf-li" v-for="letter in alphabet" :key="letter">
            <a :href="'#' + letter" @click.prevent="scrollToLetter(letter)">{{ letter }}</a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
  <div class="line-hor"></div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore }   from '@/store'
import { useRouter }  from 'vue-router'

const store  = useStore()
const router = useRouter()

// 1) Все уникальные бренды
const brands = computed(() => store.productStore.distinctBrands)

// 2) Буквы, которые есть в списке брендов
const alphabet = computed(() =>
  Array.from(
    new Set(brands.value.map(b => b[0].toUpperCase()))
  ).sort()
)

// 3) Группировка по первой букве
const groupedByLetter = computed(() => {
  const map = {}
  alphabet.value.forEach(letter => { map[letter] = [] })
  brands.value.forEach(b => {
    const L = b[0].toUpperCase()
    map[L].push(b)
  })
  // Сортируем бренды внутри каждой группы
  Object.values(map).forEach(arr =>
    arr.sort((a, b) => a.localeCompare(b, 'ru', { sensitivity: 'base' }))
  )
  return map
})

function scrollToLetter(letter) {
  const el = document.getElementById(letter)
  if (!el) return
  const topY = el.getBoundingClientRect().top + window.scrollY - 176
  window.scrollTo({ top: topY, behavior: 'smooth' })
}


// При клике — переход в каталог с query.brand
function onBrandClick(brand) {
  store.productStore.clearFilters()
  router.push({
    name: 'Catalog',
    query: { brand }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
.brands-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  .brands-title {
    margin: 120px 0 64px;
    color: $black-100;
    font-family: Bounded;
    font-weight: 400;
    font-size: 64px;
    line-height: 90%;
    letter-spacing: -5.12px;
    z-index: 20;
  }
  .brands-content {
    display: flex;
    align-items: flex-start;
    position: relative;
    padding: 10px;
    width: calc(100% - 20px);
    z-index: 20;
    .brands-list {
      display: flex;
      flex-direction: column;
      flex: 1;
      .brands-section {
        display: flex;
        flex-direction: column;
        margin-bottom: 40px;
        gap: 8px;
        .brands-letter {
          margin: 0;
          color: $black-100;
          font-family: Bounded;
          font-size: 16px;
          font-weight: 375;
          line-height: 80%;
          letter-spacing: -0.8px;
        }
        .brands-ul {
          display: flex;
          flex-direction: column;
          margin: 0;
          padding: 0;
          gap: 8px;
          list-style: none;
          .brands-li {
            display: flex;
            .brands-button {
              padding: 0;
              border: none;
              background: none;
              color: $black-100;
              font-size: 16px;
              line-height: 100%;
              letter-spacing: -0.64px;
              cursor: pointer;
            }
          }
        }
      }
    }
    .alf-nav {
      position: sticky;
      top: 176px;
      .alf-ul {
        display: flex;
        flex-direction: column;
        margin: 0;
        padding: 0;
        gap: 6px;
        list-style: none;
        .alf-li {
          display: flex;
          a {
            color: $black-40;
            font-size: 14px;
            line-height: 100%;
            letter-spacing: -0.56px;
            text-decoration: none;
          }
        }
      }
    }
  }
}

@media (max-width: 600px) {
  .brands-page {
    .brands-title {
      margin: 96px 0 40px;
      font-size: 32px;
      letter-spacing: -2.24px;
    }
  }
}
</style>
