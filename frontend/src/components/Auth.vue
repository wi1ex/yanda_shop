<template>
  <transition name="fade">
    <div class="auth-modal-backdrop" @click.self="onClose" v-if="store.userStore.showAuth">
      <button type="button" class="close-btn" @click="onClose">
        <img :src="icon_close" alt="Закрыть" />
      </button>
      <div class="auth-modal" v-if="step === 1">
        <h2>Вход или регистрация</h2>
        <p class="text" style="width: 75%;">Введите почтовый адрес, и мы отправим вам письмо с кодом подтверждения.</p>
        <input v-model.trim="form.email" type="email" placeholder="Введи e-mail" @keyup.enter="sendCode"/>
        <p class="error" v-if="error">{{ error }}</p>
        <button type="button" class="button-code" @click="sendCode" :disabled="pending || !canSendEmail">
          {{ pending ? 'Отправляем…' : 'Получить код' }}
        </button>
        <p class="info">Нажимая на кнопку «Получить код», я даю согласие на обработку своих персональных данных в соответствии с политикой обработки персональных данных</p>
      </div>
      <div class="auth-modal" v-else-if="step === 2">
        <h2>Подтверди почту</h2>
        <p class="text">{{ form.email }}</p>
        <p class="text">Введи код из сообщения.</p>
        <input v-model.trim="form.code" inputmode="numeric" maxlength="6" placeholder="Введи код" @keyup.enter="checkCode" />
        <p class="error" v-if="error">{{ error }}</p>
        <p v-if="remaining > 0" class="text" style="margin-top: 40px;">
          Запросить код повторно можно через 0:{{ ss }} секунд
        </p>
        <button v-else type="button" class="resend-link" @click="resendCode" :disabled="pending">
          Запросить новый код
        </button>
        <p class="info" style="margin-top: 8px;">
          Не получили код? Обратись в нашу
          <a v-if="store.globalStore.parameters.url_social_email" :href="`mailto:${store.globalStore.parameters.url_social_email}`" rel="noopener">
            службу поддержки
          </a>
        </p>
        <button type="button" class="button-code" @click="checkCode" :disabled="pending || !canSubmitCode">
          {{ pending ? 'Проверяем…' : 'Подтвердить почту' }}
        </button>
        <p class="info">Нажимая на кнопку «Подтвердить номер», я даю согласие на обработку своих персональных данных в соответствии с политикой обработки персональных данных</p>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useStore } from '@/store/index.js'
import icon_close from '@/assets/images/close.svg'

const store     = useStore()
const step      = ref(1)
const error     = ref('')
const form      = ref({ email: '', code: '' })
const pending   = ref(false)
const remaining = ref(0)
let timerId     = null


const ss = computed(() => String(remaining.value % 60).padStart(2, '0'))
const canSendEmail  = computed(() => /\S+@\S+\.\S+/.test(form.value.email))
const canSubmitCode = computed(() => /^[0-9]{6}$/.test(form.value.code))

function startTimer(seconds) {
  stopTimer()
  remaining.value = Math.max(0, seconds | 0)
  if (remaining.value <= 0) return
  timerId = setInterval(() => {
    if (remaining.value > 0) remaining.value -= 1
    else stopTimer()
  }, 1000)
}
function stopTimer() {
  if (timerId) { clearInterval(timerId); timerId = null }
}

function reset() {
  step.value = 1
  form.value.email = ''
  form.value.code = ''
  error.value = ''
  pending.value = false
  remaining.value = 0
  stopTimer()
}

function onClose() {
  store.userStore.closeAuth()
  reset()
}

async function sendCode() {
  if (!canSendEmail.value) { error.value = 'Введите корректный e-mail'; return }
  error.value = ''
  pending.value = true
  try {
    await store.userStore.requestCode(form.value.email)
    const seconds = 59
    step.value = 2
    startTimer(seconds)
  } catch (e) {
    error.value = e?.response?.data?.error || 'Ошибка отправки кода'
  } finally {
    pending.value = false
  }
}

async function resendCode() {
  if (remaining.value > 0) return
  error.value = ''
  pending.value = true
  try {
    await store.userStore.requestCode(form.value.email)
    const seconds = 59
    startTimer(seconds)
  } catch (e) {
    error.value = e?.response?.data?.error || 'Не удалось отправить код повторно'
  } finally {
    pending.value = false
  }
}

async function checkCode() {
  if (!canSubmitCode.value) { error.value = 'Введите 6-значный код'; return }
  error.value = ''
  pending.value = true
  try {
    await store.userStore.verifyCode(form.value.email, form.value.code)
    localStorage.removeItem('visitorId')
    onClose()
  } catch (e) {
    error.value = e?.response?.data?.error || 'Неверный или просроченный код'
  } finally {
    pending.value = false
  }
}

onBeforeUnmount(stopTimer)

</script>

<style scoped lang="scss">

.auth-modal-backdrop {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: fixed;
  inset: 0;
  padding: 20px 10px;
  background-color: $white-100;
  z-index: 2000;
  .close-btn {
    display: flex;
    position: absolute;
    top: 20px;
    right: 10px;
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
    img {
      width: 24px;
      height: 24px;
      object-fit: cover;
    }
  }
  .auth-modal {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    text-align: center;
    h2 {
      margin: 0;
      color: $black-100;
      font-family: Bounded;
      font-size: 24px;
      font-style: normal;
      font-weight: 250;
      line-height: 80%;
      letter-spacing: -1.2px;
    }
    input {
      margin: 40px 0 15px;
      padding: 21px 10px 8px;
      text-align: center;
      width: calc(100% - 20px);
      outline: none;
      box-shadow: none;
      border: none;
      border-bottom: 1px solid $grey-20;
      color: $grey-20;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      &::placeholder {
        color: $black-40;
      }
    }
    .button-code {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-top: 40px;
      padding: 0 24px;
      width: 100%;
      height: 56px;
      border: none;
      border-radius: 4px;
      background-color: $grey-20;
      color: $white-100;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      cursor: pointer;
    }
    .email {
      margin: 16px 0 0;
      color: $black-100;
      font-size: 16px;
      line-height: 110%;
      letter-spacing: -0.64px;
    }
    .text {
      margin: 16px 0 0;
      color: $grey-20;
      font-size: 15px;
      line-height: 110%;
      letter-spacing: -0.6px;
    }
    .info {
      margin: 24px 0 0;
      color: $black-40;
      font-size: 14px;
      line-height: 100%;
      letter-spacing: -0.56px;
      a {
        color: $black-40;
      }
    }
    .error {
      margin: 0;
      color: $red-error;
      font-size: 14px;
      line-height: 100%;
      letter-spacing: -0.56px;
    }
    .resend-link {
      margin: 40px 0 0;
      padding: 0;
      border: none;
      background: none;
      color: $black-100;
      font-size: 15px;
      line-height: 110%;
      letter-spacing: -0.6px;
      cursor: pointer;
    }
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease-in-out;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

</style>
