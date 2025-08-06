<template>
  <transition name="fade">
    <div class="auth-modal-backdrop" @click.self="onClose" v-if="store.userStore.showAuth">
      <button class="close-btn" @click="onClose">
        <img :src="icon_close" alt="Закрыть" />
      </button>

      <div class="auth-modal">
        <h2>Авторизация</h2>

        <div v-if="step === 1">
          <input v-model="form.email" type="email" placeholder="E-mail"/>
          <button @click="sendCode">Получить код</button>
        </div>

        <div v-else-if="step === 2">
          <input v-model="form.code" placeholder="Код из письма" />
          <button @click="checkCode">Подтвердить</button>
        </div>

        <p v-if="error">{{ error }}</p>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '@/store/index.js'
import icon_close from '@/assets/images/close.svg'

const store = useStore()
const step  = ref(1)
const error = ref('')
const form  = ref({ email: '', code: '' })

function reset() {
  step.value = 1
  form.value.email = ''
  form.value.code = ''
  error.value = ''
}

function onClose() {
  store.userStore.closeAuth()
  reset()
}

async function sendCode() {
  error.value = ''
  try {
    await store.userStore.requestCode(form.value.email)
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка отправки кода'
  }
}

async function checkCode() {
  error.value = ''
  try {
    await store.userStore.verifyCode(form.value.email, form.value.code)
    store.userStore.closeAuth()
    localStorage.removeItem('visitorId')
  } catch (e) {
    error.value = e.response?.data?.error || 'Неверный код'
  }
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
    h2 {
      color: grey;
      margin-top: 8px;
      text-align: center;
    }
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
    p {
      color: red;
      margin-top: 8px;
      text-align: center;
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
