import os
import re
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация бота и диспетчера ---
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Получаем ID администратора из переменных окружения
ADMIN_ID = int(os.getenv('ADMIN_ID'))


# --- Команда /upload ---
@dp.message(Command("upload"))
async def cmd_upload(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        # Сохраняем ID сообщения для последующей проверки
        await message.reply("📤 Пришлите мне CSV-файл и укажите в подписи к файлу тип:\n"
                            "`shoe`, `clothing` или `accessory`\n\nПример: `accessory`",
                            parse_mode=ParseMode.MARKDOWN)


# --- Обработчик документа ---
@dp.message(F.document)
async def handle_csv(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        # Проверяем, что это ответ на сообщение с командой /upload
        if not message.reply_to_message or not message.reply_to_message.text:
            return await message.reply("❗ Сначала выполните команду /upload!")

        # Извлекаем тип из подписи к файлу (message.caption)
        user_input = (message.caption or "").strip().lower()

        # Ищем совпадение с допустимыми типами
        match = re.search(r'\b(shoe|clothing|accessory)\b', user_input)
        if not match:
            return await message.reply("❗ Неверно указан тип. В подписи к файлу должно быть одно из: \n"
                                       "`shoe`, `clothing` или `accessory`\n\nВы указали: {user_input or 'пусто'}",
                                       parse_mode=ParseMode.MARKDOWN)
        actual_type = match.group(1)

        # Скачиваем файл
        file = await bot.get_file(message.document.file_id)
        buf = await bot.download_file(file.file_path)

        # Формируем запрос
        data = aiohttp.FormData()
        data.add_field("type", actual_type)
        data.add_field("file", buf, filename=message.document.file_name or "products.csv", content_type="text/csv")

        # Адрес бэкенда
        url = f'{os.getenv("BACKEND_URL")}/api/import_products'

        # Отправляем на бэкенд
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as resp:
                    if resp.status == 201:
                        await message.reply("✅ Импорт выполнен успешно!")
                    else:
                        text = await resp.text()
                        logger.error(f"Backend error {resp.status}: {text}")
                        await message.reply(f"❌ Ошибка {resp.status}: {text[:300]}")
        except Exception as e:
            logger.exception("Connection error")
            await message.reply(f"🚫 Ошибка соединения: {str(e)}")


# --- Точка входа ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.send_message(ADMIN_ID, "Приложение запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
