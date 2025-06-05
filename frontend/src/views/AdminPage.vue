<template>
  <div class="admin-page">
    <h1>Админ-панель</h1>

    <!-- === Секция: Загрузка CSV === -->
    <section class="upload-section">
      <h2>Загрузить CSV для товаров</h2>
      <form @submit.prevent="submitCsv">
        <input type="file" accept=".csv" @change="onCsvSelected" ref="csvInput"/>
        <button type="submit" :disabled="!csvFile">
          Загрузить CSV
        </button>
      </form>
      <p v-if="csvResult" class="upload-result">{{ csvResult }}</p>
    </section>
    <!-- === /Секция: Загрузка CSV === -->

    <!-- === Секция: Загрузка ZIP === -->
    <section class="upload-section">
      <h2>Загрузить ZIP с изображениями</h2>
      <form @submit.prevent="submitZip">
        <input type="file" accept=".zip" @change="onZipSelected" ref="zipInput"/>
        <button type="submit" :disabled="!zipFile">
          Загрузить ZIP
        </button>
      </form>
      <p v-if="zipResult" class="upload-result">{{ zipResult }}</p>
    </section>
    <!-- === /Секция: Загрузка ZIP === -->

    <!-- === Секция: Статистика посещений === -->
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
        <!-- Отрисовываем BarChart только после того, как visitsData.hours — массив -->
        <BarChart v-if="Array.isArray(visitsData.hours)" :chartLabels="labelsForChart" :chartData="visitsData.hours"/>
      </div>
    </section>
    <!-- === /Секция: Статистика посещений === -->
  </div>
</template>

<script setup>
import { ref, onMounted, computed, h } from 'vue'
import { useStore } from '@/store/index.js'

// --- Импортируем Chart.js и его компоненты для BarChart ---
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

// Регистрируем необходимые компоненты Chart.js
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useStore()

// --------------- ДАННЫЕ И ЛОГИКА ДЛЯ ГРАФИКА ---------------

// Дата, выбранная в input[type="date"]
const selectedDate = ref('')

// Объект вида { date: 'YYYY-MM-DD', hours: [ { hour: '00', unique: 12, total: 34 }, … ] }
// Изначально — пустой массив часов
const visitsData = ref({ date: '', hours: [] })

// Флаг, что в данный момент идёт загрузка данных
const visitsLoading = ref(false)

// Вычисленное свойство: массив строк-меток для оси X ["00:00", "01:00", …, "23:00"]
const labelsForChart = computed(() =>
  visitsData.value.hours.map((h) => h.hour + ':00')
)

// Функция, чтобы подтянуть данные визитов с backend
async function fetchVisits() {
  visitsLoading.value = true
  // Сбрасываем старые данные, выставляем visitsData.hours = []
  visitsData.value = { date: '', hours: [] }

  try {
    // Если дата не выбрана, по умолчанию используем «сегодня»
    const dateToFetch = selectedDate.value || new Date().toISOString().slice(0, 10)
    const resp = await fetch(`${store.url}/api/visits?date=${dateToFetch}`)

    if (!resp.ok) {
      console.error('Ошибка при получении статистики:', resp.statusText)
      visitsLoading.value = false
      return
    }

    const data = await resp.json()

    // Нормализуем полученные данные: гарантируем, что hours — массив
    visitsData.value = {
      date: data.date || dateToFetch,
      hours: Array.isArray(data.hours) ? data.hours : []
    }
  } catch (e) {
    console.error('Ошибка сети при fetchVisits:', e)
    // Если ошибка сети, тоже оставляем пустой массив
    visitsData.value = { date: '', hours: [] }
  } finally {
    visitsLoading.value = false
  }
}

// При монтировании компонента задаём сегодняшнюю дату и сразу вызываем fetchVisits
onMounted(() => {
  const today = new Date().toISOString().slice(0, 10)
  selectedDate.value = today
  fetchVisits()
})

// --------------- КОМПОНЕНТ-ОБЁРТКА ДЛЯ BAR CHART ---------------

/**
 * BarChart — это локальный компонент, который принимает:
 *   props.chartLabels: Array<String> — метки (часы) для оси X
 *   props.chartData:   Array<{hour: String, unique: Number, total: Number}>
 * И отображает столбчатый график количества «total» визитов по часам.
 */
const BarChart = {
  name: 'BarChart',
  props: {
    chartLabels: {
      type: Array,
      required: true
    },
    chartData: {
      type: Array,
      required: true
    }
  },
  setup(props) {
    // Формируем объект данных для Chart.js
    const chartData = {
      labels: props.chartLabels,
      datasets: [
        {
          label: 'Всего визитов',
          data: props.chartData.map((item) => item.total),
          backgroundColor: '#2196F3' // синий цвет столбцов, можно заменить
        }
      ]
    }

    // Параметры (опции) для графика
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

    // Возвращаем рендер-функцию (h(Bar, { … }))
    return () => h(Bar, { chartData, chartOptions, style: { height: '100%' } })
  }
}
// --------------------------------------------------------------

// === Ниже идут методы для загрузки CSV и ZIP (как у вас было раньше) ===
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
    // Обнуляем выбранный файл в input
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

/* --- Стили для раздела статистики --- */
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
/* Контейнер графика: ограничиваем по высоте и центруем */
.chart-container {
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
  height: 350px; /* Здесь задаётся «компактность» графика */
}
/* --- /Стили для раздела статистики --- */

/* --- Стили для раздела загрузки CSV/ZIP --- */
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
/* --- /Стили для раздела загрузки CSV/ZIP --- */
</style>
