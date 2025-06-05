<template>
  <div class="profile-page">
    <h1>Профиль пользователя</h1>
    <div v-if="loading" class="loading-profile">Загрузка профиля...</div>
    <div v-else-if="error" class="error-profile">{{ error }}</div>
    <div v-else class="profile-info">
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
import { ref, onMounted } from 'vue'
import { useStore } from '@/store/index.js'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

const profile = ref(null)
const loading = ref(true)
const error = ref("")

// Если пользователь не авторизован (нет store.user.id) – редиректим на /
onMounted(async () => {
  if (!store.user || !store.user.id) {
    router.push({ name: 'Home' })
    return
  }

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

.profile-info {
  background-color: $background-color;
  padding: 20px;
  border-radius: 8px;
}
.profile-info p {
  margin: 8px 0;
  font-size: 16px;
}
</style>
