<template>
  <div class="brands-page">
    <div class="line-vert"></div>
    <h1>Бренды</h1>
    <div class="line-hor"></div>
    <div class="brands-content">
      <!-- Левая колонка: полный список брендов, сгруппированных по букве -->
      <div class="brands-list">
        <section v-for="(items, letter) in groupedByLetter" :key="letter" :id="letter">
          <h2>{{ letter }}</h2>
          <ul>
            <li v-for="brand in items" :key="brand">
              <button type="button" @click="onBrandClick(brand)">
                {{ brand }}
              </button>
            </li>
          </ul>
        </section>
      </div>
    </div>
    <!-- Правая колонка: якорный алфавит -->
    <nav>
      <ul>
        <li v-for="letter in alphabet" :key="letter">
          <a :href="'#' + letter">{{ letter }}</a>
        </li>
      </ul>
    </nav>
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
  store.clearFilters()
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
  h1 {
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
    position: relative;
    padding: 10px;
    width: calc(100% - 20px);
    z-index: 20;
    .brands-list {
      display: flex;
      flex-direction: column;
      section {
        display: flex;
        flex-direction: column;
        margin-bottom: 40px;
        gap: 8px;
        h2 {
          margin: 0;
          color: $black-100;
          font-family: Bounded;
          font-size: 16px;
          font-weight: 375;
          line-height: 80%;
          letter-spacing: -0.8px;
        }
        ul {
          display: flex;
          flex-direction: column;
          margin: 0;
          padding: 0;
          gap: 8px;
          list-style: none;
          li {
            display: flex;
            button {
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
  }
  nav {
    position: fixed;
    top: 176px;
    right: 10px;
    ul {
      display: flex;
      flex-direction: column;
      margin: 0;
      padding: 0;
      gap: 6px;
      list-style: none;
      li {
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

@media (max-width: 600px) {
  .brands-page {
    h1 {
      margin: 96px 0 40px;
      font-size: 32px;
      letter-spacing: -2.24px;
    }
  }
}
</style>
