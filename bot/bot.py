import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация бота и диспетчера ---
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Получаем значения из переменных окружения
ADMIN_ID = int(os.getenv('ADMIN_ID'))


@dp.message(Command("start"))
async def cmd_upload(message: types.Message):
    await message.reply('🛍 YANDA Shop — ваш персональный доступ к брендам!\n'
                        'Выкупаем любую вещь для вас из официального магазина!\n\n'
                        '✔️ Гарантия оригинальности\n'
                        '✉️ Работаем по вашему запросу')


# --- Точка входа ---
async def main():
    await bot.send_message(ADMIN_ID, "Приложение запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
