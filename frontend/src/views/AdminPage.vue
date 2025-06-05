<template>
  <div class="admin-page">
    <h1>Админ-панель</h1>

    <!-- Секция: Статистика посещений -->
    <section class="visits-section">
      <h2>Статистика посещений за день</h2>
      <div class="date-picker">
        <label for="visit-date">Дата:</label>
        <input type="date" id="visit-date" v-model="selectedDate" @change="fetchVisits"/>
      </div>
      <button class="refresh-button" @click="fetchVisits">
        Обновить
      </button>
      <div v-if="visitsLoading" class="loading-visits">Загрузка данных...</div>
      <div v-else>
        <table class="visits-table">
          <thead>
            <tr>
              <th>Час</th>
              <th>Уникальные посетители</th>
              <th>Всего визитов</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hourData in visitsData.hours" :key="hourData.hour">
              <td>{{ hourData.hour }}:00</td>
              <td>{{ hourData.unique }}</td>
              <td>{{ hourData.total }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Секция: Загрузка CSV (import_products) -->
    <section class="upload-section">
      <h2>Загрузка CSV для товаров</h2>
      <form @submit.prevent="submitCsv">
        <input type="file" accept=".csv" @change="onCsvSelected" />
        <button type="submit" :disabled="!csvFile">Загрузить CSV</button>
      </form>
      <p v-if="csvResult" class="upload-result">{{ csvResult }}</p>
    </section>

    <!-- Секция: Загрузка ZIP (upload_images) -->
    <section class="upload-section">
      <h2>Загрузка ZIP с изображениями</h2>
      <form @submit.prevent="submitZip">
        <input type="file" accept=".zip" @change="onZipSelected" />
        <button type="submit" :disabled="!zipFile">Загрузить ZIP</button>
      </form>
      <p v-if="zipResult" class="upload-result">{{ zipResult }}</p>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from '@/store/index.js'

const store = useStore()

// --- Для статистики посещений ---
const selectedDate = ref('')
const visitsData = ref({ date: '', hours: [] })
const visitsLoading = ref(false)

// Устанавливаем сегодня как значение по умолчанию
onMounted(() => {
  const today = new Date().toISOString().slice(0, 10) // 'YYYY-MM-DD'
  selectedDate.value = today
  fetchVisits()
})

// Функция получения статистики
async function fetchVisits() {
  visitsLoading.value = true
  visitsData.value = { date: '', hours: [] }
  try {
    const resp = await fetch(`${store.url}/api/visits?date=${selectedDate.value}`)
    if (!resp.ok) {
      console.error('Ошибка при получении статистики:', resp.statusText)
      visitsLoading.value = false
      return
    }
    const data = await resp.json()
    visitsData.value = data
  } catch (e) {
    console.error('Ошибка сети при fetchVisits:', e)
  } finally {
    visitsLoading.value = false
  }
}

// --- Для загрузки CSV (import_products) ---
const csvFile = ref(null)
const csvResult = ref('')

function onCsvSelected(event) {
  csvFile.value = event.target.files[0] || null
  csvResult.value = ''
}

async function submitCsv() {
  if (!csvFile.value) return
  csvResult.value = 'Загрузка...'
  const formData = new FormData()
  formData.append('file', csvFile.value)

  try {
    const resp = await fetch(`${store.url}/api/import_products`, {
      method: 'POST',
      body: formData
    })
    const data = await resp.json()
    if (resp.status === 201 && data) {
      csvResult.value = `Успех: Добавлено ${data.added || 0}, Обновлено ${data.updated || 0}`
    } else {
      csvResult.value = `Ошибка ${resp.status}: ${data.error || JSON.stringify(data)}`
    }
  } catch (e) {
    console.error('Ошибка при загрузке CSV:', e)
    csvResult.value = `Ошибка соединения: ${e.message}`
  }
}

// --- Для загрузки ZIP (upload_images) ---
const zipFile = ref(null)
const zipResult = ref('')

function onZipSelected(event) {
  zipFile.value = event.target.files[0] || null
  zipResult.value = ''
}

async function submitZip() {
  if (!zipFile.value) return
  zipResult.value = 'Загрузка...'
  const formData = new FormData()
  formData.append('file', zipFile.value)

  try {
    const resp = await fetch(`${store.url}/api/upload_images`, {
      method: 'POST',
      body: formData
    })
    const data = await resp.json()
    if (resp.status === 201 && data) {
      zipResult.value = `Успех: Добавлено ${data.added || 0}, Заменено ${data.replaced || 0}, Удалено ${data.deleted || 0}`
    } else {
      zipResult.value = `Ошибка ${resp.status}: ${data.error || JSON.stringify(data)}`
    }
  } catch (e) {
    console.error('Ошибка при загрузке ZIP:', e)
    zipResult.value = `Ошибка соединения: ${e.message}`
  }
}
</script>

<style scoped lang="scss">
.admin-page {
  margin-top: 12vh;
  padding: 2vw;
  color: #fff;
}

.admin-page h1 {
  text-align: center;
  margin-bottom: 20px;
}

.visits-section {
  margin-bottom: 40px;
}

.date-picker {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.refresh-button {
  background: #007bff;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  margin-left: 10px;
}
.refresh-button:hover {
  background: #0056b3;
}

.loading-visits {
  color: #bbb;
  font-style: italic;
  margin-top: 10px;
}

.visits-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
.visits-table th,
.visits-table td {
  border: 1px solid #555;
  padding: 8px;
  text-align: center;
}
.visits-table th {
  background: #333;
  color: #fff;
}
.visits-table tbody tr:nth-child(even) {
  background: #2a2e3e;
}

.upload-section {
  margin-bottom: 30px;
}
.upload-section h2 {
  margin-bottom: 10px;
}
.upload-section form {
  display: flex;
  align-items: center;
  gap: 10px;
}
.upload-section input[type="file"] {
  color: #fff;
}
.upload-section button {
  background: #28a745;
  color: #fff;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}
.upload-section button:disabled {
  background: #555;
  cursor: not-allowed;
}
.upload-section button:hover:not(:disabled) {
  background: #218838;
}

.upload-result {
  margin-top: 8px;
  font-weight: bold;
}
</style>
