<template>
  <div class="admin-page">
    <h1>Админ-панель</h1>

    <!-- === Google Sheets === -->
    <section class="sheets-section">
      <h2>Импорт из Google Sheets</h2>
      <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="sheet-block">
        <h3>{{ cat.charAt(0).toUpperCase() + cat.slice(1) }}</h3>

        <!-- Режим редактирования ссылки -->
        <template v-if="editingUrl[cat]">
          <input type="text" v-model="store.sheetUrls[cat]" :placeholder="`URL для ${cat}`" class="sheet-input"/>
          <button @click="onSaveUrl(cat)" :disabled="store.sheetSaveLoading[cat]" class="sheet-save">
            {{ store.sheetSaveLoading[cat] ? 'Сохранение…' : 'Сохранить ссылку' }}
          </button>
        </template>

        <!-- Стандартный режим -->
        <template v-else>
          <button v-if="!store.sheetUrls[cat]" @click="startEdit(cat)">
            Загрузить ссылку
          </button>
          <button v-else @click="startEdit(cat)" :disabled="store.sheetImportLoading[cat]">
            Обновить ссылку
          </button>

          <button @click="store.importSheet(cat, adminId, adminName)" :disabled="!store.sheetUrls[cat] || store.sheetImportLoading[cat] || editingUrl[cat]" class="sheet-import">
            {{ store.sheetImportLoading[cat] ? 'Обновление…' : 'Обновить данные' }}
          </button>
        </template>

        <p v-if="store.sheetResult[cat]" class="upload-result">
          {{ store.sheetResult[cat] }}
        </p>
      </div>
    </section>

    <!-- === Загрузка ZIP === -->
    <section class="upload-section">
      <h2>Загрузить ZIP с изображениями</h2>
      <form @submit.prevent="submitZip">
        <input type="file" accept=".zip" @change="onZipSelected" ref="zipInput" />
        <button type="submit" :disabled="!zipFile || store.zipLoading">
          {{ store.zipLoading ? 'Загрузка…' : 'Загрузить ZIP' }}
        </button>
      </form>
      <p v-if="store.zipResult" class="upload-result">{{ store.zipResult }}</p>
    </section>

    <!-- === Логи изменений товаров/изображений === -->
    <section class="logs-section">
      <h2>Последние 10 изменений</h2>
      <div v-if="store.logsLoading" class="loading-logs">Загрузка журналов...</div>
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
            <tr v-for="log in store.logs" :key="log.id">
              <td>{{ log.id }}</td>
              <td>{{ log.author_id }}</td>
              <td>{{ log.author_name }}</td>
              <td>{{ log.action_type }}</td>
              <td>{{ log.description }}</td>
              <td>{{ log.timestamp }}</td>
            </tr>
            <tr v-if="store.logs.length === 0">
              <td colspan="6" class="no-logs">Нет записей</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- === Статистика посещений (бар-чарт) === -->
    <section class="visits-section">
      <h2>Статистика посещений</h2>

      <div class="date-picker">
        <label for="visit-date">Дата:</label>
        <input type="date" id="visit-date" v-model="selectedDate" @change="fetchVisits" />
        <button class="refresh-button" @click="fetchVisits">Обновить</button>
      </div>

      <div v-if="store.visitsLoading" class="loading-visits">Загрузка данных...</div>

      <div v-else class="chart-wrapper">
        <!-- Если нет данных, выводим сообщение -->
        <div v-if="!store.visitsData.hours.length" class="no-data">Нет данных за выбранный день</div>
        <!-- Иначе: «самописный» бар-чарт -->
        <div v-else class="bar-chart">
          <div v-for="h in store.visitsData.hours" :key="h.hour" class="bar" :style="{ height: (h.total / maxTotal * 100) + '%' }">
            <div class="bar-label">{{ Number(h.hour) }}</div>
            <div class="bar-value">{{ h.total }}</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from '@/store/index.js'

const store = useStore()
const adminId = store.user.id
const adminName = store.user.username

const zipFile = ref(null)
const zipInput = ref(null)
const editingUrl = reactive({ shoes:false, clothing:false, accessories:false })
const selectedDate = ref(new Date().toISOString().slice(0,10))

const maxTotal = computed(() => {
  const hours = store.visitsData.hours || []
  if (!hours.length) return 1
  return Math.max(...hours.map(h => h.total), 1)
})

function startEdit(cat) {
  editingUrl[cat] = true
}

function onZipSelected(e) {
  zipFile.value = e.target.files[0]
}

// Ждём, пока ZIP будет загружен, затем очищаем и reset input
async function submitZip() {
  if (!zipFile.value) return
  await store.uploadZip(zipFile.value, adminId, adminName)
  // сбрасываем выбранный файл
  zipFile.value = null
  // и сам HTML-элемент
  if (zipInput.value) {
    zipInput.value.value = ''
  }
}

function fetchVisits() {
  store.loadVisits(selectedDate.value)
}

async function onSaveUrl(cat) {
  const ok = await store.saveSheetUrl(cat)
  // Сбрасываем режим редактирования только при успехе
  if (ok) {
    editingUrl[cat] = false
  }
}

onMounted(() => {
  store.loadSheetUrls()
  store.loadLogs()
  store.loadVisits(selectedDate.value)
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
  margin-bottom: 24px;
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
  margin-bottom: 24px;
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

@media (max-width: 600px) {
  /* Google Sheets */
  .sheet-block {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .sheet-input {
    width: 100% !important;
    margin-right: 0;
  }
  .sheet-save,
  .sheet-import {
    width: 100%;
  }

  /* CSV/ZIP upload */
  .upload-section form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .upload-section input,
  .upload-section button {
    width: 100%;
  }

  /* Таблица логов */
  .logs-table {
    display: block;
    width: 100%;
    overflow-x: auto;
  }
  .logs-table thead,
  .logs-table tbody,
  .logs-table tr {
    display: table;
    width: 100%;
    table-layout: fixed;
  }

  /* Date-picker */
  .date-picker {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .date-picker input,
  .date-picker .refresh-button {
    width: 100%;
  }

  /* Бар-чарт */
  .chart-wrapper {
    max-width: 100%;
  }
  .bar-chart {
    height: 200px;
  }
  .bar {
    margin: 0 1px;
  }
  .bar-label {
    font-size: 10px;
    bottom: -16px;
  }
  .bar-value {
    font-size: 10px;
  }
}

</style>
