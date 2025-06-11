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

# # Получаем значения из переменных окружения
# ADMIN_ID = int(os.getenv('ADMIN_ID'))
# BACKEND_URL = os.getenv("BACKEND_URL")


@dp.message(Command("start"))
async def cmd_upload(message: types.Message):
    await message.reply('''
    🛍 YANDA Shop — ваш персональный доступ к брендам!
    Выкупаем любую вещь для вас из официального магазина! 
    
    ✔️ Гарантия оригинальности
    ✉️ Работаем по вашему запросу''')


# @dp.message(Command("upload"))
# async def cmd_upload(message: types.Message):
#     if message.from_user.id == ADMIN_ID:
#         await message.reply("📤 Пришлите *CSV* или *ZIP* файл\n"
#                             "- `shoes.csv` → обновит таблицу обуви\n"
#                             "- `clothing.csv` → обновит таблицу одежды\n"
#                             "- `accessories.csv` → обновит таблицу аксессуаров\n"
#                             "- `images.zip` → обновит хранилище изображений", parse_mode=ParseMode.MARKDOWN)
#
#
# @dp.message(F.document)
# async def handle_all(message: types.Message):
#     if message.from_user.id != ADMIN_ID:
#         return
#
#     fname = message.document.file_name.lower()
#     ext = fname.rsplit(".", 1)[-1]
#
#     # скачиваем содержимое
#     f = await bot.get_file(message.document.file_id)
#     buf = await bot.download_file(f.file_path)
#     data = buf.read()
#
#     # собираем форму
#     form = aiohttp.FormData()
#     form.add_field("file", data, filename=message.document.file_name, content_type="application/octet-stream")
#
#     # определяем куда шлём
#     if ext == "csv":
#         url = f"{BACKEND_URL}/api/import_products"
#     elif ext == "zip":
#         url = f"{BACKEND_URL}/api/upload_images"
#     else:
#         return await message.reply("❗ Поддерживаются только CSV и ZIP.")
#
#     # отправляем
#     try:
#         async with aiohttp.ClientSession() as sess:
#             async with sess.post(url, data=form) as resp:
#                 try:
#                     data = await resp.json()
#                 except Exception:
#                     data = None
#
#                 if resp.status == 201 and isinstance(data, dict):
#                     # отчёт CSV-импорта
#                     if "added" in data and "updated" in data:
#                         await message.reply(f"✅ Товары обработаны:\n"
#                                             f"Добавлено: {data['added']}\n"
#                                             f"Обновлено: {data['updated']}")
#                     # отчёт ZIP-импорта
#                     elif {"added", "replaced", "deleted"} <= data.keys():
#                         await message.reply(f"✅ Изображения обработаны:\n"
#                                             f"Добавлено: {data['added']}\n"
#                                             f"Заменено: {data['replaced']}\n"
#                                             f"Удалено: {data['deleted']}")
#                     else:
#                         await message.reply("✅ Успешно!")
#                 else:
#                     text = data or await resp.text()
#                     logger.error(f"Backend {resp.status}: {text}")
#                     await message.reply(f"❌ Ошибка {resp.status}: {str(text)[:200]}")
#     except Exception as e:
#         logger.exception(e)
#         await message.reply(f"🚫 Ошибка соединения: {e}")


# --- Точка входа ---
async def main():
    # await bot.send_message(ADMIN_ID, "Приложение запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
