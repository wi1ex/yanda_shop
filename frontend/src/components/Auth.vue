<template>
  <transition name="fade">
    <div class="auth-modal-backdrop" @click.self="onClose" v-if="store.userStore.showAuth">
      <button class="close-btn" @click="onClose">
        <img :src="icon_close" alt="Закрыть" />
      </button>
      <div class="auth-modal">
        <h2 v-if="mode === 'register'">Регистрация</h2>
        <h2 v-else>Вход</h2>

        <div v-if="step === 1">
          <div v-if="mode === 'register'">
            <input v-model="form.first_name"  placeholder="Имя" />
            <input v-model="form.last_name"   placeholder="Фамилия" />
            <input v-model="form.email"       placeholder="E-mail" />
            <button @click="sendRegisterCode">Получить код</button>
          </div>
          <div v-else>
            <input v-model="form.email" placeholder="E-mail" />
            <button @click="sendLoginCode">Получить код</button>
          </div>
        </div>

        <div v-else-if="step === 2">
          <input v-model="form.code" placeholder="Код из письма" />
          <button v-if="mode === 'register'" @click="verifyRegisterCode">Подтвердить регистрацию</button>
          <button v-else @click="verifyLoginCode">Войти</button>
        </div>

        <p class="error" v-if="error">{{ error }}</p>

        <div class="switch-mode">
          <span v-if="mode === 'register'">Уже есть аккаунт?</span>
          <span v-else>Нет аккаунта?</span>
          <button @click="toggleMode">
            {{ mode === 'register' ? 'Войти' : 'Зарегистрироваться' }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '@/store/index.js'

import icon_close from "@/assets/images/close.svg";

const store = useStore()

const step  = ref(1)
const error = ref('')
const mode  = ref('register')
const form  = ref({ email: '', first_name: '', last_name: '', code: '' })

function onClose() {
  store.userStore.closeAuth()
  reset()
}

function toggleMode() {
  mode.value = mode.value === 'register' ? 'login' : 'register'
  reset()
}

function reset() {
  step.value = 1
  form.value = { email: '', first_name: '', last_name: '', code: '' }
  error.value = ''
}

async function sendRegisterCode() {
  error.value = ''
  try {
    await store.userStore.requestRegistrationCode(
      form.value.email,
      form.value.first_name,
      form.value.last_name
    )
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка отправки кода'
  }
}

async function verifyRegisterCode() {
  error.value = ''
  try {
    await store.userStore.verifyRegistrationCode(form.value.email, form.value.code)
    await onSuccess()
  } catch (e) {
    error.value = e.response?.data?.error || 'Неверный код'
  }
}

async function sendLoginCode() {
  error.value = ''
  try {
    await store.userStore.requestLoginCode(form.value.email)
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка отправки кода'
  }
}

async function verifyLoginCode() {
  error.value = ''
  try {
    await store.userStore.verifyLoginCode(form.value.email, form.value.code)
    await onSuccess()
  } catch (e) {
    error.value = e.response?.data?.error || 'Неверный код'
  }
}

async function onSuccess() {
  // после успешной авторизации
  store.userStore.closeAuth()
  localStorage.removeItem('visitorId')
}

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
    input {
      width: 100%;
      margin: 8px 0;
      padding: 8px;
      box-sizing: border-box;
    }
    button {
      width: 100%;
      padding: 10px;
      margin-top: 12px;
      cursor: pointer;
    }
    .error {
      color: red;
      margin-top: 8px;
      text-align: center;
    }
    .switch-mode {
      text-align: center;
      margin-top: 12px;
      button {
        background: none;
        border: none;
        color: #007bff;
        cursor: pointer;
      }
    }
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>
