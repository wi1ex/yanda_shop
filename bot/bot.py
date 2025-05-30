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

# Получаем значения из переменных окружения
ADMIN_ID = int(os.getenv('ADMIN_ID'))
BACKEND_URL = os.getenv("BACKEND_URL")

@dp.message(Command("upload"))
async def cmd_upload(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("📤 Пришлите *CSV* или *ZIP* без подписи.\n"
                            "- `shoes.csv` → обновит таблицу обуви\n"
                            "- `clothing.csv` → обновит одежду\n"
                            "- `accessories.csv` → обновит аксессуары\n"
                            "- ZIP → загрузит картинки в MinIO", parse_mode=ParseMode.MARKDOWN)


@dp.message(F.document)
async def handle_all(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    fname = message.document.file_name.lower()
    ext = fname.rsplit(".", 1)[-1]

    # скачиваем содержимое
    f = await bot.get_file(message.document.file_id)
    buf = await bot.download_file(f.file_path)
    data = buf.read()

    # собираем форму
    form = aiohttp.FormData()
    form.add_field("file", data, filename=message.document.file_name, content_type="application/octet-stream")

    # определяем куда шлём
    if ext == "csv":
        url = f"{BACKEND_URL}/api/import_products"
    elif ext == "zip":
        url = f"{BACKEND_URL}/api/upload_images"
    else:
        return await message.reply("❗ Поддерживаются только CSV и ZIP.")

    # отправляем
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, data=form) as resp:
                text = await resp.text()
                if resp.status == 201:
                    await message.reply("✅ Успешно!")
                else:
                    logger.error(f"Backend {resp.status}: {text}")
                    await message.reply(f"❌ Ошибка {resp.status}: {text[:200]}")
    except Exception as e:
        logger.exception(e)
        await message.reply(f"🚫 Ошибка соединения: {e}")


# --- Точка входа ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.send_message(ADMIN_ID, "Приложение запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
