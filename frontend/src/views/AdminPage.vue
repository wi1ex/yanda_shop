<template>
  <div class="admin-page">
    <h1>Админ-панель</h1>

    <!-- === Секция 1: Загрузка CSV === -->
    <section class="upload-section">
      <h2>Загрузить CSV для товаров</h2>
      <form @submit.prevent="submitCsv">
        <input type="file" accept=".csv" @change="onCsvSelected" ref="csvInput" />
        <button type="submit" :disabled="!csvFile">Загрузить CSV</button>
      </form>
      <p v-if="csvResult" class="upload-result">{{ csvResult }}</p>
    </section>
    <!-- === /Секция 1 === -->

    <!-- === Секция 2: Загрузка ZIP === -->
    <section class="upload-section">
      <h2>Загрузить ZIP с изображениями</h2>
      <form @submit.prevent="submitZip">
        <input type="file" accept=".zip" @change="onZipSelected" ref="zipInput" />
        <button type="submit" :disabled="!zipFile">Загрузить ZIP</button>
      </form>
      <p v-if="zipResult" class="upload-result">{{ zipResult }}</p>
    </section>
    <!-- === /Секция 2 === -->

    <!-- === Секция 3: Логи изменений товаров/изображений === -->
    <section class="logs-section">
      <h2>Последние 10 изменений</h2>
      <div v-if="logsLoading" class="loading-logs">Загрузка журналов...</div>
      <div v-else>
        <table class="logs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Автор</th>
              <th>Ник автора</th>
              <th>Тип действия</th>
              <th>Описание</th>
              <th>Дата</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ log.id }}</td>
              <td>{{ log.author_id }}</td>
              <td>{{ log.author_name }}</td>
              <td>{{ log.action_type }}</td>
              <td>{{ log.description }}</td>
              <td>{{ log.timestamp }}</td>
            </tr>
            <tr v-if="logs.length === 0">
              <td colspan="5" class="no-logs">Нет записей</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    <!-- === /Секция 3 === -->

    <!-- === Секция 4: Статистика посещений (бар-чарт) === -->
    <section class="visits-section">
      <h2>Статистика посещений</h2>

      <div class="date-picker">
        <label for="visit-date">Дата:</label>
        <input type="date" id="visit-date" v-model="selectedDate" @change="fetchVisits" />
        <button class="refresh-button" @click="fetchVisits">Обновить</button>
      </div>

      <div v-if="visitsLoading" class="loading-visits">Загрузка данных...</div>

      <div v-else class="chart-wrapper">
        <!-- Если нет данных, выводим сообщение -->
        <div v-if="!visitsData.hours.length" class="no-data">Нет данных за выбранный день</div>
        <!-- Иначе: «самописный» бар-чарт -->
        <div v-else class="bar-chart">
          <div v-for="h in visitsData.hours" :key="h.hour" class="bar" :style="{ height: (h.total / maxTotal * 100) + '%' }">
            <div class="bar-label">{{ h.hour }}:00</div>
            <div class="bar-value">{{ h.total }}</div>
          </div>
        </div>
      </div>
    </section>
    <!-- === /Секция 4 === -->
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useStore } from '@/store/index.js'

// ——— Работа с бэкендом статистики посещений и логов ———
const store = useStore()
const adminId = store.user?.id
const adminName = store.user?.username

// Поле даты
const selectedDate = ref('')

// Объект посещений: { date, hours: [ {hour, unique, total} ] }
const visitsData = ref({ date: '', hours: [] })

// Флаг, что идёт загрузка данных посещений
const visitsLoading = ref(false)

// Массив логов последних 10 изменений
const logs = ref([])
const logsLoading = ref(false)

// Вычисляемая “максимальная” высота (макс total), чтобы масштабировать бары
const maxTotal = computed(() => {
  if (!visitsData.value.hours.length) return 1
  return Math.max(...visitsData.value.hours.map((item) => item.total), 1)
})

// Загрузка посещений
async function fetchVisits() {
  visitsLoading.value = true
  visitsData.value = { date: '', hours: [] }
  try {
    const dateToFetch = selectedDate.value || new Date().toISOString().slice(0, 10)
    const resp = await fetch(`${store.url}/api/visits?date=${dateToFetch}`)
    if (!resp.ok) {
      console.error('Ошибка при получении статистики:', resp.statusText)
      visitsLoading.value = false
      return
    }
    const data = await resp.json()
    visitsData.value = {
      date: data.date || dateToFetch,
      hours: Array.isArray(data.hours) ? data.hours : []
    }
  } catch (e) {
    console.error('Ошибка сети при fetchVisits:', e)
    visitsData.value = { date: '', hours: [] }
  } finally {
    visitsLoading.value = false
  }
}

// Загрузка последних 10 логов
async function fetchLogs() {
  logsLoading.value = true
  logs.value = []
  try {
    const resp = await fetch(`${store.url}/api/logs?limit=10`)
    if (!resp.ok) {
      console.error('Ошибка при получении логов:', resp.statusText)
      logsLoading.value = false
      return
    }
    const data = await resp.json()
    logs.value = Array.isArray(data.logs) ? data.logs : []
  } catch (e) {
    console.error('Ошибка сети при fetchLogs:', e)
    logs.value = []
  } finally {
    logsLoading.value = false
  }
}

// При монтировании задаём сегодняшнюю дату и одновременно грузим посещения и логи
onMounted(() => {
  const today = new Date().toISOString().slice(0, 10)
  selectedDate.value = today
  fetchVisits()
  fetchLogs()
})

// ——— Методы заливки CSV и ZIP ———
const csvInput = ref(null)
const zipInput = ref(null)

const csvFile = ref(null)
const csvResult = ref('')

const zipFile = ref(null)
const zipResult = ref('')

function onCsvSelected(event) {
  csvFile.value = event.target.files[0] || null
  csvResult.value = ''
}
function onZipSelected(event) {
  zipFile.value = event.target.files[0] || null
  zipResult.value = ''
}

async function submitCsv() {
  if (!csvFile.value) return
  csvResult.value = 'Загрузка...'
  const formData = new FormData()
  formData.append('file', csvFile.value)
  formData.append('author_id', adminId)
  formData.append('author_name', adminName)

  try {
    const resp = await fetch(`${store.url}/api/import_products`, {
      method: 'POST',
      body: formData
    })
    const data = await resp.json()
    if (resp.status === 201 && data) {
      csvResult.value = `Успех: Добавлено ${data.added || 0}, Обновлено ${data.updated || 0}, Удалено ${data.deleted || 0}`
      // После удачной загрузки — обновим логи
      fetchLogs()
    } else {
      csvResult.value = `Ошибка ${resp.status}: ${data.error || JSON.stringify(data)}`
    }
  } catch (e) {
    console.error('Ошибка при загрузке CSV:', e)
    csvResult.value = `Ошибка соединения: ${e.message}`
  } finally {
    // Обнуляем input
    csvFile.value = null
    if (csvInput.value) {
      csvInput.value.value = null
    }
  }
}

async function submitZip() {
  if (!zipFile.value) return
  zipResult.value = 'Загрузка...'
  const formData = new FormData()
  formData.append('file', zipFile.value)
  formData.append('author_id', adminId)
  formData.append('author_name', adminName)

  try {
    const resp = await fetch(`${store.url}/api/upload_images`, {
      method: 'POST',
      body: formData
    })
    const data = await resp.json()
    if (resp.status === 201 && data) {
      zipResult.value = `Успех: Добавлено ${data.added || 0}, Заменено ${data.replaced || 0}, Удалено ${data.deleted || 0}`
      // После загрузки ZIP — обновим логи
      fetchLogs()
    } else {
      zipResult.value = `Ошибка ${resp.status}: ${data.error || JSON.stringify(data)}`
    }
  } catch (e) {
    console.error('Ошибка при загрузке ZIP:', e)
    zipResult.value = `Ошибка соединения: ${e.message}`
  } finally {
    // Обнуляем выбранный файл в input
    zipFile.value = null
    if (zipInput.value) {
      zipInput.value.value = null
    }
  }
}

// Форматирование даты из лога (возвращаем уже строку, т. е. без изменений)
function formatDateTime(str) {
  return str
}
</script>

<style scoped lang="scss">
.admin-page {
  margin-top: 12vh;
  padding: 2vw;
  color: #fff;
}

/* --- Секция загрузки CSV/ZIP --- */
.upload-section {
  margin-bottom: 30px;
}
.upload-section input[type='file'] {
  margin-right: 10px;
}
.upload-result {
  margin-top: 8px;
  color: #bada55;
}

/* --- Секция логов изменений --- */
.logs-section {
  margin-bottom: 40px;
}
.logs-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
.logs-table th,
.logs-table td {
  border: 1px solid #444;
  padding: 8px;
  text-align: center;
  font-size: 14px;
}
.logs-table th {
  background-color: #252a3b;
}
.no-logs {
  text-align: center;
  padding: 10px;
  font-style: italic;
}

/* --- Секция статистики посещений --- */
.visits-section {
  margin-top: 40px;
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
}
.refresh-button:hover {
  background: #0056b3;
}
.loading-visits,
.loading-logs {
  color: #bbb;
  font-style: italic;
  margin-top: 10px;
}
.no-data {
  color: #bbb;
  font-style: italic;
  margin-top: 20px;
}

/* Контейнер для «самописного» бар-чарта */
.chart-wrapper {
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
}

/* Стили «бар-чарта» */
.bar-chart {
  display: flex;
  align-items: flex-end;
  height: 300px;
  border-left: 1px solid #666;
  border-bottom: 1px solid #666;
}
.bar {
  flex: 1;
  margin: 0 2px;
  background-color: #2196F3;
  position: relative;
  display: flex;
  flex-direction: column-reverse;
  justify-content: flex-start;
  align-items: center;
  transition: background 0.2s;
}
.bar:hover {
  background-color: #1976D2;
}
/* Надпись с числом сверху */
.bar-value {
  color: #fff;
  font-size: 12px;
  padding: 2px;
}
.bar-label {
  position: absolute;
  bottom: -20px;
  font-size: 12px;
  color: #ccc;
}
</style>
