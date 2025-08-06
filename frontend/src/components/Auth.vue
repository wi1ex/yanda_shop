<template>
  <transition name="fade">
    <div class="auth-modal-backdrop" @click.self="onClose" v-if="store.userStore.showAuth">
      <button class="close-btn" @click="onClose">
        <img :src="icon_close" alt="Закрыть" />
      </button>
      <div class="auth-modal" v-if="step === 1">
        <h2>Вход или регистрация</h2>
        <p class="text">Введите почтовый адрес, и мы отправим вам письмо с кодом подтверждения.</p>
        <input v-model="form.email" type="email" placeholder="Введи e-mail"/>
        <p class="error" v-if="error">{{ error }}</p>
        <button @click="sendCode">Получить код</button>
        <p class="info">Нажимая на кнопку «Получить код», я даю согласие на обработку своих персональных данных в соответствии с политикой обработки персональных данных</p>
      </div>
      <div class="auth-modal" v-else-if="step === 2">
        <h2>Подтверди почту</h2>
        <p class="text">{{ form.email }}</p>
        <p class="text">Введи код из сообщения.</p>
        <input v-model="form.code" placeholder="Введи код" />
        <p class="info">
          Не получили код? Обратись в нашу
          <a v-if="store.globalStore.parameters.url_social_email" :href="`mailto:${store.globalStore.parameters.url_social_email}`" rel="noopener">
            службу поддержки
          </a>
        </p>
        <p class="error" v-if="error">{{ error }}</p>
        <button @click="checkCode">Подтвердить номер</button>
        <p class="info">Нажимая на кнопку «Подтвердить номер», я даю согласие на обработку своих персональных данных в соответствии с политикой обработки персональных данных</p>
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
    text-align: center;
    h2 {
      margin: 16px 0;
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
    button {
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
      font-family: Manrope;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
      cursor: pointer;
    }
    .text {
      margin: 0;
      width: 75%;
      color: $grey-20;
      font-family: Manrope;
      font-size: 15px;
      line-height: 110%;
      letter-spacing: -0.6px;
    }
    .info {
      margin: 24px 0;
      color: $black-40;
      font-family: Manrope;
      font-size: 14px;
      font-style: normal;
      font-weight: 500;
      line-height: 100%;
      letter-spacing: -0.56px;
      a {
        color: $black-40;
      }
    }
    .error {
      margin: 0;
      color: $red-error;
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
