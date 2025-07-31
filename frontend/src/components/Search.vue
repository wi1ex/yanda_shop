<template>
  <transition name="fade">
    <section class="request-form" v-if="store.globalStore.showSearch">
      <form @submit.prevent="onSubmitRequest">
        <div class="request-div">
          <button type="button" class="close-btn" @click="toggleSearchClose()">
            <img :src="icon_close_white" alt="Закрыть" />
          </button>
          <h2>Не нашел что хотел?</h2>
          <p style="margin-bottom: 24px;">Загрузи изображение или добавь артикул товара, и мы выкупим это из официального магазина.</p>
          <input class="input-field" type="text" v-model="request.name" placeholder="Имя *" required/>
          <input class="input-field" type="email" v-model="request.email" placeholder="Почта *" required/>
          <input class="input-field" type="text" v-model="request.sku" placeholder="Артикул товара"/>
          <p>или</p>
          <label class="file-upload">
            <input type="file" @change="onFileChange" hidden />
            <div class="file-div">
              <div class="file-div-button">
                <img :src="icon_paper_clip" alt="paper clip" />
                <span class="file-text">{{ uploadedFileName || 'Приложи файл' }}</span>
              </div>
              <span class="file-size">макс. 10 MB</span>
            </div>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="request.agree"/>
            <span>Я согласен на <u>обработку персональных данных</u></span>
          </label>
        </div>
        <button type="submit" class="btn-submit">Отправить запрос</button>
      </form>
    </section>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '@/store'
import icon_paper_clip from "@/assets/images/paper_clip.svg";
import icon_close_white from "@/assets/images/close_white.svg";

const store = useStore()
const uploadedFileName = ref('')
const request = ref({ name:'', email:'', sku:'', file:null, agree:false })

function toggleSearchClose() {
  store.globalStore.showSearch = false
}

function onFileChange(e) {
  const file = e.target.files[0];
  if (file) {
    request.value.file = file
    uploadedFileName.value = file.name;
  } else {
    uploadedFileName.value = '';
  }
}

function onSubmitRequest() {
  if (!request.value.agree) {
    alert("Нужно согласиться с обработкой данных")
    return
  }
  const file = request.value.file
  if (file && file.size > 10 * 1024 * 1024) {
    alert("Файл не должен быть больше 10 МБ")
    return
  }

  const fd = new FormData()
  fd.append("name",  request.value.name)
  fd.append("email", request.value.email)
  fd.append("sku",   request.value.sku)
  if (file) fd.append("file", file)

  store.globalStore.createRequest(fd)
    .then(() => {
      alert("Запрос успешно отправлен")
      // сброс формы
      request.value = { name:'', email:'', sku:'', file:null, agree:false }
      uploadedFileName.value = ''
    })
    .catch(err => {
      alert(err.response?.data?.error || err.message)
    })
}

</script>

<style scoped lang="scss">
.request-form {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  position: fixed;
  inset: 0;
  padding: 0 10px;
  background-color: $black-25;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 2000;
  form {
    display: flex;
    flex-direction: column;
    .request-div {
      display: flex;
      flex-direction: column;
      padding: 24px 10px;
      border-radius: 4px;
      background-color: $black-100;
      .close-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        align-self: flex-end;
        margin-bottom: 24px;
        width: 24px;
        height: 24px;
        border: none;
        background: none;
        cursor: pointer;
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }
      h2 {
        margin: 0 0 16px;
        text-align: center;
        color: $grey-95;
        font-family: Bounded;
        font-weight: 500;
        font-size: 24px;
        line-height: 90%;
        letter-spacing: -0.72px;
      }
      p {
        margin: 0 0 16px;
        text-align: center;
        color: $grey-90;
        font-size: 15px;
        line-height: 110%;
        letter-spacing: -0.6px;
      }
      .input-field {
        margin-bottom: 15px;
        padding: 21px 10px 8px;
        border: none;
        background-color: transparent;
        outline: none;
        border-bottom: 1px solid $white-60;
        color: $white-100;
        font-size: 15px;
        line-height: 100%;
        letter-spacing: -0.6px;
        &::placeholder {
          color: $white-40;
        }
      }
      .file-upload {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 10px;
        border: 1px solid $white-40;
        border-radius: 4px;
        background-color: transparent;
        cursor: pointer;
        .file-div {
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: 100%;
          .file-div-button {
            display: flex;
            align-items: center;
            width: calc(100% - 62px);
            gap: 8px;
            img {
              width: 24px;
              height: 24px;
              object-fit: cover;
            }
            .file-text {
              width: calc(100% - 40px);
              color: $white-60;
              font-family: Bounded;
              font-size: 18px;
              font-weight: 250;
              line-height: 100%;
              letter-spacing: -0.9px;
              overflow: hidden;
              white-space: nowrap;
              text-overflow: ellipsis;
            }
          }
          .file-size {
            color: $white-40;
            font-size: 12px;
            line-height: 100%;
            letter-spacing: -0.48px;
          }
        }
      }
      .checkbox-label {
        display: flex;
        align-items: center;
        margin-top: 24px;
        gap: 5px;
        color: $white-60;
        font-size: 16px;
        line-height: 100%;
        letter-spacing: -0.64px;
        cursor: pointer;
        input[type="checkbox"] {
          appearance: none;
          margin: 0;
          width: 20px;
          height: 20px;
          border: 1px solid $white-40;
          background-color: transparent;
          border-radius: 2px;
          cursor: pointer;
          position: relative;
        }
        input[type="checkbox"]:checked::after {
          content: "";
          position: absolute;
          top: 0;
          left: 5px;
          width: 6px;
          height: 10px;
          border: solid $white-100;
          border-width: 0 2px 2px 0;
          transform: rotate(45deg);
        }
        u {
          text-decoration: underline;
        }
      }
    }
    .btn-submit {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 24px;
      width: 100%;
      height: 56px;
      border: none;
      background-color: $white-80;
      color: $black-100;
      border-radius: 4px;
      font-size: 16px;
      line-height: 100%;
      letter-spacing: -0.64px;
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
