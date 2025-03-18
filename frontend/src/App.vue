<template>
    <div v-if="!showForm">
        <h1>
          Тестовое приложение
        </h1>
        <button class="btn" @click="toggleForm">
          Тест отправки данных
        </button>
    </div>

    <form v-else>
        <input type="text" placeholder="Введите заголовок" class="title-inp">
        <input type="text" placeholder="Введите описание" class="desc-inp">
        <input type="text" placeholder="Введите текст" class="text-inp">
        <button class="btn" @click.prevent="sendData">
          Отправить
        </button>
    </form>
</template>



<script setup>
import {onMounted, ref} from 'vue';

let tg = window.Telegram.WebApp;
const showForm = ref(false);

const toggleForm = () => {
    showForm.value = !showForm.value;
};

const sendData = () => {
    const data = {
        title: document.querySelector(".title-inp").value,
        desc: document.querySelector(".desc-inp").value,
        text: document.querySelector(".text-inp").value
    };
    tg.sendData(JSON.stringify(data));
};

onMounted(() => {
    let user = tg.initDataUnsafe.user;
    if (user) {
        fetch("/save_user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id: user.id,
                first_name: user.first_name,
                last_name: user.last_name,
                username: user.username
            })
        })
        .then(response => response.json())
        .then(data => console.log("Ответ сервера:", data));
    }
});
</script>



<style>
body {
    color: var(--tg-theme-text-color);
    background: var(--tg-theme-bg-color);
}
.btn {
    background: var(--tg-theme-button-color);
    color: var(--tg-theme-button-text-color);
}
</style>
