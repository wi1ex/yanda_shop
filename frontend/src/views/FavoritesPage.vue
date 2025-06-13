<template>
  <div class="favorites-container">
    <router-link to="/catalog" class="back-link">
      ← Вернуться к покупкам
    </router-link>
    <h2 v-if="store.favorites.items.length">Избранное</h2>
    <div v-else class="empty">Список избранного пуст</div>
    <ul v-if="store.favorites.items.length" class="fav-list">
      <li v-for="item in store.favorites.items" :key="item.variant_sku" class="fav-item">
        <img :src="item.image" alt="" class="image"/>
        <div class="details">
          <p class="name">{{ item.name }}</p>
          <p class="price">{{ item.price }}₽</p>
          <button @click="store.addToCart(item)" class="to-cart">В корзину</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { useStore } from '@/store/index.js'
const store = useStore()
</script>

<style scoped lang="scss">
.favorites-container {
  margin-top: 12vh;
  padding: 2vh;
}
.back-link {
  text-decoration: none;
  color: #007bff;
}
.empty {
  text-align: center;
  color: #bbb;
  margin-top: 20px;
}
.fav-list {
  list-style: none;
  padding: 0;
}
.fav-item {
  display: flex;
  align-items: center;
  background: #252a3b;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
}
.image {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 5px;
}
.details {
  margin-left: 10px;
  flex-grow: 1;
}
.name {
  font-weight: bold;
  margin: 0;
  color: #fff;
}
.price {
  color: #ccc;
  margin: 4px 0;
}
.to-cart {
  background: #28a745;
  color: #fff;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
</style>
