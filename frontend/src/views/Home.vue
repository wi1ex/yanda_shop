<template>
  <div class="home-container">
    <h1>Добро пожаловать в YANDA SHOP!</h1>
    <p>Здесь вы можете просмотреть наши лучшие товары.</p>
    <!-- Ссылка на страницу каталога -->
    <router-link to="/catalog" class="go-catalog-button">
      Перейти в каталог
    </router-link>
  </div>
</template>

<script setup>
// Логики здесь нет, исключительно шаблон
</script>

<style scoped lang="scss">
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80vh;
  color: #fff;
}

.go-catalog-button {
  margin-top: 20px;
  padding: 10px 20px;
  background: #007bff;
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  transition: background 0.3s;
}
.go-catalog-button:hover {
  background: #0056b3;
}
</style>
