<template>
  <div class="profile-page">
    <h1>Профиль пользователя</h1>

    <!-- Если мы решили редиректить или показывать сообщение гостю, можно добавить тут отдельный блок -->
    <div v-if="notTelegramUser" class="not-tg-message">
      <p>Профиль доступен только авторизованным через Telegram пользователям.</p>
      <button @click="goHome">Вернуться на главную</button>
    </div>

    <!-- Если идёт загрузка профиля (и это telegram-пользователь) -->
    <div v-else-if="store.profileLoading" class="loading-profile">
      Загрузка профиля...
    </div>

    <!-- Если ошибка (и telegram-пользователь) -->
    <div v-else-if="store.profileError" class="error-profile">{{ store.profileError }}</div>

    <!-- Когда профиль успешно загружен (и telegram-пользователь) -->
    <div v-else class="profile-info">
      <img :src="store.user.photo_url || icon_default_avatar_grey" alt="avatar" class="profile-avatar"/>
      <p>
        <strong>ID:</strong> {{ store.profile.user_id }}
      </p>
      <p v-if="store.profile.first_name">
        <strong>Имя:</strong> {{ store.profile.first_name }}
      </p>
      <p v-if="store.profile.last_name">
        <strong>Фамилия:</strong> {{ store.profile.last_name }}
      </p>
      <p v-if="store.profile.username">
        <strong>Username:</strong> {{ store.profile.username }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'
import icon_default_avatar_grey from '@/assets/images/default_avatar_grey.svg'

const store  = useStore()
const router = useRouter()

function goHome() {
  router.push({ name: 'Home' })
}

function isNumericUserId(value) {
  if (value === null || value === undefined) return false
  const n = Number(value)
  return !isNaN(n) && Number.isInteger(n)
}

const notTelegramUser = computed(() => {
  // Если нет store.user или store.user.id, тоже считаем не-TG
  if (!store.user || !store.user.id) return true
  return !isNumericUserId(store.user.id)
})

onMounted(() => {
  if (!notTelegramUser.value) {
    store.fetchUserProfile(store.user.id)
  }
})
</script>

<style scoped lang="scss">

.profile-page {
  margin-top: 12vh;
  padding: 2vw;
  color: #fff;
}

.loading-profile,
.error-profile {
  text-align: center;
  margin-top: 20px;
  font-style: italic;
  color: #bbb;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 16px;
}

.profile-info {
  background-color: #252a3b;
  padding: 20px;
  border-radius: 8px;
}

.profile-info p {
  margin: 8px 0;
  font-size: 16px;
}

/* Стиль для сообщения гостя */
.not-tg-message {
  text-align: center;
  margin-top: 40px;
  background-color: #292e3f;
  padding: 20px;
  border-radius: 8px;
}

.not-tg-message p {
  margin-bottom: 12px;
  font-size: 16px;
}

.not-tg-message button {
  background: #007bff;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

@media (max-width: 600px) {
  .profile-page {
    padding: 4vw;
    margin-top: 8vh;
  }
  .profile-page h1 {
    font-size: 20px;
    text-align: center;
  }

  .not-tg-message,
  .loading-profile,
  .error-profile,
  .profile-info {
    margin: 16px 0;
  }

  .not-tg-message p,
  .loading-profile,
  .error-profile {
    font-size: 14px;
  }
  .not-tg-message button {
    width: 100%;
    padding: 10px;
    font-size: 14px;
  }

  .profile-avatar {
    width: 60px;
    height: 60px;
    margin: 0 auto 12px;
  }

  .profile-info {
    padding: 16px;
  }
  .profile-info p {
    font-size: 14px;
    margin: 6px 0;
  }
}

</style>
