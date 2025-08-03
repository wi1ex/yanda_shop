<template>
  <div class="profile-page">
    <div class="line-vert"></div>
    <h1 class="section-title">ЛИЧНЫЙ КАБИНЕТ</h1>

    <button type="button" class="back-button" @click="goBack">
      <img :src="icon_arrow_grey" alt="arrow back" />
      Назад
    </button>

    <div class="line-hor"></div>

    <div class="profile-menu">
      <button type="button" @click="onLogout()">Мой профиль</button>
      <button type="button" @click="onLogout()">Заказы</button>
      <button type="button" @click="onLogout()">Мои адреса</button>
      <button type="button" @click="onLogout()">Выйти из профиля</button>
    </div>
  </div>
  <div class="line-hor" style="margin-top: 96px;"></div>
<!--<img :src="store.userStore.user.photo_url || icon_default_avatar_grey" alt="avatar" />-->
<!--<p>Никнейм: {{ store.userStore.user.username }}</p>-->
<!--<p>Имя: {{ store.userStore.user.first_name }}</p>-->
<!--<p>Фамилия: {{ store.userStore.user.last_name }}</p>-->
</template>

<script setup>
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

import icon_default_avatar_grey from '@/assets/images/default_avatar_grey.svg'
import icon_arrow_grey from "@/assets/images/arrow_grey.svg";

const store  = useStore()
const router = useRouter()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({ name: 'Home' })
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

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
  .section-title {
    margin: 96px 0 40px;
    text-align: center;
    color: $black-100;
    font-family: Bounded;
    font-weight: 400;
    font-size: 32px;
    line-height: 90%;
    letter-spacing: -2.24px;
    z-index: 20;
  }
  .back-button {
    display: flex;
    align-items: center;
    margin: 0 10px 10px;
    padding: 0;
    width: fit-content;
    gap: 4px;
    background: none;
    border: none;
    color: $black-100;
    font-size: 16px;
    line-height: 100%;
    letter-spacing: -0.64px;
    cursor: pointer;
    img {
      width: 24px;
      height: 24px;
      object-fit: cover;
    }
  }
  .profile-menu {
    display: flex;
    flex-direction: column;
    position: relative;
    padding: 10px 10px 0;
    z-index: 20;
    button {
      display: flex;
      padding: 16px 8px;
      border: none;
      border-bottom: 1px solid $white-100;
      background-color: $grey-95;
      color: $grey-20;
      font-family: Bounded;
      font-size: 16px;
      font-weight: 350;
      line-height: 80%;
      letter-spacing: -0.8px;
      cursor: pointer;
    }
    button:first-child {
      border-radius: 4px 4px 0 0;
    }
    button:last-child {
      border-radius: 0 0 4px 4px;
      border-bottom: none;
    }
  }
}

@media (max-width: 600px) {
  .profile-page {
    margin-top: 96px;
  }
}

</style>
