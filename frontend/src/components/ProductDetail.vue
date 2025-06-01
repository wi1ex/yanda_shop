<template>
  <div class="product-detail">
    <!-- Кнопка “Назад к каталогу” -->
    <button class="back-button" @click="goBack">
      ← Назад в каталог
    </button>

    <!-- Если detailData ещё не загрузились, показываем «Загрузка…» -->
    <div v-if="loading" class="loading">
      Загрузка...
    </div>

    <!-- Когда detailData загружены, рендерим карточку -->
    <div v-else class="detail-card">
      <!-- Изображение -->
      <img
        v-if="detailData.image_url"
        :src="detailData.image_url"
        alt="product image"
        class="detail-image"
      />
      <div class="detail-info">
        <!-- Название -->
        <h2 class="detail-name">{{ detailData.name }}</h2>

        <!-- Цена -->
        <p class="detail-price">{{ detailData.price }} ₽</p>

        <!-- Выведем все поля, которые есть в detailData -->
        <!-- Например, sku, gender, category, subcategory, brand и т. д. -->
        <p v-if="detailData.sku" class="detail-field">
          <strong>SKU:</strong> {{ detailData.sku }}
        </p>
        <p v-if="detailData.gender" class="detail-field">
          <strong>Пол:</strong> {{ detailData.gender }}
        </p>
        <p v-if="detailData.category" class="detail-field">
          <strong>Категория:</strong> {{ detailData.category }}
        </p>
        <p v-if="detailData.subcategory" class="detail-field">
          <strong>Субкатегория:</strong> {{ detailData.subcategory }}
        </p>
        <p v-if="detailData.brand" class="detail-field">
          <strong>Бренд:</strong> {{ detailData.brand }}
        </p>
        <p v-if="detailData.description" class="detail-field">
          <strong>Описание:</strong> {{ detailData.description }}
        </p>
        <p v-if="detailData.material" class="detail-field">
          <strong>Материал:</strong> {{ detailData.material }}
        </p>
        <p v-if="detailData.color" class="detail-field">
          <strong>Цвет:</strong> {{ detailData.color }}
        </p>

        <!-- Для «Обуви» размер может храниться в size_label, width_mm, height_mm, depth_mm -->
        <p v-if="detailData.size_label" class="detail-field">
          <strong>Размер:</strong> {{ detailData.size_label }}
        </p>
        <p v-if="detailData.width_mm" class="detail-field">
          <strong>Ширина (мм):</strong> {{ detailData.width_mm }}
        </p>
        <p v-if="detailData.height_mm" class="detail-field">
          <strong>Высота (мм):</strong> {{ detailData.height_mm }}
        </p>
        <p v-if="detailData.depth_mm" class="detail-field">
          <strong>Глубина (мм):</strong> {{ detailData.depth_mm }}
        </p>

        <!-- Для «Одежды» отображаем size_label, material, color (уже выше) -->
        <!-- Для «Аксессуаров» похожим образом -->

        <p v-if="detailData.size_guide_url" class="detail-field">
          <strong>Size Guide:</strong>
          <a :href="detailData.size_guide_url" target="_blank">ссылка</a>
        </p>
        <p v-if="detailData.delivery_time" class="detail-field">
          <strong>Время доставки:</strong> {{ detailData.delivery_time }}
        </p>

        <!-- Кнопки управления количеством в корзине -->
        <div class="detail-cart-controls">
          <div v-if="currentQuantity > 0" class="quantity-controls">
            <button @click="decreaseQuantity(detailData)">➖</button>
            <span class="quantity">{{ currentQuantity }}</span>
            <button @click="increaseQuantity(detailData)">➕</button>
          </div>
          <button v-else class="add-button" @click="addToCart(detailData)">
            Купить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import {
  store,
  clearSelectedProduct,
  addToCart,
  getProductQuantity,
  increaseQuantity,
  decreaseQuantity,
} from '@/store.js'

// Локальный стейт: вся детальная информация о товаре
const detailData = ref(null)
// Индикатор загрузки
const loading = ref(true)

// Когда store.selectedProduct меняется, будем выполнять fetchDetail()
watch(
  () => store.selectedProduct,
  async (newVal) => {
    if (newVal) {
      await fetchDetail(newVal.category, newVal.sku)
    }
  },
  { immediate: true }
)

// Функция для загрузки полного JSON‐объекта из /api/product
async function fetchDetail(category, sku) {
  loading.value = true
  try {
    // Делаем запрос к бекенду:
    const response = await fetch(
      `${store.url}/api/product?category=${encodeURIComponent(category)}&sku=${encodeURIComponent(sku)}`
    )
    if (!response.ok) {
      console.error('Ошибка при получении детализации товара:', response.statusText)
      detailData.value = null
    } else {
      detailData.value = await response.json()
    }
  } catch (err) {
    console.error('Ошибка сети при fetchDetail:', err)
    detailData.value = null
  } finally {
    loading.value = false
  }
}

// Кнопка “Назад”
function goBack() {
  clearSelectedProduct()
}

// Сколько уже в корзине (для данной SKU)
const currentQuantity = ref(0)
watch(
  () => detailData.value,
  (newVal) => {
    if (newVal) {
      currentQuantity.value = getProductQuantity(newVal)
    }
  }
)
// Также следим за динамическим изменением корзины
watch(
  () => store.cart.items,
  () => {
    if (detailData.value) {
      currentQuantity.value = getProductQuantity(detailData.value)
    }
  }
)

// При клике на “➕” рядом с детальным товаром:
function increaseQuantity(item) {
  increaseQuantity(item)
}

// При клике на “➖” рядом с детальным товаром:
function decreaseQuantity(item) {
  decreaseQuantity(item)
}

// При клике “Купить”:
function addToCart(item) {
  addToCart(item)
}
</script>

<style scoped lang="scss">
.product-detail {
  margin-top: 100px;
  padding: 20px;
}

/* Кнопка “назад” */
.back-button {
  background: transparent;
  color: white;
  border: 1px solid #bbb;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 16px;
  transition: background 0.2s;
}
.back-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Состояние “Загрузка” */
.loading {
  color: #bbb;
  font-size: 18px;
  text-align: center;
  margin-top: 40px;
}

/* Карточка товара */
.detail-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: $background-color;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Изображение */
.detail-image {
  width: 100%;
  max-width: 300px;
  border-radius: 8px;
  object-fit: cover;
}

/* Блок с текстовой информацией */
.detail-info {
  margin-top: 16px;
  width: 100%;
  max-width: 500px;
}

/* Заголовок (название) */
.detail-name {
  font-size: 24px;
  margin-bottom: 8px;
}

/* Цена */
.detail-price {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 12px;
}

/* Общий стиль для всех полей */
.detail-field {
  font-size: 14px;
  color: #ccc;
  margin-bottom: 8px;
  word-wrap: break-word;
}

/* Контейнер для управления корзиной */
.detail-cart-controls {
  margin-top: 16px;
}

/* Кнопка “Купить” */
.add-button {
  background: #007bff;
  color: white;
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s;
}
.add-button:hover {
  background: #0056b3;
}

/* Кнопки “➖/➕” */
.quantity-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}
.quantity-controls button {
  background: #007bff;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.quantity {
  font-size: 16px;
  font-weight: bold;
  color: white;
}
</style>
