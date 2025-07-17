<template>
  <div class="admin-page">
    <h1>Админ-панель</h1>

    <nav class="tabs">
      <button type="button" v-for="t in tabs" :key="t.key" :class="{ active: selected === t.key }" @click="selected = t.key">
        {{ t.label }}
      </button>
    </nav>


    <!-- Google Sheets -->
    <section class="sheets-section" v-if="selected === 'sheets'">
      <h2>Импорт из Google Sheets</h2>
      <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="sheet-block">
        <h3>{{ cat.charAt(0).toUpperCase() + cat.slice(1) }}</h3>

        <!-- Режим редактирования ссылки -->
        <template v-if="editingUrl[cat]">
          <input type="text" v-model="store.sheetUrls[cat]" :placeholder="`URL для ${cat}`" class="sheet-input"/>
          <button type="button" @click="onSaveUrl(cat)" :disabled="store.sheetSaveLoading[cat]" class="sheet-save">
            {{ store.sheetSaveLoading[cat] ? 'Сохранение…' : 'Сохранить ссылку' }}
          </button>
        </template>

        <!-- Стандартный режим -->
        <template v-else>
          <button type="button" v-if="!store.sheetUrls[cat]" @click="startEdit(cat)">
            Загрузить ссылку
          </button>
          <button type="button" v-else @click="startEdit(cat)" :disabled="store.sheetImportLoading[cat]">
            Обновить ссылку
          </button>

          <button type="button" @click="store.importSheet(cat)" :disabled="!store.sheetUrls[cat] || store.sheetImportLoading[cat] || editingUrl[cat]" class="sheet-import">
            {{ store.sheetImportLoading[cat] ? 'Обновление…' : 'Обновить данные' }}
          </button>
        </template>

        <p v-if="store.sheetResult[cat]" class="upload-result">
          {{ store.sheetResult[cat] }}
        </p>
      </div>
    </section>

    <!-- Загрузка ZIP -->
    <section class="upload-section" v-if="selected === 'upload'">
      <h2>Загрузить ZIP с изображениями</h2>
      <form @submit.prevent="submitZip">
        <input type="file" accept=".zip" @change="onZipSelected" ref="zipInput" />
        <button type="submit" :disabled="!zipFile || store.zipLoading">
          {{ store.zipLoading ? 'Загрузка…' : 'Загрузить ZIP' }}
        </button>
      </form>
      <p v-if="store.zipResult" class="upload-result">{{ store.zipResult }}</p>
    </section>

    <!-- Логи изменений товаров/изображений -->
    <section class="logs-section" v-if="selected === 'logs'">
      <h2>Последние 10 событий</h2>
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
        <div class="pagination-controls">
          <button type="button" @click="prevPage" :disabled="logPage===1">← Предыдущие</button>
          <span>Стр. {{ logPage }} из {{ Math.ceil(store.totalLogs / pageSize) }}</span>
          <button type="button" @click="nextPage" :disabled="logPage*pageSize>=store.totalLogs">Следующие →</button>
        </div>
      </div>
    </section>

    <!-- Статистика посещений (бар-чарт) -->
    <section class="visits-section" v-if="selected === 'visits'">
      <h2>Статистика посещений</h2>

      <div class="date-picker">
        <label for="visit-date">Дата:</label>
        <input type="date" id="visit-date" v-model="selectedDate" @change="fetchVisits" />
        <button type="button" class="refresh-button" @click="fetchVisits">Обновить</button>
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

    <!-- === Пользователи === -->
    <section class="users-section" v-if="selected === 'users'">
      <h2>Пользователи</h2>
      <table>
        <thead>
          <tr>
            <th>Админ-права</th>
            <th v-for="col in userColumns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in store.users" :key="u.user_id">
            <td>
              <button type="button" v-if="store.user.id !== u.user_id && u.role !== 'admin'" @click="makeAdmin(u.user_id)">Сделать админом</button>
              <button type="button" v-if="store.user.id !== u.user_id && u.role === 'admin'" @click="revokeAdmin(u.user_id)">Снять админа</button>
            </td>
            <td v-for="col in userColumns" :key="col">
              <span v-if="isDateField(col)">{{ formatDate(u[col]) }}</span>
              <span v-else>{{ u[col] }}</span>
            </td>
          </tr>
          <tr v-if="!store.users.length">
            <td :colspan="userColumns.length" class="no-data">Нет пользователей</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Параметры AdminSetting -->
    <section class="settings-section" v-if="selected === 'settings'">
      <h2>Параметры</h2>

      <!-- Существующие -->
      <table>
        <tr>
          <th>Ключ</th>
          <th>Значение</th>
          <th></th>
        </tr>
        <tr v-for="s in filteredSettings" :key="s.key">
          <td>{{ s.key }}</td>
          <td><input v-model="s.value" /></td>
          <td><button type="button" class="delete-icon" :disabled="s.key.startsWith('delivery_')" @click="deleteSetting(s.key)"
                      :title="s.key.startsWith('delivery_') ? 'Нельзя удалить системный параметр' : 'Удалить параметр'">🗑️</button></td>
        </tr>
      </table>

      <button type="button" class="btn-save-all" @click="saveAllSettings" :disabled="!hasSettingsChanged || savingAll">
        {{ savingAll ? 'Сохраняем…' : 'Сохранить все изменения' }}
      </button>

      <!-- Форма «Добавить новый параметр» -->
      <div class="add-setting">
        <h3>Добавить новый параметр</h3>
        <input v-model="newSetting.key" placeholder="Ключ (уникальный)"/>
        <input v-model="newSetting.value" placeholder="Значение"/>
        <button type="button" @click="onAddSetting" :disabled="!newSetting.key.trim() || newSetting.value === '' || saving==='add'">
          {{ saving==='add' ? 'Добавляем…' : 'Добавить' }}
        </button>
      </div>
    </section>

    <!-- Все отзывы -->
    <section class="all-reviews-section" v-if="selected === 'all_reviews'">
      <h2>Все отзывы</h2>
      <ul v-if="store.reviews.length">
        <li v-for="r in store.reviews" :key="r.id" class="admin-review">
          <div class="review-header">
            <strong>#{{ r.id }}</strong>
            <span>{{ r.client_name }}</span>
            <span class="review-date">{{ new Date(r.created_at).toLocaleString() }}</span>
          </div>
          <p class="user-text"><strong>Текст клиента 1:</strong> {{ r.client_text1 }}</p>
          <p class="shop-text"><strong>Ответ магазина:</strong> {{ r.shop_response }}</p>
          <p class="user-text"><strong>Текст клиента 2:</strong> {{ r.client_text2 }}</p>
          <div class="photos">
            <img v-for="url in r.photo_urls" :key="url" :src="url" alt="photo" class="admin-photo"/>
          </div>
          <div class="review-link">
            <a :href="r.link_url" target="_blank">Ссылка на оригинал →</a>
          </div>
          <button type="button" class="delete-btn" @click="deleteReview(r.id)">Удалить</button>
        </li>
      </ul>
      <p v-else>Отзывов пока нет.</p>
    </section>

    <!-- Добавить отзыв -->
    <section class="add-review-section" v-if="selected === 'add_review'">
      <h2>Добавить отзыв</h2>
      <div v-if="formError" class="error">{{ formError }}</div>
      <div v-if="formSuccess" class="success">{{ formSuccess }}</div>
      <form @submit.prevent="onSubmitReview">
        <input v-model="form.client_name" placeholder="Имя клиента" required/>
        <textarea v-model="form.client_text1" placeholder="Текст клиента 1" required></textarea>
        <textarea v-model="form.shop_response" placeholder="Ответ магазина" required></textarea>
        <textarea v-model="form.client_text2" placeholder="Текст клиента 2"></textarea>
        <input v-model="form.link_url" placeholder="Ссылка" required/>
        <div class="photos-inputs">
          <input type="file" @change="onFile($event,1)" ref="fileInput1"/>
          <input type="file" @change="onFile($event,2)" ref="fileInput2"/>
          <input type="file" @change="onFile($event,3)" ref="fileInput3"/>
        </div>
        <button type="submit" :disabled="!form.client_name || !form.client_text1 || !form.shop_response || !form.link_url || (!files[1] && !files[2] && !files[3])">
          Добавить
        </button>
      </form>
    </section>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from '@/store/index.js'

const store            = useStore()

const localSettings    = reactive([])
const originalSnapshot = ref('')
const savingAll        = ref(false)
const saving           = ref(null)
const zipFile          = ref(null)
const zipInput         = ref(null)
const editingUrl       = reactive({ shoes:false, clothing:false, accessories:false })
const selectedDate     = ref(new Date().toISOString().slice(0, 10))
const fileInput1       = ref(null)
const fileInput2       = ref(null)
const fileInput3       = ref(null)
const formError        = ref('')
const formSuccess      = ref('')
const files            = reactive({})
const selected         = ref('sheets')
const logPage          = ref(1)
const pageSize         = 10
const newSetting       = reactive({ key: '', value: '' })
const tabs             = [
  { key:'sheets',      label:'Sheets'         },
  { key:'upload',      label:'ZIP Upload'     },
  { key:'logs',        label:'Логи'           },
  { key:'visits',      label:'Посещения'      },
  { key:'users',       label:'Пользователи'   },
  { key:'settings',    label:'Параметры'      },
  { key:'all_reviews', label:'Все отзывы'     },
  { key:'add_review',  label:'Добавить отзыв' },
]

// Форма добавления отзыва
const form = reactive({
  client_name:'', client_text1:'', shop_response:'', client_text2:'', link_url:''
})

// Вычисляем список колонок по ключам первого пользователя
const preferredColumns = ['user_id', 'username', 'first_name', 'last_name', 'gender', 'phone', 'date_of_birth', 'order_count', 'total_spent']
const userColumns = computed(() => {
  if (!store.users.length) return []
  const cols = Object.keys(store.users[0])
  const first = preferredColumns.filter(c => cols.includes(c))
  const rest  = cols.filter(c => !preferredColumns.includes(c))
  return [...first, ...rest]
})

// Фильтруем параметры: убираем все, ключи которых начинаются на `sheet_url_`
const filteredSettings = computed(() =>
  localSettings.filter(s => !s.key.startsWith('sheet_url_'))
)

// Флаг: было ли хоть одно изменение?
const hasSettingsChanged = computed(() =>
  JSON.stringify(filteredSettings.value) !== originalSnapshot.value
)

const maxTotal = computed(() => {
  const hours = store.visitsData.hours || []
  return hours.length ? Math.max(...hours.map(h => h.total)) : 1
})

// Утилиты
function onFile(e,i) {
  files[i] = e.target.files[0]
}
function onZipSelected(e) {
  zipFile.value = e.target.files[0]
}

function prevPage() {
  if (logPage.value > 1) {
    logPage.value--
    store.loadLogs(pageSize, (logPage.value - 1) * pageSize)
  }
}
function nextPage() {
  if (logPage.value * pageSize < store.totalLogs) {
    logPage.value++
    store.loadLogs(pageSize, (logPage.value - 1) * pageSize)
  }
}

// Функции для форматирования
function isDateField(col) {
  return ['created_at', 'last_visit', 'updated_at', /* и любые другие */].includes(col)
}

function formatDate(val) {
  return val
    ? new Date(val).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
    : '—'
}

// Отправка нового отзыва
async function onSubmitReview() {
  // Сброс сообщений
  formError.value = ''
  formSuccess.value = ''

  // Проверки на фронте
  if (!form.client_name.trim() || !form.client_text1.trim() || !form.shop_response.trim() || !form.link_url.trim()) {
    formError.value = 'Пожалуйста, заполните все обязательные поля'
    return
  }

  // Проверка хотя бы одного фото
  if (!files[1] && !files[2] && !files[3]) {
    formError.value = 'Требуется хотя бы одна фотография'
    return
  }

  // Формируем FormData
  const fd = new FormData()
  fd.append('client_name', form.client_name)
  fd.append('client_text1', form.client_text1)
  fd.append('shop_response', form.shop_response)
  fd.append('client_text2', form.client_text2 || '') // client_text2 может быть пустым
  fd.append('link_url', form.link_url)

  // Добавляем фото
  for (let i = 1; i <= 3; i++) {
    if (files[i]) fd.append(`photo${i}`, files[i])
  }

  try {
    // Отправка и получение сообщения об успехе
    formSuccess.value = await store.createReview(fd)
    // очистка
    Object.keys(form).forEach(k => form[k]='')
    Object.keys(files).forEach(k => delete files[k])
    // сброс input[type=file]
    fileInput1.value && (fileInput1.value.value = '')
    fileInput2.value && (fileInput2.value.value = '')
    fileInput3.value && (fileInput3.value.value = '')
  } catch (err) {
    formError.value = err.message
  }
}

// Другие действия
function submitZip() {
  if (!zipFile.value) return
  store.uploadZip(zipFile.value).then(() => {
    zipFile.value = null
    zipInput.value.value = ''
  })
}

function deleteReview(id) {
  if (confirm(`Удалить отзыв #${id}?`)) store.deleteReview(id)
}

// Сохраняем все изменённые параметры подряд
async function saveAllSettings() {
  savingAll.value = true
  try {
    const changed = filteredSettings.value.filter(s => {
      const orig = JSON.parse(originalSnapshot.value)
        .find(o => o.key === s.key)
      return orig && orig.value !== s.value
    })
    for (const s of changed) {
      await store.saveSetting(s.key, s.value)
    }
    await store.fetchSettings()
    // оригинальный снимок обновится через watch
  } catch (err) {
    alert(err.message || 'Ошибка при сохранении')
  } finally {
    savingAll.value = false
  }
}

// Удаляем один параметр
async function deleteSetting(key) {
  if (!confirm(`Удалить параметр «${key}»?`)) return;
  savingAll.value = true;
  try {
    await store.deleteSetting(key);
    await store.fetchSettings();
  } catch (err) {
    alert(err.message || 'Ошибка при удалении');
  } finally {
    savingAll.value = false;
  }
}

async function onAddSetting() {
  saving.value = 'add'
  await store.saveSetting(newSetting.key.trim(), newSetting.value)
  await store.fetchSettings()
  newSetting.key = ''
  newSetting.value = ''
  saving.value = null
}

function startEdit(cat) {
  editingUrl[cat] = true
}

function fetchVisits() {
  store.loadVisits(selectedDate.value)
}

async function onSaveUrl(cat) {
  if (await store.saveSheetUrl(cat)) editingUrl[cat] = false
}

async function makeAdmin(userId) {
  try {
    await store.updateUserRole(userId, 'admin')
  } catch (e) {
    alert(e.message)
  }
}
async function revokeAdmin(userId) {
  try {
    await store.updateUserRole(userId, 'customer')
  } catch (e) {
    alert(e.message)
  }
}

// При монтировании — подгрузим все по умолчанию
onMounted(() => {
  store.loadSheetUrls()
  store.loadLogs(pageSize, 0)
  store.loadVisits(selectedDate.value)
  store.fetchSettings()
  store.fetchReviews()
  store.fetchUsers()
})

// Когда store.settings обновляются — заполняем localSettings и снимаем снимок
// watch(
//   () => store.settings,
//   (newSettings) => {
//     const filtered = newSettings
//       .filter(s => !s.key.startsWith('sheet_url_'))
//     // Обновляем или добавляем
//     filtered.forEach(ns => {
//       const idx = localSettings.findIndex(ls => ls.key === ns.key)
//       if (idx >= 0) {
//         localSettings[idx].value = ns.value
//       } else {
//         localSettings.push({ key: ns.key, value: ns.value })
//       }
//     })
//     // Убираем удалённые
//     for (let i = localSettings.length - 1; i >= 0; i--) {
//       if (!filtered.some(ns => ns.key === localSettings[i].key)) {
//         localSettings.splice(i, 1)
//       }
//     }
//     // Снимок для кнопки «Сохранить всё»
//     originalSnapshot.value = JSON.stringify(
//       localSettings.map(s => ({ key: s.key, value: s.value }))
//     )
//   },
//   { immediate: true }
// )

// **Новый watch**: при каждом переключении вкладки обновляем её данные
watch(selected, (tab) => {
  switch(tab) {
    case 'sheets':
      store.loadSheetUrls()
      break
    case 'upload':
      // ничего не нужно грузить
      break
    case 'logs':
      logPage.value = 1
      store.loadLogs(pageSize, 0)
      break
    case 'visits':
      store.loadVisits(selectedDate.value)
      break
    case 'users':
      store.fetchUsers()
      break
    case 'settings':
      store.fetchSettings()
      break
    case 'all_reviews':
      store.fetchReviews()
      break
    case 'add_review':
      // ничего не грузим
      break
  }
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
/* Пагинация логов */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  flex-wrap: wrap;
}

.pagination-controls button {
  background: #007bff;
  color: #fff;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background 0.2s;
}

.pagination-controls button:disabled {
  background: #ccc;
  color: #666;
  cursor: not-allowed;
}

.pagination-controls span {
  font-size: 0.9em;
  color: #eee;
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
  text-align: center;
  padding: 12px;
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

/* Навигационные табы */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.tabs button {
  padding: 8px 12px;
  background: #eee;
  border: none;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.tabs button.active {
  background: #333;
  color: #fff;
}

/* Секция «Параметры» */
.settings-section {
  margin-top: 24px;
}
.settings-section table {
  width: 100%;
  border-collapse: collapse;
}
.settings-section th,
.settings-section td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}
.settings-section button {
  padding: 4px 8px;
  cursor: pointer;
}
.add-setting {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.add-setting input {
  padding: 6px;
  flex: 1 1 200px;
}
.add-setting button {
  padding: 6px 12px;
}
.delete-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1em;
  color: #e94f37;
  padding: 2px;
  line-height: 1;
  transition: color 0.2s;
}
.settings-section .btn-save-all {
  margin-top: 16px;
  padding: 8px 16px;
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}
.settings-section .btn-save-all:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Секция «Все отзывы» */
.all-reviews-section {
  margin-top: 24px;
}
.all-reviews-section ul {
  list-style: none;
  padding: 0;
}
.all-reviews-section li {
  padding: 8px 0;
  border-bottom: 1px solid #ddd;
}
.all-reviews-section button {
  margin-left: 12px;
  padding: 2px 6px;
  cursor: pointer;
}

/* Секция «Добавить отзыв» */
.add-review-section {
  margin-top: 24px;
}
.add-review-section form {
  display: grid;
  gap: 12px;
  max-width: 400px;
}
.add-review-section input,
.add-review-section textarea {
  width: 100%;
  padding: 6px;
  box-sizing: border-box;
}
.add-review-section button {
  padding: 8px 12px;
  cursor: pointer;
}
.error {
  color: #e94f37;
  margin-bottom: 8px;
}
.success {
  color: #4caf50;
  margin-bottom: 8px;
}

/* Поля загрузки фотографий */
.photos-inputs {
  margin-bottom: 4px;
}
.photos-inputs input {
  display: block;
  margin-bottom: 8px;
}

.admin-review {
  border: 1px solid #ccc;
  padding: 12px;
  margin-bottom: 16px;
  border-radius: 6px;
}
.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.review-date { color: #888; font-size: 0.9em; }
.user-text, .shop-text {
  margin: 4px 0;
}
.photos {
  display: flex;
  gap: 8px;
  margin: 8px 0;
}
.admin-photo {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
}
.delete-btn {
  background: #e94f37;
  color: white;
  border: none;
  padding: 6px 12px;
  cursor: pointer;
  border-radius: 4px;
}
.review-link a {
  color: #007bff;
  text-decoration: none;
}

.users-section {
  margin-top: 24px;
}
.users-section table {
  width: 100%;
  border-collapse: collapse;
}
.users-section th, .users-section td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
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
    /* Листы отзывов */
  .admin-review {
    padding: 8px;
    font-size: 14px;
  }
  .review-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  .photos {
    flex-wrap: wrap;
    justify-content: flex-start;
  }
  .admin-photo {
    width: 60px;
    height: 60px;
  }

  /* Формы и табы */
  .tabs {
    flex-wrap: wrap;
    gap: 4px;
  }
  .tabs button {
    flex: 1 1 45%;
    margin-bottom: 4px;
  }

  /* Логи */
  .logs-table {
    font-size: 12px;
  }
  .logs-table th, .logs-table td {
    padding: 4px;
  }

  .pagination-controls {
    flex-direction: column;
    gap: 8px;
  }
  .pagination-controls button {
    width: 100%;
    padding: 8px 0;
    font-size: 1em;
  }
  .pagination-controls span {
    margin: 0 8px;
  }

  /* Google Sheets / ZIP */
  .sheet-input {
    width: 100% !important;
    margin-bottom: 8px;
  }
  .sheet-save, .sheet-import, .upload-section button {
    width: 100%;
  }

  .tabs {
    flex-wrap: wrap;
    gap: 4px;
  }
  .tabs button {
    flex: 1 1 45%;
  }

  .sheet-block {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .sheet-input {
    width: 100%;
  }
  .sheet-save,
  .sheet-import {
    width: 100%;
  }

  .upload-section form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .upload-section input,
  .upload-section button {
    width: 100%;
  }

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

  .chart-wrapper {
    max-width: 100%;
  }
  .bar-chart {
    height: 200px;
  }
  .bar {
    margin: 0 1px;
  }
  .bar-label, .bar-value {
    font-size: 10px;
  }

  .users-section table {
    display: block;
    width: 100%;
    overflow-x: auto;
  }

  .admin-review {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .photos {
    flex-wrap: wrap;
  }
  .admin-photo {
    width: 60px;
    height: 60px;
  }

}

</style>
