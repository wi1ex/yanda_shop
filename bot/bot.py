import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация бота и диспетчера ---
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp  = Dispatcher()

# --- Команда /upload ---
@dp.message(Command("upload"))
async def cmd_upload(message: types.Message):
    await message.reply("📤 Ответом на это сообщение пришлите CSV-файл и укажите в тексте тип:\n"
                        "`shoe`, `clothing` или `accessory`", parse_mode="Markdown")

# --- Обработчик документа ---
@dp.message(content_types=types.ContentType.DOCUMENT)
async def handle_csv(message: types.Message):
    # Проверяем, что это reply на /upload
    reply = message.reply_to_message
    if not reply or not reply.text:
        return await message.reply("❗ Сначала выполните команду /upload и ответьте на неё CSV.")

    typ = reply.text.strip().lower()
    if typ not in ("shoe", "clothing", "accessory"):
        return await message.reply("❗ Неверный тип — должно быть: shoe, clothing или accessory.")

    # Скачиваем файл и готовим форму
    file = await bot.get_file(message.document.file_id)
    buf  = await bot.download_file(file.file_path)

    data = aiohttp.FormData()
    data.add_field("type", typ)
    data.add_field("file", buf, filename=message.document.file_name, content_type="text/csv")

    # Адрес вашего бэкенда (можно вынести в BACKEND_URL)
    backend = os.getenv("BACKEND_URL", "https://shop.yanda.twc1.net")
    url = f"{backend}/api/import_products"

    # Отправляем на бэкенд
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as resp:
            if resp.status == 201:
                await message.reply("✅ Импорт выполнен успешно.")
            else:
                text = await resp.text()
                await message.reply(f"❌ Ошибка {resp.status}: {text}")

# --- Точка входа ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.send_message(os.getenv('ADMIN_ID'), "Приложение запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
