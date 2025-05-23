<template>
  <div class="app-container" v-if="user">
    <!-- Хедер (верхняя панель с логотипом, пользователем и корзиной) -->
    <header class="header">
      <h1>YANDA SHOP</h1>
      <div class="user-info">
        <img :src="user.photo_url" alt="user.photo_url" class="avatar" />
        <span class="username">
          {{ user.first_name }} <span class="status">@{{ user.username }}</span>
        </span>
      </div>
      <!-- Кнопка корзины с отображением количества товаров и итоговой суммы -->
      <button class="cart-button" @click="toggleCart">
        🛒 <span>{{ cart.count }}</span> <span class="cart-total-price">({{ cart.total }}₽)</span>
      </button>
    </header>

    <!-- Окно корзины -->
    <div v-if="cartOpen" class="cart-container">
      <h2 v-if="cart.items.length !== 0">Корзина</h2>

      <!-- Если корзина пуста -->
      <div v-if="cart.items.length === 0" class="empty-cart">Корзина пуста</div>

      <!-- Если в корзине есть товары -->
      <ul v-else class="cart-list">
        <li v-for="(item, index) in groupedCartItems" :key="item.id" class="cart-item">
          <img :src="item.image" alt="item.name" class="cart-item-image" />
          <div class="cart-item-details">
            <p class="cart-item-name">{{ item.name }}</p>
            <p class="cart-item-price">{{ item.totalPrice }}₽</p>
            <div class="cart-item-controls">
              <!-- Кнопки управления количеством товара -->
              <button @click="decreaseQuantity(item)">➖</button>
              <span class="item-quantity">{{ item.quantity }}</span>
              <button @click="increaseQuantity(item)">➕</button>
            </div>
          </div>
        </li>
      </ul>

      <!-- Итоговая сумма в корзине -->
      <p class="cart-total">Итого: {{ cart.total }}₽</p>

      <!-- Кнопки оформления заказа и закрытия корзины -->
      <div class="cart-buttons">
        <button class="checkout-button" @click="checkout">Оформить заказ</button>
        <button class="close-cart" @click="toggleCart">Вернуться к покупкам</button>
      </div>
    </div>

    <!-- Каталог товаров -->
    <div v-else class="catalog">
      <!-- Навигация по категориям товаров -->
      <div class="sticky-nav">
        <div class="categories">
          <!-- Перебираем список категорий и создаем кнопки для каждой -->
          <button v-for="(category, index) in categoryList" :key="index" :class="{ active: category === selectedCategory }" @click="changeCategory(category)">
            {{ category }}
          </button>
        </div>
      </div>

      <h2>{{ selectedCategory }}</h2>
      <div class="products-grid">
        <!-- Перебираем товары и отображаем карточки -->
        <div v-for="(product, index) in filteredProducts" :key="index" class="product-card">
          <img :src="product.image" alt="product" class="product-image" />
          <div class="product-info">
            <p class="product-price">{{ product.price }} ₽</p>
            <p class="product-name">{{ product.name }}</p>
          </div>

          <!-- Если товар уже есть в корзине, отображаем количество с кнопками -->
          <div v-if="getProductQuantity(product) > 0" class="cart-item-controls">
            <button @click="decreaseQuantity(product)">➖</button>
            <span class="item-quantity">{{ getProductQuantity(product) }}</span>
            <button @click="increaseQuantity(product)">➕</button>
          </div>

          <!-- Если товара еще нет в корзине, показываем кнопку "Купить" -->
          <button v-else class="buy-button" @click="addToCart(product)">Купить</button>
        </div>
      </div>
    </div>

    <!-- Футер (нижняя панель с контактной информацией) -->
    <footer :style="footerStyle" class="footer-content">
      <p>Магазин "Телеграм Магазин"</p>
      <p>Телефон: +7 (123) 456-78-90</p>
      <p>Email: info@example.com</p>
      <p>Адрес: г. Москва, ул. Примерная, д.1</p>
    </footer>
  </div>
</template>



<script setup>
import { ref, computed, onMounted } from 'vue';
import img_bot from '@/assets/images/bot.png'

// 🔹 Telegram-состояние
const tg = ref(null);
// 🔹 Информация о пользователе
const user = ref(null);
// 🛒 Реактивный список сгруппированных товаров в корзине
const groupedCartItems = ref([]);
// 🔹 Список категорий товаров
const categoryList = ref(["Кроссовки", "Одежда", "Аксессуары"]);
// 🔹 Выбранная категория (по умолчанию "Кроссовки")
const selectedCategory = ref("Кроссовки");
// 🔹 Открыта ли корзина (true — открыта, false — скрыта)
const cartOpen = ref(false);
// 🛒 Список товаров в корзине в порядке их добавления
const cartOrder = ref([]);
// 🛒 Состояние корзины: количество товаров, итоговая сумма и массив товаров
const cart = ref({ count: 0, total: 0, items: [] });

// 📦 Исходный список товаров с категориями
const products = ref([
  ...Array(10).fill().map((_, i) => ({ image: img_bot, price: `${9000 + i * 500}`, name: `Кроссовки ${i+1}`, category: "Кроссовки" })),
  ...Array(10).fill().map((_, i) => ({ image: img_bot, price: `${3000 + i * 200}`, name: `Одежда ${i+1}`, category: "Одежда" })),
  ...Array(10).fill().map((_, i) => ({ image: img_bot, price: `${1500 + i * 100}`, name: `Аксессуар ${i+1}`, category: "Аксессуары" })),
]);

// 🔍 Фильтруем товары по выбранной категории
const filteredProducts = computed(() => {
  return products.value
    .filter(product => product.category === selectedCategory.value)
    .map(product => ({
      ...product,
      price: Number(product.price) // Приводим цену к числу
    }));
});

// 🛒 Обновляет сгруппированные товары в корзине и сохраняет порядок добавления
const updateGroupedCartItems = () => {
  const grouped = [];
  // Группируем товары по имени и суммируем количество и цену
  cart.value.items.forEach(item => {
    let existingItem = grouped.find(i => i.name === item.name);
    if (existingItem) {
      existingItem.quantity++;
      existingItem.totalPrice += parseInt(item.price);
    } else {
      grouped.push({
        ...item,
        quantity: 1,
        totalPrice: parseInt(item.price),
      });
    }
  });
  // Сортируем товары в порядке их первого добавления
  groupedCartItems.value = grouped.sort((a, b) =>
    cartOrder.value.indexOf(a.name) - cartOrder.value.indexOf(b.name)
  );
  groupedCartItems.value = groupedCartItems.value.slice(); // 🔥 Принудительное обновление Vue
};

// 🔹 Смена категории товаров в каталоге
const changeCategory = (category) => {
  selectedCategory.value = category;
};

// 🛒 Добавляем товар в корзину (увеличивает количество, если товар уже есть)
const addToCart = (product) => {
  const existingItem = cart.value.items.find(i => i.name === product.name);
  if (existingItem) {
    increaseQuantity(existingItem); // Если товар уже есть, увеличиваем его количество
  } else {
    cart.value.count++;
    cart.value.total += parseInt(product.price);
    // Присваиваем уникальный ID при первом добавлении товара
    const productId = product.id || `${Date.now()}-${Math.random()}`;
    cart.value.items.push({ ...product, id: productId });
    // 🔥 Если товара не было в корзине, добавляем его в список `cartOrder`
    if (!cartOrder.value.includes(product.name)) {
      cartOrder.value.push(product.name);
    }
  }
  updateGroupedCartItems(); // Обновляем корзину после добавления товара
};

// 🔄 Переключает отображение корзины (открывает или закрывает)
const toggleCart = () => {
  cartOpen.value = !cartOpen.value;
  if (cartOpen.value) {
    updateGroupedCartItems(); // 🔥 Принудительное обновление корзины при открытии
  }
};

// 🔼 Увеличение количества товара в корзине
const increaseQuantity = (item) => {
  cart.value.count++;
  cart.value.total += parseInt(item.price);
  // Добавляем товар в корзину (он сгруппируется автоматически)
  cart.value.items.push(item);
  updateGroupedCartItems(); // 🔥 Обновляем UI сразу
};

// 🔽 Уменьшение количества товара (или удаление, если остался 1 товар)
const decreaseQuantity = (product) => {
  const index = cart.value.items.findIndex(i => i.name === product.name);
  if (index !== -1) {
    const quantity = cart.value.items.filter(i => i.name === product.name).length;
    if (quantity > 1) {
      cart.value.count--;
      cart.value.total -= parseInt(product.price);
      cart.value.items.splice(index, 1);
    } else {
      cart.value.count--;
      cart.value.total = Math.max(cart.value.total - parseInt(product.price), 0);
      cart.value.items = cart.value.items.filter(i => i.name !== product.name);
      // 🔥 Если удален последний экземпляр товара, убираем его из `cartOrder`
      cartOrder.value = cartOrder.value.filter(name => name !== product.name);
    }
    updateGroupedCartItems(); // Обновляем корзину после удаления товара
  }
};

// 🔢 Получает количество товара в корзине
const getProductQuantity = (product) => {
  return cart.value.items.filter(i => i.name === product.name).length;
};

// ✅ Оформление заказа (очистка корзины)
const checkout = () => {
  alert("Заказ оформлен!");
  cart.value = { count: 0, total: 0, items: [] };
};

// Если приложение запущено внутри Telegram, получаем данные пользователя
onMounted(() => {
  if (window.Telegram && window.Telegram.WebApp) {
    tg.value = window.Telegram.WebApp;
    const initDataUnsafe = tg.value.initDataUnsafe
    if (initDataUnsafe && initDataUnsafe.user) {
      user.value = initDataUnsafe.user;
    }
  }
  if (!user.value) {
    user.value = {
      id: 1,
      first_name: "Test",
      last_name: "User",
      username: "testuser",
    };
  }
  if (user.value) {
    fetch("https://shop.yanda.twc1.net/save_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: user.value.id,
        first_name: user.value.first_name,
        last_name: user.value.last_name,
        username: user.value.username,
      })
    })
      .then(response => response.json())
      .then(data => console.log("Ответ сервера:", data))
      .catch(error => console.error("Ошибка запроса:", error));
  }
});
</script>



<style lang="scss" scoped>
/* 🌑 Основные стили */
.app-container {
  background-color: #131722; /* Темный фон приложения */
  color: white; /* Основной цвет текста */
  min-height: 100vh; /* Минимальная высота экрана */
  padding: 0 16px;
}

/* 🏷️ Хедер (верхняя панель с логотипом, пользователем и корзиной) */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1c1f2e; /* Темный фон панели */
  padding: 16px 32px;
  margin: 10px;
  position: fixed;
  top: -10px;
  left: -2px;
  width: calc(100% - 80px); /* Корректируем ширину */
  z-index: 1000; /* Размещаем поверх остальных элементов */
}

/* 🔝 Навигация по категориям */
.sticky-nav {
  position: fixed;
  top: 116px;
  left: 8px;
  width: calc(100% - 48px);
  background: #1c1f2e;
  z-index: 999; /* Размещаем поверх товаров */
  padding: 26px 16px;
}

/* 📌 Контейнер с кнопками категорий */
.categories {
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* 🔘 Кнопки категорий */
.categories button {
  padding: 10px;
  border-radius: 8px;
  background: #252a3b;
  color: white;
  transition: 0.3s ease; /* Анимация при наведении */
}

/* 🛒 Кнопка корзины */
.cart-button {
  background: #007bff;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  border: none;
  transition: 0.3s ease; /* Плавный переход цвета */
}

/* 🎁 Грид с товарами */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(135px, 1fr)); /* Адаптивная сетка */
  gap: 16px;
}

/* 📦 Карточка товара */
.product-card {
  background: #1c1f2e;
  border-radius: 15px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

/* 🖼️ Изображение товара */
.product-image {
  width: 100%;
  border-radius: 10px;
}

/* 🛍️ Кнопка "Купить" */
.buy-button {
  width: 100%;
  padding: 10px;
  background: #007bff;
  border-radius: 8px;
  margin-top: 8px;
  cursor: pointer;
  transition: 0.3s ease;
}

/* 🛒 Контейнер корзины */
.cart-container {
  background: #1c1f2e;
  padding: 20px;
  border-radius: 10px;
  margin-top: 100px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* 📜 Список товаров в корзине */
.cart-list {
  list-style: none;
  padding: 0;
}

/* 🎁 Элемент товара в корзине */
.cart-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #252a3b;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
}

/* 🖼️ Миниатюра товара в корзине */
.cart-item-image {
  width: 50px;
  height: 50px;
  border-radius: 5px;
  object-fit: cover;
}

/* 📄 Данные о товаре в корзине */
.cart-item-details {
  flex-grow: 1;
  margin-left: 10px;
}

/* 🏷️ Название товара */
.cart-item-name {
  font-size: 14px;
  font-weight: bold;
  margin: 0;
}

/* 💰 Цена товара */
.cart-item-price {
  font-size: 14px;
  color: #ffffff;
  margin: 5px 0;
}

/* ➕➖ Контролы изменения количества товаров */
.cart-item-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 🧮 Итоговая сумма в корзине */
.cart-total {
  font-size: 16px;
  font-weight: bold;
  margin-top: 10px;
}

/* 🔘 Кнопки действий в корзине */
.cart-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  gap: 16px;
}

/* 🔢 Количество товаров */
.item-quantity {
  font-size: 16px;
  font-weight: bold;
  padding: 4px 8px;
  background: #007bff;
  color: white;
  border-radius: 5px;
}

/* 👤 Информация о пользователе */
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background: #1c1f2e;
  padding: 8px;
  border-radius: 8px;
}

/* 🖼️ Аватар */
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

/* 🏷️ Имя пользователя */
.username {
  font-size: 16px;
  font-weight: bold;
}

/* 🏆 Статус пользователя */
.status {
  font-size: 12px;
  color: #00ff88;
  background: rgba(0, 255, 136, 0.2);
  padding: 2px 6px;
  border-radius: 6px;
}

/* 💰 Итоговая сумма в корзине */
.cart-total-price {
  font-size: 14px;
  font-weight: bold;
  margin-left: 6px;
}

/* ❌ Сообщение "Корзина пуста" */
.empty-cart {
  text-align: center;
  font-size: 16px;
  color: #bbb;
  margin-top: 20px;
  margin-bottom: 20px;
}

/* ✅ Кнопка оформления заказа */
.checkout-button {
  background: #28a745;
  color: white;
  padding: 10px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s ease;
  border: none;
}

/* ❌ Кнопка закрытия корзины */
.close-cart {
  background: #dc3545;
  color: white;
  padding: 10px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s ease;
  border: none;
}

/* 🔘 Кнопки увеличения и уменьшения количества */
.cart-item-controls button {
  padding: 4px;
  font-size: 18px;
  font-weight: bold;
  background: #252a3b;
  border: none;
  cursor: pointer;
  transition: 0.2s ease;
  border-radius: 6px;
}

/* 🏪 Каталог */
.catalog {
  margin-top: 170px;
  padding: 20px;
}

/* 📌 Заголовок в хедере */
h1 {
  font-size: 24px;
  text-align: center;
}

/* 📌 Заголовки в корзине и каталоге */
h2 {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-top: 30px;
}

/* 📌 Блок товара */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 💲 Цена товара */
.product-price {
  font-size: 18px;
  font-weight: bold;
  color: #00ff88;
}

/* 📜 Разделение товаров в корзине */
.cart-list li {
  border-bottom: 1px solid #444;
  padding-bottom: 10px;
}

/* 📜 Футер */
.footer-content {
  padding: 20px;
  text-align: center;
}

/* 📜 Информация о магазине */
.footer-content p {
  margin: 5px 0;
}
</style>
