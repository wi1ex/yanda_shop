<template>
  <div class="profile-page">
    <div class="line-vert"></div>
    <h1>Профиль пользователя</h1>
    <div class="profile-info">
      <img :src="store.userStore.user.photo_url || icon_default_avatar_grey" alt="avatar" />
      <p>Никнейм: {{ store.userStore.user.username }}</p>
      <p>Имя: {{ store.userStore.user.first_name }}</p>
      <p>Фамилия: {{ store.userStore.user.last_name }}</p>
    </div>
    <button @click="onLogout()">Выйти</button>
  </div>
  <div class="line-hor"></div>
</template>

<script setup>
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

import icon_default_avatar_grey from '@/assets/images/default_avatar_grey.svg'

const store  = useStore()
const router = useRouter()

async function onLogout() {
  await store.userStore.logout()
  router.push({ name: 'Home' })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

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

.profile-page {
  margin-top: 120px;
  .profile-info {
    background-color: #252a3b;
    padding: 20px;
    border-radius: 8px;
    img {
      width: 80px;
      height: 80px;
      border-radius: 100%;
      object-fit: cover;
    }
    p {
      margin: 8px 0;
      font-size: 16px;
    }
  }
}

@media (max-width: 600px) {
  .profile-page {
    margin-top: 96px;
  }
}

</style>
