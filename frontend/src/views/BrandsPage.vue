<template>
  <div class="brands-page">
    <div class="line-vert"></div>
    <h1 class="section-title">Бренды</h1>
    <div class="line-hor"></div>
        <div class="brands-content">
      <!-- Левая колонка: полный список брендов, сгруппированных по букве -->
      <div class="brands-list">
        <section class="brands-section" v-for="(items, letter) in groupedByLetter" :key="letter" :id="letter">
          <h2 class="brands-letter">{{ letter }}</h2>
          <ul class="brands-ul">
            <li v-for="brand in items" :key="brand" class="brands-li">
              <button type="button" class="brand-btn" @click="onBrandClick(brand)">
                {{ brand }}
              </button>
            </li>
          </ul>
        </section>
      </div>
      <!-- Правая колонка: якорный алфавит -->
      <nav class="brands-alphabet">
        <ul>
          <li v-for="letter in alphabet" :key="letter">
            <a :href="'#' + letter">{{ letter }}</a>
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
const brands = computed(() => store.distinctBrands)

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

// При клике — переход в каталог с query.brand
function onBrandClick(brand) {
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
  .section-title {
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
    .brands-list {
      flex: 1;
      .brands-section {
        margin-bottom: 32px;
        .brands-letter {
          font-size: 24px;
          margin-bottom: 12px;
        }
        .brands-ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        .brands-li {
          margin-bottom: 8px;
        }
        .brand-btn {
          background: none;
          border: none;
          font-size: 18px;
          padding: 0;
          cursor: pointer;
          color: #000;
          text-align: left;
          &:hover {
            text-decoration: underline;
          }
        }
      }
    }
    .brands-alphabet {
      width: 48px;
      margin-left: 24px;
      position: sticky;
      top: 100px;
      ul {
        display: flex;
        flex-direction: column;
        padding: 0;
        margin: 0;
        li {
          margin: 4px 0;
          a {
            font-size: 14px;
            color: #888;
            text-decoration: none;
            &:hover {
              color: #000;
            }
          }
        }
      }
    }
  }
}

@media (max-width: 600px) {
  .brands-page {
    .section-title {
      margin: 96px 0 40px;
      font-size: 32px;
      letter-spacing: -2.24px;
    }
  }
}
</style>
