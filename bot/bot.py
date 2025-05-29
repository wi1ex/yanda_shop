import os
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


# --- Команда /upload ---
@dp.message(Command("upload"))
async def cmd_upload(message: types.Message):
    await message.reply(
        "📤 Ответом на это сообщение пришлите CSV-файл и укажите в тексте тип:\n"
        "`shoe`, `clothing` или `accessory`",
        parse_mode=ParseMode.MARKDOWN
    )


# --- Обработчик документа ---
@dp.message(F.document)  # Новый стиль фильтрации
async def handle_csv(message: types.Message):
    # Проверяем, что это reply на /upload
    reply = message.reply_to_message
    if not reply or not reply.text:
        return await message.reply("❗ Сначала выполните команду /upload и ответьте на неё CSV.")

    # Извлекаем тип из оригинального сообщения
    typ = reply.text.split('\n', 1)[0].strip().lower()
    valid_types = ("shoe", "clothing", "accessory")

    if not any(t in typ for t in valid_types):
        return await message.reply("❗ Неверный тип — должно быть: shoe, clothing или accessory.")

    # Определяем фактический тип
    actual_type = next((t for t in valid_types if t in typ), None)
    if not actual_type:
        return await message.reply("❌ Не удалось определить тип товара")

    # Скачиваем файл
    file = await bot.get_file(message.document.file_id)
    buf = await bot.download_file(file.file_path)

    # Формируем запрос
    data = aiohttp.FormData()
    data.add_field("type", actual_type)
    data.add_field("file",
                   buf,
                   filename=message.document.file_name or "products.csv",
                   content_type="text/csv")

    # Адрес бэкенда
    url = f'{os.getenv("BACKEND_URL")}/api/import_products'

    # Отправляем на бэкенд
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                if resp.status == 201:
                    await message.reply("✅ Импорт выполнен успешно.")
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
    await bot.send_message(os.getenv('ADMIN_ID'), "Приложение запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())