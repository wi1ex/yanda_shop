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


    <!-- === Секция 3: Статистика посещений === -->
    <section class="visits-section">
      <h2>Статистика посещений</h2>

      <div class="date-picker">
        <label for="visit-date">Дата:</label>
        <input type="date" id="visit-date" v-model="selectedDate" @change="fetchVisits"/>
        <button class="refresh-button" @click="fetchVisits">
          Обновить
        </button>
      </div>

      <div v-if="visitsLoading" class="loading-visits">
        Загрузка данных...
      </div>

      <div v-else class="chart-container">
        <!--  Если hours — массив, рисуем Bar, иначе ничего  -->
        <Bar v-if="Array.isArray(visitsData.hours)" :chart-data="chartData" :chart-options="chartOptions" style="height: 100%;"/>
      </div>
    </section>
    <!-- === /Секция 3 === -->
  </div>
</template>

<script setup>
// Общие импорты
import { ref, onMounted, computed } from 'vue'
import { useStore } from '@/store/index.js'

// --- Chart.js 4 + vue-chartjs 5 ---
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from 'chart.js'
import { Bar } from 'vue-chartjs'

// Регистрируем плагины Chart.js
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useStore()

// --- Логику работы с датой и посещениями держим в setup() ---

// 1) Дата, выбранная в input[type="date"]
const selectedDate = ref('')

// 2) Объект вида { date: 'YYYY-MM-DD', hours: [ {hour, unique, total}, ... ] }
const visitsData = ref({ date: '', hours: [] })

// 3) Флаг, что идёт загрузка
const visitsLoading = ref(false)

// 4) Вычисленные метки оси X: ["00:00","01:00",…,"23:00"]
const labelsForChart = computed(() =>
  visitsData.value.hours.map((h) => h.hour + ':00')
)

// 5) Опции для Bar (Chart.js 4)
const chartOptions = {
  responsive: true,
  plugins: {
    legend: {
      display: true,
      position: 'bottom'
    },
    title: {
      display: false
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Часы'
      }
    },
    y: {
      title: {
        display: true,
        text: 'Всего визитов'
      },
      beginAtZero: true
    }
  }
}

// 6) Вычисляемые данные для Bar: { labels: [...], datasets: [ {label,data,backgroundColor} ] }
const chartData = computed(() => ({
  labels: labelsForChart.value,
  datasets: [
    {
      label: 'Всего визитов',
      data: visitsData.value.hours.map((item) => item.total),
      backgroundColor: '#2196F3'
    }
  ]
}))

// 7) Функция, чтобы подтянуть данные визитов с backend
async function fetchVisits() {
  visitsLoading.value = true
  // Обязательно сбрасываем на «пустой» формат
  visitsData.value = { date: '', hours: [] }

  try {
    // Если дата не выбрана — по умолчанию «сегодня»
    const dateToFetch = selectedDate.value || new Date().toISOString().slice(0, 10)
    const resp = await fetch(`${store.url}/api/visits?date=${dateToFetch}`)
    if (!resp.ok) {
      console.error('Ошибка при получении статистики:', resp.statusText)
      visitsLoading.value = false
      return
    }
    const data = await resp.json()

    // Нормализуем: гарантируем, что hours – массив
    visitsData.value = {
      date: data.date || dateToFetch,
      hours: Array.isArray(data.hours) ? data.hours : []
    }
  } catch (e) {
    console.error('Ошибка сети при fetchVisits:', e)
    // В случае ошибки сети оставляем пустой массив
    visitsData.value = { date: '', hours: [] }
  } finally {
    visitsLoading.value = false
  }
}

// 8) При монтировании компонента сразу задать сегодняшнюю дату и запросить данные
onMounted(() => {
  const today = new Date().toISOString().slice(0, 10)
  selectedDate.value = today
  fetchVisits()
})


// === Ниже идут методы для CSV и ZIP (без изменений) ===

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
  } finally {
    // Обнуляем выбранный файл в input
    zipFile.value = null
    if (zipInput.value) {
      zipInput.value.value = null
    }
  }
}
</script>

<style scoped lang="scss">
.admin-page {
  margin-top: 12vh;
  padding: 2vw;
  color: #fff;
}

/* --- Секция статистики --- */
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
}
.refresh-button:hover {
  background: #0056b3;
}
.loading-visits {
  color: #bbb;
  font-style: italic;
  margin-top: 10px;
}
/* Контейнер для графика: */
.chart-container {
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
  height: 350px;
}
/* --- Секция статистики завершена --- */

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
/* --- Конец секции CSV/ZIP --- */
</style>
