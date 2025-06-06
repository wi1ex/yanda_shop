<template>
  <div class="profile-page">
    <h1>Профиль пользователя</h1>

    <!-- Если мы решили редиректить или показывать сообщение гостю, можно добавить тут отдельный блок -->
    <div v-if="notTelegramUser" class="not-tg-message">
      <p>Профиль доступен только авторизованным через Telegram пользователям.</p>
      <button @click="goHome">Вернуться на главную</button>
    </div>

    <!-- Если идёт загрузка профиля (и это telegram-пользователь) -->
    <div v-else-if="loading" class="loading-profile">
      Загрузка профиля...
    </div>

    <!-- Если ошибка (и telegram-пользователь) -->
    <div v-else-if="error" class="error-profile">{{ error }}</div>

    <!-- Когда профиль успешно загружен (и telegram-пользователь) -->
    <div v-else class="profile-info">
      <img :src="store.user.photo_url || img_bot" alt="avatar" class="profile-avatar"/>
      <p>
        <strong>ID:</strong> {{ profile.user_id }}
      </p>
      <p v-if="profile.first_name">
        <strong>Имя:</strong> {{ profile.first_name }}
      </p>
      <p v-if="profile.last_name">
        <strong>Фамилия:</strong> {{ profile.last_name }}
      </p>
      <p v-if="profile.username">
        <strong>Username:</strong> {{ profile.username }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

const profile = ref(null)
const loading = ref(false)
const error = ref("")

/**
 * Утилита: проверяем, можно ли считать userId валидным целым.
 * Если это Telegram-ID (число или строка, приводимая к целому), вернёт true.
 * Если гостевой UUID (например, "8002ef4e-…"), то вернёт false.
 */
function isNumericUserId(value) {
  if (value === null || value === undefined) return false
  const n = Number(value)
  return !isNaN(n) && Number.isInteger(n)
}

// Флаг, что текущий user.id НЕ является telegram-ID
const notTelegramUser = computed(() => {
  // Если нет store.user или store.user.id, тоже считаем не-TG
  if (!store.user || !store.user.id) return true
  return !isNumericUserId(store.user.id)
})

// Функция, чтобы уйти на главную
function goHome() {
  router.push({ name: 'Home' })
}

// Когда компонент монтируется:
onMounted(async () => {
  // Если это не numeric (гость), просто не делаем запрос и ждём, что v-if покажет сообщение
  if (notTelegramUser.value) {
    return
  }

  // Иначе — telegram-пользователь, делаем fetch профиля
  loading.value = true
  try {
    const resp = await fetch(`${store.url}/api/user?user_id=${store.user.id}`)
    if (!resp.ok) {
      if (resp.status === 404) {
        error.value = "Пользователь не найден"
      } else {
        error.value = `Ошибка ${resp.status}`
      }
      loading.value = false
      return
    }
    const data = await resp.json()
    profile.value = data
  } catch (e) {
    console.error("Ошибка при fetch профиля:", e)
    error.value = "Ошибка сети"
  } finally {
    loading.value = false
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
.not-tg-message button:hover {
  background: #0056b3;
}
</style>
