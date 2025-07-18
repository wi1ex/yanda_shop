<template>
  <div class="admin-page">
    <h1>Админ-панель</h1>

    <nav class="tabs">
      <button type="button" v-for="t in tabs" :key="t.key" :class="{ active: selected === t.key }" @click="selected = t.key">
        {{ t.label }}
      </button>
    </nav>

    <!-- Превью-проверка -->
    <section class="preview-section" v-if="selected==='preview'">
      <h2>Превью: Sheets & Images</h2>

      <div class="combined-preview">
        <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="zip-input-block">
          <label>{{ catLabel(cat) }}.zip</label>
          <input type="file" @change="onPreviewZip($event,cat)" accept=".zip"/>
        </div>

        <button @click="onPreviewAll"
                :disabled="isAny(store.previewSheetLoading) || isAny(store.previewZipLoading) || !hasAnyZip"
                :aria-busy="isAny(store.previewSheetLoading) || isAny(store.previewZipLoading)">
          {{ (isAny(store.previewSheetLoading)||isAny(store.previewZipLoading)) ? 'Проверяем…' : 'Проверить всё' }}
        </button>
      </div>

      <!-- 3 Google Sheets -->
      <div class="sheet-preview-block">
        <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="preview-result">
          <h4>{{ catLabel(cat) }}</h4>
          <div v-if="store.previewSheetLoading[cat]">…</div>
          <div v-else-if="store.previewSheetResult[cat]">
            <p>Всего строк: {{ store.previewSheetResult[cat].total_rows }}</p>
            <p>Ошибок: {{ store.previewSheetResult[cat].invalid_count }}</p>
            <ul v-if="store.previewSheetResult[cat].errors?.length">
              <li v-for="e in store.previewSheetResult[cat].errors" :key="e.variant_sku">
                <strong>{{ e.variant_sku }}</strong>: {{ e.messages.join('; ') }}
              </li>
            </ul>
            <div v-else>Все в порядке</div>
          </div>
        </div>
      </div>

      <!-- 3 ZIP для изображений -->
      <div class="zip-preview-block">
        <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="preview-result">
          <h4>{{ catLabel(cat) }}</h4>
          <div v-if="store.previewZipLoading[cat]">…</div>
          <div v-else-if="store.previewZipResult[cat]">
            <div v-if="store.previewZipResult[cat].error" class="error">{{ store.previewZipResult[cat].error }}</div>
            <div v-else>
              <ul v-if="store.previewZipResult[cat].errors?.length">
                <li v-for="err in store.previewZipResult[cat].errors" :key="err.sku_or_filename">
                  <strong>{{ err.sku_or_filename }}</strong>: {{ err.messages.join('; ') }}
                </li>
              </ul>
              <div v-else>
                Нет ошибок
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

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
const selected         = ref('preview')
const logPage          = ref(1)
const pageSize         = 10
const newSetting       = reactive({ key: '', value: '' })
const tabs             = [
  { key:'preview',     label:'Проверка данных'      },
  { key:'sheets',      label:'Загрузка таблиц'      },
  { key:'upload',      label:'Загрузка изображений' },
  { key:'logs',        label:'Логи сервера'         },
  { key:'visits',      label:'Статистика посещений' },
  { key:'users',       label:'Список пользователей' },
  { key:'settings',    label:'Настройка переменных' },
  { key:'all_reviews', label:'Список отзывов'       },
  { key:'add_review',  label:'Добавить отзыв'       },
]

const zipPreviewFiles = reactive({ shoes:null, clothing:null, accessories:null });

const hasAnyZip = computed(() =>
  Object.values(zipPreviewFiles).some(f=>f)
);

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
async function onPreviewAll() {
  await store.previewEverything(zipPreviewFiles);
  Object.keys(zipPreviewFiles).forEach(cat => zipPreviewFiles[cat] = null);
}

function onPreviewZip(e,cat) {
  zipPreviewFiles[cat] = e.target.files[0];
}

function catLabel(cat) {
  return cat.charAt(0).toUpperCase() + cat.slice(1);
}

function isAny(obj) {
  return Object.values(obj).some(v => v);
}

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
  savingAll.value = true
  try {
    await store.deleteSetting(key)
    await store.fetchSettings()
  } catch (err) {
    alert(err.message || 'Ошибка при удалении')
  } finally {
    savingAll.value = false
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
watch(
  () => store.settings,
  (newSettings) => {
    const filtered = newSettings
      .filter(s => !s.key.startsWith('sheet_url_'))
    // Обновляем или добавляем
    filtered.forEach(ns => {
      const idx = localSettings.findIndex(ls => ls.key === ns.key)
      if (idx >= 0) {
        localSettings[idx].value = ns.value
      } else {
        localSettings.push({ key: ns.key, value: ns.value })
      }
    })
    // Убираем удалённые
    for (let i = localSettings.length - 1; i >= 0; i--) {
      if (!filtered.some(ns => ns.key === localSettings[i].key)) {
        localSettings.splice(i, 1)
      }
    }
    // Снимок для кнопки «Сохранить всё»
    originalSnapshot.value = JSON.stringify(
      localSettings.map(s => ({ key: s.key, value: s.value }))
    )
  },
  { immediate: true }
)

// **Новый watch**: при каждом переключении вкладки обновляем её данные
watch(selected, (tab) => {
  switch(tab) {
    case 'preview':
      store.loadSheetUrls()
      break
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
  padding: 0.5rem;
  color: $white-100;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}

/* Навигационные табы */
.tabs {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.tabs button {
  width: 100%;
  padding: 0.75rem;
  background: $grey-90;
  border: 1px solid $grey-87;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: 500;
  color: $black-100;
  min-height: 44px;
}
.tabs button:hover {
  background: $grey-89;
}
.tabs button.active {
  background: $red-active;
  color: $white-100;
  border-color: $red-active;
}

/* Заголовки секций */
section h2 {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  border-bottom: 2px solid $grey-30;
  padding-bottom: 0.5rem;
  color: $white-100;
}

/* Кнопки общего стиля */
.button,
button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  background: $red-active;
  color: $white-100;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
  min-height: 44px;
  width: 100%;
}
.button:disabled,
button:disabled {
  background: $grey-30;
  cursor: not-allowed;
}
.button:hover:not(:disabled),
button:hover:not(:disabled) {
  background: darken($red-active, 10%);
}

/* Превью-проверка */
.preview-section {
  margin-bottom: 1.5rem;
}

.combined-preview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.zip-input-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.zip-input-block label {
  font-weight: 600;
  color: $white-100;
}
.zip-input-block input[type="file"] {
  padding: 0.75rem;
  background: $black-10;
  border: 1px solid $grey-30;
  border-radius: 4px;
  color: $white-100;
  width: 100%;
}

.preview-result {
  background: $black-10;
  padding: 0.75rem;
  border-radius: 6px;
}
.preview-result h4 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: $white-100;
}
.preview-result p {
  margin: 0.25rem 0;
  color: $white-80;
}
.preview-result ul {
  margin: 0.5rem 0 0;
  padding-left: 1rem;
}
.preview-result li {
  margin-bottom: 0.3rem;
  color: $white-60;
}
.preview-result .error {
  color: $red-error;
  font-weight: 600;
}

/* Секции загрузки и импорта */
.sheets-section,
.upload-section {
  margin-bottom: 1.5rem;
}

.sheet-block {
  background: $black-10;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 0.75rem;
}
.sheet-block h3 {
  margin-top: 0;
  font-size: 1.1rem;
  color: $white-100;
}
.sheet-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid $grey-30;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  background: $black-25;
  color: $white-100;
}

/* Логи */
.logs-section {
  margin-bottom: 1.5rem;
}
.logs-table {
  width: 100%;
  border-collapse: collapse;
  overflow-x: auto;
  display: block;
}
.logs-table th,
.logs-table td {
  border: 1px solid $grey-30;
  padding: 0.5rem;
  text-align: center;
  font-size: 0.75rem;
}
.logs-table th {
  background: $black-10;
  color: $white-100;
}
.no-logs {
  text-align: center;
  padding: 0.75rem;
  font-style: italic;
  color: $white-40;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

/* Статистика посещений */
.visits-section {
  margin-bottom: 1.5rem;
}
.date-picker {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.date-picker input[type="date"] {
  padding: 0.75rem;
  border: 1px solid $grey-30;
  border-radius: 4px;
  background: $black-25;
  color: $white-100;
  width: 100%;
}
.chart-wrapper {
  width: 100%;
  overflow-x: auto;
}
.bar-chart {
  height: 150px;
  border-left: 1px solid $grey-30;
  border-bottom: 1px solid $grey-30;
}
.bar-label {
  font-size: 0.6rem;
  color: $white-60;
}
.bar-value {
  font-size: 0.6rem;
  color: $white-100;
}

/* Пользователи */
.users-section table {
  width: 100%;
  border-collapse: collapse;
  overflow-x: auto;
  display: block;
}

/* Настройки */
.settings-section table {
  width: 100%;
  border-collapse: collapse;
  overflow-x: auto;
  display: block;
}
.add-setting {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.add-setting input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid $grey-30;
  border-radius: 4px;
  background: $black-25;
  color: $white-100;
}

/* Отзывы */
.all-reviews-section li,
.admin-review {
  background: $black-10;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 0.75rem;
}
.review-header {
  display: flex;
  flex-direction: column;
}
.photos {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.admin-photo {
  max-width: 100%;
  height: auto;
}

/* Добавить отзыв */
.add-review-section form {
  display: grid;
  gap: 0.75rem;
}
.add-review-section input,
.add-review-section textarea {
  padding: 0.75rem;
  border: 1px solid $grey-30;
  border-radius: 4px;
  background: $black-25;
  color: $white-100;
  width: 100%;
}

/* Мобильная адаптация */
@media (max-width: 600px) {
  .admin-page {
    padding: 0.5rem;
  }
  h1 { font-size: 1.25rem; }
  h2 { font-size: 1.1rem; }
  h3 { font-size: 1rem; }
  p, li, td, th { font-size: 0.8rem; }
  .logs-table,
  .users-section table,
  .settings-section table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
}

</style>
