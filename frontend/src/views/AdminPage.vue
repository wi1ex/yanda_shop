<template>
  <div class="admin-page">
    <h1>Админ-панель</h1>

  <!-- === Секция 1: Google Sheets === -->
  <section class="sheets-section">
    <h2>Импорт из Google Sheets</h2>
    <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="sheet-block">
      <h3>{{ capitalize(cat) }}</h3>

      <!-- Режим редактирования ссылки -->
      <template v-if="editingUrl[cat]">
        <input type="text" v-model="sheetUrls[cat]" :placeholder="`URL для ${cat}`" class="sheet-input"/>
        <button @click="saveSheetUrl(cat)" :disabled="sheetLoading[cat]" class="sheet-save">
          {{ sheetLoading[cat] ? 'Сохранение…' : 'Сохранить ссылку' }}
        </button>
      </template>

      <!-- Стандартный режим -->
      <template v-else>
        <button v-if="!sheetUrls[cat]" @click="startEdit(cat)" class="sheet-load">
          Загрузить ссылку
        </button>
        <button v-else @click="startEdit(cat)" class="sheet-refresh-url" :disabled="sheetImportLoading[cat]">
          Обновить ссылку
        </button>

        <button @click="importSheet(cat)" :disabled="!sheetUrls[cat] || sheetImportLoading[cat] || editingUrl[cat]" class="sheet-import">
          {{ sheetImportLoading[cat] ? 'Обновление…' : 'Обновить данные' }}
        </button>
      </template>

      <p v-if="sheetResult[cat]" class="upload-result">
        {{ sheetResult[cat] }}
      </p>
    </div>
  </section>

    <!-- === Секция 2: Загрузка CSV === -->
    <section class="upload-section">
      <h2>Загрузить CSV для товаров</h2>
      <form @submit.prevent="submitCsv">
        <input type="file" accept=".csv" @change="onCsvSelected" ref="csvInput" />
        <button type="submit" :disabled="!csvFile || csvLoading">
          {{ csvLoading ? 'Загрузка…' : 'Загрузить CSV' }}
        </button>
      </form>
      <p v-if="csvResult" class="upload-result">{{ csvResult }}</p>
    </section>

    <!-- === Секция 3: Загрузка ZIP === -->
    <section class="upload-section">
      <h2>Загрузить ZIP с изображениями</h2>
      <form @submit.prevent="submitZip">
        <input type="file" accept=".zip" @change="onZipSelected" ref="zipInput" />
        <button type="submit" :disabled="!zipFile || zipLoading">
          {{ zipLoading ? 'Загрузка…' : 'Загрузить ZIP' }}
        </button>
      </form>
      <p v-if="zipResult" class="upload-result">{{ zipResult }}</p>
    </section>

    <!-- === Секция 4: Логи изменений товаров/изображений === -->
    <section class="logs-section">
      <h2>Последние 10 изменений</h2>
      <div v-if="logsLoading" class="loading-logs">Загрузка журналов...</div>
      <div v-else>
        <table class="logs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Автор (ID)</th>
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
              <td colspan="6" class="no-logs">Нет записей</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- === Секция 5: Статистика посещений (бар-чарт) === -->
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
            <div class="bar-label">{{ Number(h.hour) }}</div>
            <div class="bar-value">{{ h.total }}</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import { useStore } from '@/store/index.js'

const store = useStore()
const adminId = store.user?.id
const adminName = store.user?.username

// CSV/ZIP
const csvFile = ref(null)
const csvResult = ref('')
const csvLoading = ref(false)

const zipFile = ref(null)
const zipResult = ref('')
const zipLoading = ref(false)

const csvInput = ref(null)
const zipInput = ref(null)

// Google Sheets
const sheetUrls = reactive({ shoes: '', clothing: '', accessories: '' })
const editingUrl = reactive({ shoes: false, clothing: false, accessories: false })
const sheetLoading = reactive({ shoes: false, clothing: false, accessories: false })
const sheetImportLoading = reactive({ shoes: false, clothing: false, accessories: false })
const sheetResult = reactive({ shoes: '', clothing: '', accessories: '' })

// Логи
const logs = ref([])
const logsLoading = ref(false)

// Посещения
const selectedDate = ref('')
const visitsData = ref({ date: '', hours: [] })
const visitsLoading = ref(false)

// Helpers
function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

// --- CSV handlers ---
function onCsvSelected(event) {
  csvFile.value = event.target.files[0] || null
  csvResult.value = ''
}

async function submitCsv() {
  if (!csvFile.value) return
  csvLoading.value = true
  csvResult.value = 'Загрузка…'
  const form = new FormData()
  form.append('file', csvFile.value)
  form.append('author_id', adminId)
  form.append('author_name', adminName)
  try {
    const resp = await fetch(`${store.url}/api/import_products`, {
      method: 'POST',
      body: form
    })
    const data = await resp.json()
    if (resp.status === 201) {
      csvResult.value = `Успех: Добавлено ${data.added||0}, Обновлено ${data.updated||0}, Удалено ${data.deleted||0}`
      fetchLogs()
    } else {
      csvResult.value = `Ошибка ${resp.status}: ${data.error||JSON.stringify(data)}`
    }
  } catch (e) {
    console.error('CSV upload error:', e)
    csvResult.value = `Ошибка сети: ${e.message}`
  } finally {
    csvLoading.value = false
    csvFile.value = null
    if (csvInput.value) {
      csvInput.value.value = ""
    }
  }
}

// --- ZIP handlers ---
function onZipSelected(event) {
  zipFile.value = event.target.files[0] || null
  zipResult.value = ''
}

async function submitZip() {
  if (!zipFile.value) return
  zipLoading.value = true
  zipResult.value = 'Загрузка…'
  const form = new FormData()
  form.append('file', zipFile.value)
  form.append('author_id', adminId)
  form.append('author_name', adminName)
  try {
    const resp = await fetch(`${store.url}/api/upload_images`, {
      method: 'POST',
      body: form
    })
    const data = await resp.json()
    if (resp.status === 201) {
      zipResult.value = `Успех: Добавлено ${data.added||0}, Заменено ${data.replaced||0}, Удалено ${data.deleted||0}`
      fetchLogs()
    } else {
      zipResult.value = `Ошибка ${resp.status}: ${data.error||JSON.stringify(data)}`
    }
  } catch (e) {
    console.error('ZIP upload error:', e)
    zipResult.value = `Ошибка сети: ${e.message}`
  } finally {
    zipLoading.value = false
    zipFile.value = null
    if (zipInput.value) {
      zipInput.value.value = ""
    }
  }
}

// --- Logs ---
async function fetchLogs() {
  logsLoading.value = true
  try {
    const resp = await fetch(`${store.url}/api/logs?limit=10`)
    if (resp.ok) {
      const j = await resp.json()
      logs.value = j.logs || []
    }
  } catch (e) {
    console.error('fetchLogs error:', e)
    logs.value = []
  } finally {
    logsLoading.value = false
  }
}

// --- Visits ---
const maxTotal = computed(() => {
  if (!visitsData.value.hours.length) return 1
  return Math.max(...visitsData.value.hours.map(h => h.total), 1)
})

async function fetchVisits() {
  visitsLoading.value = true
  try {
    const date = selectedDate.value || new Date().toISOString().slice(0,10)
    const resp = await fetch(`${store.url}/api/visits?date=${date}`)
    if (resp.ok) {
      const j = await resp.json()
      visitsData.value = { date: j.date, hours: j.hours }
    }
  } catch (e) {
    console.error('fetchVisits error:', e)
    visitsData.value = { date: '', hours: [] }
  } finally {
    visitsLoading.value = false
  }
}

// --- Sheets ---
function startEdit(cat) {
  editingUrl[cat] = true
  sheetResult[cat] = ''
}

async function saveSheetUrl(cat) {
  sheetLoading[cat] = true
  sheetResult[cat] = ''
  try {
    const resp = await fetch(`${store.url}/api/admin/sheet_url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: cat, url: sheetUrls[cat] }),
    })
    const j = await resp.json()
    if (resp.ok) {
      sheetResult[cat] = 'Ссылка сохранена'
      editingUrl[cat] = false   // выходим из режима редактирования
    } else {
      sheetResult[cat] = `Ошибка: ${j.error || resp.status}`
    }
  } catch (e) {
    sheetResult[cat] = `Ошибка сети: ${e.message}`
  } finally {
    sheetLoading[cat] = false
  }
}

async function importSheet(cat) {
  sheetImportLoading[cat] = true
  sheetResult[cat] = ''
  try {
    const resp = await fetch(`${store.url}/api/import_sheet`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category: cat,
        author_id: adminId,
        author_name: adminName
      })
    })
    const j = await resp.json()
    if (resp.status === 201 && j.status === 'ok') {
      sheetResult[cat] = `Добавлено ${j.added}, Обновлено ${j.updated}, Удалено ${j.deleted}`
      fetchLogs()
    } else {
      sheetResult[cat] = `Ошибка: ${j.error || JSON.stringify(j)}`
    }
  } catch (e) {
    sheetResult[cat] = `Ошибка сети: ${e.message}`
  } finally {
    sheetImportLoading[cat] = false
  }
}

// При инициализации подгружаем существующие URL
async function fetchSheetUrls() {
  try {
    const resp = await fetch(`${store.url}/api/admin/sheet_urls`)
    const j = await resp.json()
    Object.keys(sheetUrls).forEach(cat => {
      sheetUrls[cat] = j[cat] || ''
    })
  } catch (e) {
    console.error('fetchSheetUrls error:', e)
  }
}

onMounted(() => {
  fetchLogs()
  const today = new Date().toISOString().slice(0,10)
  selectedDate.value = today
  fetchVisits()
  fetchSheetUrls()
})
</script>

<style scoped lang="scss">
.admin-page {
  margin-top: 12vh;
  padding: 2vw;
  color: #fff;
}
/* --- Секции CSV/ZIP и Google Sheets --- */
.upload-section,
.sheets-section {
  margin-bottom: 30px;
}
.sheet-block {
  margin-bottom: 20px;
}
.sheet-input {
  width: 60%;
  margin-right: 8px;
}
.sheet-save,
.sheet-import {
  margin-right: 8px;
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
