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
      <h2>Проверка и загрузка данных</h2>
      <div class="combined-preview">
        <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="zip-input-block">
          <label>{{ catLabel(cat) }}.zip</label>
          <input type="file" @change="onPreviewZip($event,cat)" accept=".zip" />
        </div>
        <button @click="onProcessAll" :disabled="isProcessing" :aria-busy="isProcessing">
          {{ isProcessing ? 'Загружаем…' : 'Загрузить данные' }}
        </button>
      </div>
      <h3>Результаты импорта</h3>
      <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" v-if="statsLoaded">
        <h4>{{ catLabel(cat) }}</h4>
        <p>
          Таблица - добавлено: {{ store.adminStore.sheetStats[cat].added }},
          обновлено: {{ store.adminStore.sheetStats[cat].updated }},
          удалено: {{ store.adminStore.sheetStats[cat].deleted }}
        </p>
        <p>
          Изображения - добавлено: {{ store.adminStore.imageStats[cat].added }},
          заменено: {{ store.adminStore.imageStats[cat].replaced }},
          удалено: {{ store.adminStore.imageStats[cat].deleted }},
          ошибок: {{ store.adminStore.imageStats[cat].warns }}
        </p>
      </div>
      <div class="sheet-preview-block">
        <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="preview-result">
          <h4>{{ catLabel(cat) }}</h4>
          <div v-if="store.adminStore.previewSheetLoading[cat]">…</div>
          <div v-else-if="store.adminStore.previewSheetResult[cat]">
            <p>Всего строк: {{ store.adminStore.previewSheetResult[cat].total_rows }}</p>
            <p>Ошибок: {{ store.adminStore.previewSheetResult[cat].invalid_count }}</p>
            <ul v-if="store.adminStore.previewSheetResult[cat].errors?.length">
              <li v-for="e in store.adminStore.previewSheetResult[cat].errors" :key="e.variant_sku">
                <strong>{{ e.variant_sku }}</strong>: {{ e.messages.join('; ') }}
              </li>
            </ul>
            <div v-else>Все в порядке</div>
          </div>
        </div>
      </div>
      <div class="zip-preview-block">
        <div v-for="cat in ['shoes','clothing','accessories']" :key="cat" class="preview-result">
          <h4>{{ catLabel(cat) }}</h4>
          <div v-if="store.adminStore.previewZipLoading[cat]">…</div>
          <div v-else-if="store.adminStore.previewZipResult[cat]">
            <p>Всего ожидается: {{ store.adminStore.previewZipResult[cat].total_expected }}</p>
            <p>Обработано: {{ store.adminStore.previewZipResult[cat].total_processed }}</p>
            <ul v-if="store.adminStore.previewZipResult[cat].errors?.length">
              <li v-for="err in store.adminStore.previewZipResult[cat].errors" :key="err.sku_or_filename">
                <strong>{{ err.sku_or_filename }}</strong>: {{ err.messages.join('; ') }}
              </li>
            </ul>
            <div v-else>Все в порядке</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Логи изменений товаров/изображений -->
    <section class="logs-section" v-if="selected === 'logs'">
      <h2>Последние 10 событий</h2>
      <div v-if="store.adminStore.logsLoading" class="loading-logs">Загрузка журналов...</div>
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
            <tr v-for="log in store.adminStore.logs" :key="log.id">
              <td>{{ log.id }}</td>
              <td>{{ log.author_id }}</td>
              <td>{{ log.author_name }}</td>
              <td>{{ log.action_type }}</td>
              <td>{{ log.description }}</td>
              <td>{{ log.timestamp }}</td>
            </tr>
            <tr v-if="store.adminStore.logs.length === 0">
              <td colspan="6" class="no-logs">Нет записей</td>
            </tr>
          </tbody>
        </table>
        <div class="pagination-controls">
          <button type="button" @click="prevPage" :disabled="logPage===1">← Предыдущие</button>
          <span>Стр. {{ logPage }} из {{ Math.ceil(store.adminStore.totalLogs / pageSize) }}</span>
          <button type="button" @click="nextPage" :disabled="logPage*pageSize>=store.adminStore.totalLogs">Следующие →</button>
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

      <div v-if="store.adminStore.visitsLoading" class="loading-visits">Загрузка данных...</div>

      <div v-else class="chart-wrapper">
        <!-- Если нет данных, выводим сообщение -->
        <div v-if="!store.adminStore.visitsData.hours.length" class="no-data">Нет данных за выбранный день</div>
        <!-- Иначе: «самописный» бар-чарт -->
        <div v-else class="bar-chart">
          <div v-for="h in store.adminStore.visitsData.hours" :key="h.hour" class="bar" :style="{ height: (h.total / maxTotal * 100) + '%' }">
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
          <tr v-for="u in store.adminStore.users" :key="u.user_id">
            <td>
              <button type="button" v-if="store.userStore.user.id !== u.user_id && u.role !== 'admin'" @click="makeAdmin(u.user_id)">Сделать админом</button>
              <button type="button" v-if="store.userStore.user.id !== u.user_id && u.role === 'admin'" @click="revokeAdmin(u.user_id)">Снять админа</button>
            </td>
            <td v-for="col in userColumns" :key="col">
              <span v-if="isDateField(col)">{{ formatDate(u[col]) }}</span>
              <span v-else>{{ u[col] }}</span>
            </td>
          </tr>
          <tr v-if="!store.adminStore.users.length">
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
        <tr v-for="s in localSettings" :key="s.key">
          <td>{{ s.key }}</td>
          <td><input v-model="s.value" /></td>
          <td><button type="button" class="delete-icon" :disabled="s.key.startsWith('delivery_') || s.key.startsWith('sheet_url_')" @click="deleteSetting(s.key)"
                      :title="s.key.startsWith('delivery_') || s.key.startsWith('sheet_url_') ? 'Нельзя удалить системный параметр' : 'Удалить параметр'">🗑️</button></td>
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
      <ul v-if="store.globalStore.reviews.length">
        <li v-for="r in store.globalStore.reviews" :key="r.id" class="admin-review">
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
      <form ref="reviewForm" @submit.prevent="onSubmitReview">
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
        <button type="submit" :disabled="isLoading || !form.client_name || !form.client_text1 || !form.shop_response || !form.link_url || (!files[1] && !files[2] && !files[3])">
          {{ isLoading ? 'Отправка…' : 'Добавить' }}
        </button>
      </form>
    </section>

    <!-- Все заявки -->
    <section class="requests-section" v-if="selected === 'requests'">
      <h2>Заявки клиентов</h2>
      <ul v-if="store.adminStore.requests.length" class="requests-list">
        <li v-for="r in store.adminStore.requests" :key="r.id" class="request-item">
          <div class="request-header">
            <strong>#{{ r.id }}</strong>
            <span>{{ r.name }}</span>
            <span>{{ r.email || '—' }}</span>
            <span class="date">{{ new Date(r.created_at).toLocaleString() }}</span>
          </div>
          <p>Артикул: {{ r.sku || '—' }}</p>
          <a v-if="r.file_url" :href="r.file_url" target="_blank">Файл</a>
          <button @click="onDeleteRequest(r.id)">Удалить</button>
        </li>
      </ul>
      <p v-else>Заявок пока нет.</p>
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
const reviewForm       = ref(null)
const isLoading        = ref(false)
const isProcessing     = ref(false)
const statsLoaded      = ref(false);
const tabs             = [
  { key:'preview',     label:'Проверка и загрузка данных' },
  { key:'logs',        label:'Логи сервера' },
  { key:'visits',      label:'Статистика посещений' },
  { key:'users',       label:'Список пользователей' },
  { key:'settings',    label:'Настройка переменных' },
  { key:'all_reviews', label:'Список отзывов' },
  { key:'add_review',  label:'Добавить отзыв' },
  { key:'requests',    label:'Заявки клиентов' },
]

const zipPreviewFiles = reactive({ shoes:null, clothing:null, accessories:null });

// Форма добавления отзыва
const form = reactive({
  client_name:'', client_text1:'', shop_response:'', client_text2:'', link_url:''
})

// Вычисляем список колонок по ключам первого пользователя
const preferredColumns = ['user_id', 'username', 'first_name', 'last_name', 'gender', 'phone', 'date_of_birth', 'order_count', 'total_spent']
const userColumns = computed(() => {
  if (!store.adminStore.users.length) return []
  const cols = Object.keys(store.adminStore.users[0])
  const first = preferredColumns.filter(c => cols.includes(c))
  const rest  = cols.filter(c => !preferredColumns.includes(c))
  return [...first, ...rest]
})

// Флаг: было ли хоть одно изменение?
const hasSettingsChanged = computed(() =>
  JSON.stringify(localSettings) !== originalSnapshot.value
)

const maxTotal = computed(() => {
  const hours = store.adminStore.visitsData.hours || []
  return hours.length ? Math.max(...hours.map(h => h.total)) : 1
})

// Утилиты
function resetReviewForm() {
  // 1) нативный reset всех <input> и <textarea>
  reviewForm.value?.reset()
  // 2) очистка реактивного объекта
  Object.keys(form).forEach(k => form[k] = '')
  // 3) очистка объекта files
  for (const k of Object.keys(files)) { delete files[k] }
  // 4) очистка файловых инпутов
  [fileInput1, fileInput2, fileInput3].forEach(refEl => {
    if (refEl.value) refEl.value.value = ''
  })
}

async function onProcessAll() {
  isProcessing.value = true;
  statsLoaded.value = false;
  // Сбросить прошлые превью
  Object.keys(store.adminStore.previewSheetResult).forEach(cat => {
    store.adminStore.previewSheetResult[cat] = null;
  });
  Object.keys(store.adminStore.previewZipResult).forEach(cat => {
    store.adminStore.previewZipResult[cat] = null;
  });
  // Включить загрузку
  Object.keys(store.adminStore.previewSheetLoading).forEach(cat => {
    store.adminStore.previewSheetLoading[cat] = true;
  });
  Object.keys(store.adminStore.previewZipLoading).forEach(cat => {
    store.adminStore.previewZipLoading[cat] = !!zipPreviewFiles[cat];
  });

  try {
    // передаём object { shoes: File|null, clothing: File|null, accessories: File|null }
    const filesMap = { ...zipPreviewFiles };
    await store.adminStore.syncAll(filesMap);
    statsLoaded.value = true;
    alert('Всё проверено и загружено без ошибок');

  } catch (e) {
    const data = e.response?.data || {};
    // Заполнить preview по таблицам
    Object.entries(data.sheet_errors || {}).forEach(([cat, report]) => {
      store.adminStore.previewSheetResult[cat] = report;
    });
    // Заполнить preview по картинкам
    Object.entries(data.image_errors || {}).forEach(([cat, report]) => {
      store.adminStore.previewZipResult[cat] = report;
    });
    alert('Найдены ошибки – см. детали выше');

  } finally {
    isProcessing.value = false;
    // Отключить все спиннеры
    Object.keys(store.adminStore.previewSheetLoading).forEach(cat => {
      store.adminStore.previewSheetLoading[cat] = false;
    });
    Object.keys(store.adminStore.previewZipLoading).forEach(cat => {
      store.adminStore.previewZipLoading[cat] = false;
    });
  }
}

function onPreviewZip(e,cat) {
  zipPreviewFiles[cat] = e.target.files[0];
}

function catLabel(cat) {
  return cat.charAt(0).toUpperCase() + cat.slice(1);
}

function onFile(e, idx) {
  const f = e.target.files[0]
  if (f) files[idx] = f
}

function prevPage() {
  if (logPage.value > 1) {
    logPage.value--
    store.adminStore.loadLogs(pageSize, (logPage.value - 1) * pageSize)
  }
}

function nextPage() {
  if (logPage.value * pageSize < store.adminStore.totalLogs) {
    logPage.value++
    store.adminStore.loadLogs(pageSize, (logPage.value - 1) * pageSize)
  }
}

// Функции для форматирования
function isDateField(col) {
  return ['created_at', 'last_visit', 'updated_at', /* и любые другие */].includes(col)
}

function formatDate(val) {
  return val ? new Date(val).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' }) : '—'
}

// Отправка нового отзыва
async function onSubmitReview() {
  // 1) сброс предыдущих сообщений
  formError.value = ''
  formSuccess.value = ''
  isLoading.value = true
  // 2) валидация обязательных полей
  if (!form.client_name.trim() ||
      !form.client_text1.trim() ||
      !form.shop_response.trim() ||
      !form.link_url.trim()) {
    formError.value = 'Пожалуйста, заполните все обязательные поля'
    isLoading.value = false
    return
  }
  // 3) проверка хотя бы одного фото
  if (!files[1] && !files[2] && !files[3]) {
    formError.value = 'Требуется хотя бы одна фотография'
    isLoading.value = false
    return
  }
  // 4) сбор FormData
  const fd = new FormData()
  fd.append('client_name',  form.client_name)
  fd.append('client_text1', form.client_text1)
  fd.append('shop_response',form.shop_response)
  fd.append('client_text2', form.client_text2 || '')
  fd.append('link_url',     form.link_url)
  for (let i = 1; i <= 3; i++) {
    if (files[i]) fd.append(`photo${i}`, files[i])
  }
  // 5) отправка
  try {
    formSuccess.value = await store.adminStore.createReview(fd)
    resetReviewForm()
  } catch (err) {
    formError.value = err.message || 'Ошибка при отправке'
  } finally {
    isLoading.value = false
  }
}

// Функция удаления отзыва
async function deleteReview(id) {
  if (confirm(`Удалить отзыв #${id}?`)) {
    await store.adminStore.deleteReview(id)
    await store.globalStore.fetchReviews()
  }
}

// Функция удаления заявки
async function onDeleteRequest(id) {
  if (confirm(`Удалить заявку #${id}?`)) {
    await store.adminStore.deleteRequest(id)
    await store.adminStore.fetchRequests()
  }
}

// Сохраняем все изменённые параметры подряд
async function saveAllSettings() {
  savingAll.value = true
  try {
    const changed = localSettings.filter(s => {
      const orig = JSON.parse(originalSnapshot.value)
        .find(o => o.key === s.key)
      return orig && orig.value !== s.value
    })
    for (const s of changed) {
      await store.adminStore.saveSetting(s.key, s.value)
    }
    await store.adminStore.fetchSettings()
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
    await store.adminStore.deleteSetting(key)
    await store.adminStore.fetchSettings()
  } catch (err) {
    alert(err.message || 'Ошибка при удалении')
  } finally {
    savingAll.value = false
  }
}

async function onAddSetting() {
  saving.value = 'add'
  await store.adminStore.saveSetting(newSetting.key.trim(), newSetting.value)
  await store.adminStore.fetchSettings()
  newSetting.key = ''
  newSetting.value = ''
  saving.value = null
}

function fetchVisits() {
  store.adminStore.loadVisits(selectedDate.value)
}

async function makeAdmin(userId) {
  try {
    await store.adminStore.updateUserRole(userId, 'admin')
  } catch (e) {
    alert(e.message)
  }
}
async function revokeAdmin(userId) {
  try {
    await store.adminStore.updateUserRole(userId, 'customer')
  } catch (e) {
    alert(e.message)
  }
}

// При монтировании — подгрузим все по умолчанию
onMounted(() => {
  store.adminStore.loadLogs(pageSize, 0)
  store.adminStore.loadVisits(selectedDate.value)
  store.adminStore.fetchSettings()
  store.globalStore.fetchReviews()
  store.adminStore.fetchUsers()
  store.adminStore.fetchRequests()
})

// Когда store.settings обновляются — заполняем localSettings и снимаем снимок
watch(
  () => store.adminStore.settings,
  (newSettings) => {
    // синхронизируем localSettings со всеми параметрами из бекенда
    newSettings.forEach(ns => {
      const idx = localSettings.findIndex(ls => ls.key === ns.key)
      if (idx >= 0) {
        localSettings[idx].value = ns.value
      } else {
        localSettings.push({ key: ns.key, value: ns.value })
      }
    })
    // удаляем те, которых больше нет на бекенде
    for (let i = localSettings.length - 1; i >= 0; i--) {
      if (!newSettings.some(ns => ns.key === localSettings[i].key)) {
        localSettings.splice(i, 1)
      }
    }
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
      // ничего не грузим
      break
    case 'logs':
      logPage.value = 1
      store.adminStore.loadLogs(pageSize, 0)
      break
    case 'visits':
      store.adminStore.loadVisits(selectedDate.value)
      break
    case 'users':
      store.adminStore.fetchUsers()
      break
    case 'settings':
      store.adminStore.fetchSettings()
      break
    case 'all_reviews':
      store.globalStore.fetchReviews()
      break
    case 'add_review':
      // ничего не грузим
      break
    case 'requests':
      store.adminStore.fetchRequests()
      break
  }
})

</script>

<style scoped lang="scss">
/* =====================
   Container & Headings
   ===================== */
.admin-page {
  margin-top: 12vh;
  padding: 2vw;
  color: #fff;
  h1 {
    text-align: center;
    margin-bottom: 1.5rem;
  }
  section {
    margin: 2rem 0;
    h2 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
      border-bottom: 1px solid #444;
      padding-bottom: .5rem;
    }
    h3 {
      font-size: 1.25rem;
      margin: 1rem 0 .5rem;
    }
  }
  .no-data {
    color: #bbb;
    text-align: center;
    font-style: italic;
    padding: .5rem 0;
  }
}
/* ===== Tabs ===== */
.tabs {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #444;
  &::-webkit-scrollbar {
    height: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2);
    border-radius: 2px;
  }
  button {
    flex: 0 0 auto;
    padding: 0.6rem 1rem;
    background: #333;
    color: #fff;
    border: none;
    border-radius: 4px;
    white-space: nowrap;
    transition: background 0.2s;
    &.active {
      background: #007bff;
    }
  }
}
/* ===== Preview & Import ===== */
.preview-section {
  h2 {
    font-size: 1.4rem;
    margin-bottom: 1.2rem;
  }
  h3 {
    font-size: 1.2rem;
    margin: 1.5rem 0 1rem;
    border-bottom: 1px solid #444;
    padding-bottom: .5rem;
  }
  .combined-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 2rem;
    .zip-input-block {
      flex: 1 1 30%;
      min-width: 200px;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      label {
        font-weight: bold;
      }
      input[type="file"] {
        padding: .5rem;
        background: #1e222b;
        border: 1px solid #444;
        border-radius: 4px;
        color: #fff;
      }
    }
    button {
      flex: 1 1 120px;
      align-self: flex-end;
      padding: .75rem 1.25rem;
      background: #007bff;
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: background .2s;
      &:disabled {
        background: #555;
        cursor: not-allowed;
      }
    }
  }
  .sheet-preview-block,
  .zip-preview-block {
    display: flex;
    flex-wrap: wrap;
    margin-top: 2rem;
    gap: 1rem;
    .preview-result {
      flex: 1 1 30%;
      min-width: 200px;
      background: #252a3b;
      padding: 1rem;
      border-radius: 8px;
      h4 {
        margin: 0 0 .5rem;
        font-size: 1rem;
        color: #fff;
      }
      p {
        margin: .3rem 0;
        font-size: .9rem;
      }
      ul {
        margin: .5rem 0 0 1rem;
        color: #ddd;
        list-style: disc;
      }
      li {
        margin-bottom: .3rem;
      }
      .error {
        color: #e94f37;
      }
    }
  }
}
/* ===== Logs ===== */
.logs-section {
  .logs-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
    display: block;
    overflow-x: auto;
    min-width: 600px;
    th, td {
      border: 1px solid #444;
      padding: .6rem;
      text-align: left;
      font-size: .9rem;
      word-break: break-word;
      hyphens: auto;
    }
    thead {
      background: #333;
      color: #fff;
    }
  }
  .loading-logs {
    color: #bbb;
    font-style: italic;
    text-align: center;
    padding: 1rem 0;
  }
  .no-logs {
    color: #bbb;
    text-align: center;
    padding: .5rem 0;
    font-style: italic;
  }
  .pagination-controls {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: .5rem;
    button {
      padding: .5rem 1rem;
      background: #007bff;
      color: #fff;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      &:disabled {
        background: #ccc;
        color: #666;
        cursor: not-allowed;
      }
    }
    span {
      color: #eee;
      font-size: .9rem;
      align-self: center;
    }
  }
}
/* ===== Visits ===== */
.visits-section {
  h2 {
    margin-bottom: 1rem;
  }
  .date-picker {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem;
    margin-bottom: 1rem;
    label {
      align-self: center;
    }
    input, .refresh-button {
      flex: 1 1 120px;
      padding: .5rem;
      border: 1px solid #444;
      border-radius: 4px;
      background: #1e222b;
      color: #fff;
    }
    .refresh-button {
      background: #007bff;
      cursor: pointer;
    }
  }
  .loading-visits {
    color: #bbb;
    font-style: italic;
  }
  .chart-wrapper {
    overflow-x: auto;
    margin-bottom: 1rem;
  }
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
    background: #2196F3;
    position: relative;
    display: flex;
    flex-direction: column-reverse;
    align-items: center;
  }
  .bar-value {
    color: #fff;
    font-size: 12px;
    padding: 2px;
  }
  .bar-label {
    position: absolute;
    bottom: -18px;
    font-size: 12px;
    color: #ccc;
  }
  .no-data {
    color: #bbb;
    font-style: italic;
    text-align: center;
    padding: 1rem 0;
  }
}
/* ===== Users ===== */
.users-section {
  table {
    width: 100%;
    border-collapse: collapse;
    display: block;
    overflow-x: auto;
    min-width: 600px;
    margin-bottom: 1rem;
    th, td {
      border: 1px solid #444;
      padding: .6rem;
      text-align: left;
      font-size: .9rem;
      word-break: break-word;
      hyphens: auto;
    }
    thead {
      background: #333;
      color: #fff;
    }
  }
}
/* ===== Settings ===== */
.settings-section {
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
    th, td {
      border: 1px solid #444;
      padding: .6rem;
      text-align: left;
      font-size: .9rem;
      word-break: break-word;
      hyphens: auto;
    }
    thead {
      background: #333;
      color: #fff;
    }
  }
  .btn-save-all {
    padding: .75rem 1.5rem;
    background: #007bff;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    &:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
  }
  .add-setting {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem;
    margin-top: 1rem;
    input {
      flex: 1 1 200px;
      padding: .5rem;
      border: 1px solid #444;
      border-radius: 4px;
      background: #1e222b;
      color: #fff;
    }
    button {
      padding: .5rem 1rem;
      background: #007bff;
      color: #fff;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    .delete-icon {
      background: none;
      border: none;
      font-size: 1.1rem;
      color: #e94f37;
      cursor: pointer;
      &:disabled {
        color: #666;
        cursor: not-allowed;
      }
    }
  }
  table .delete-icon {
    background: none;
    border: none;
    font-size: 1.1rem;
    color: #e94f37;
    cursor: pointer;
    &:disabled {
      color: #666;
      cursor: not-allowed;
    }
  }
}
/* ===== All Reviews ===== */
.all-reviews-section {
  ul {
    list-style: none;
    padding: 0;
  }
  .admin-review {
    background: #252a3b;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    .review-header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      margin-bottom: .5rem;
      .review-date {
        color: #aaa;
        font-size: .9rem;
      }
    }
    p {
      margin: .3rem 0;
      color: #ddd;
    }
    .photos {
      display: flex;
      flex-wrap: wrap;
      gap: .5rem;
      margin: .5rem 0;
    }
    .admin-photo {
      width: 80px;
      height: 80px;
      object-fit: cover;
      border-radius: 4px;
    }
    .review-link a {
      color: #4caf50;
      text-decoration: none;
    }
    .delete-btn {
      margin-top: .5rem;
      padding: .5rem 1rem;
      background: #e94f37;
      color: #fff;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
  }
}
/* ===== Add Review ===== */
.add-review-section {
  form {
    display: grid;
    gap: 1rem;
    max-width: 400px;
    input, textarea {
      width: 100%;
      padding: .5rem;
      border: 1px solid #444;
      border-radius: 4px;
      background: #1e222b;
      color: #fff;
    }
    .photos-inputs input {
      margin-top: .5rem;
    }
    button {
      padding: .75rem 1.5rem;
      background: #007bff;
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }
    .error {
      color: #e94f37;
    }
    .success {
      color: #4caf50;
    }
  }
}
/* ===== Requests ===== */
.requests-section {
  .requests-list {
    list-style: none;
    padding: 0;
    .request-item {
      background: #252a3b;
      padding: 1rem;
      border-radius: 6px;
      margin-bottom: 1rem;
      .request-header {
        display: flex;
        flex-wrap: wrap;
        gap: .5rem;
        margin-bottom: .5rem;
        .date {
          margin-left: auto;
          color: #aaa;
        }
      }
      p {
        margin: .3rem 0;
        color: #ddd;
        word-break: break-word;
        hyphens: auto;
      }
      a {
        color: #4caf50;
        text-decoration: none;
        margin-right: 1rem;
      }
      button {
        padding: .5rem 1rem;
        background: #e94f37;
        color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      }
    }
  }
}
/* ===== Responsive Enhancements ===== */
@media (max-width: 600px) {
  .combined-preview,
  .sheet-preview-block,
  .zip-preview-block,
  .pagination-controls,
  .date-picker {
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
  }
  .zip-input-block,
  .preview-result,
  .combined-preview button,
  .pagination-controls button,
  .date-picker input,
  .date-picker .refresh-button {
    flex: 1 1 100% !important;
    width: 100% !important;
    box-sizing: border-box;
    margin-bottom: .75rem;
  }
  .sheet-preview-block .preview-result,
  .zip-preview-block .preview-result {
    max-width: 100%;
    margin-bottom: 1rem;
  }
  .logs-section .logs-table,
  .users-section table,
  .settings-section table {
    display: block;
    overflow-x: auto;
    min-width: 100%;
  }
  .bar-chart {
    height: 150px !important;
  }
  .admin-review {
    padding: .75rem !important;
  }
  .admin-review .review-header {
    display: flex !important;
    flex-direction: column !important;
    gap: .25rem !important;
  }
  .photos {
    justify-content: flex-start !important;
    flex-wrap: wrap;
  }
  .admin-photo {
    width: 60px !important;
    height: 60px !important;
  }
  .tabs button {
    flex: 1 1 45% !important;
    font-size: .8rem !important;
    padding: .5rem .75rem !important;
  }
  .add-review-section form {
    max-width: 100% !important;
  }
  .requests-section .request-item {
    padding: .75rem !important;
  }
}

</style>
