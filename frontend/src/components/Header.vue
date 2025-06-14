<template>
  <header class="header">
    <div>
      <router-link to="/profile" class="user-info">
        <img :src="store.user.photo_url || profile_avatar" alt="avatar" class="avatar" />
        <span class="username">{{ store.user.username }}</span>
      </router-link>
    </div>

    <nav class="nav-links">
      <router-link to="/" class="nav-link" exact>
        Главная
      </router-link>
      <router-link to="/catalog" class="nav-link">
        Каталог
      </router-link>
      <router-link to="/favorites" class="nav-link">
        Избранное ({{ store.favorites.count }})
      </router-link>
      <button type="button" class="nav-link btn-as-link" @click="store.openCartDrawer()">
        Корзина ({{ store.cart.count }})
      </button>
      <router-link to="/about" class="nav-link">
        О нас
      </router-link>
      <router-link v-if="isAdmin" to="/admin" class="nav-link">
        Админ-панель
      </router-link>
    </nav>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'
import profile_avatar from '@/assets/images/profile_avatar.svg'

const store = useStore()
const router = useRouter()

// Комьютед: true, если текущий user.id равен ADMIN_ID
const isAdmin = computed(() => {
  return store.user && String(store.user.id) === String(store.admin_id)
})

function goHome() {
  router.push({ name: 'Home' })
}
</script>

<style scoped lang="scss">

.header {
  @include flex-header;
  background-color: $background-color;
  padding: 2vh 2vw;
  position: fixed;
  top: 0;
  width: calc(100% - 4vw);
  max-height: 10vh;
  z-index: 1000;
}

.nav-links {
  display: flex;
  gap: 16px;
}

.nav-link {
  color: #fff;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.3s;
}

.nav-link.router-link-active {
  background: #007bff;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1vh;
  text-decoration: none;
  color: inherit;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 100%;
  object-fit: cover;
}

.username {
  font-size: 16px;
  font-weight: bold;
}

.btn-as-link {
  background: none;
  border: none;
  padding: 8px 12px;
  color: #fff;
  cursor: pointer;
  font: inherit;
  text-decoration: none;
}

@media (max-width: 360px) {
  .nav-links {
    flex-wrap: wrap;
    gap: 8px;
  }
  .nav-link { font-size: 14px; padding: 6px 8px; }
}

</style>
