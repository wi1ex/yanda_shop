import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_admin_message():
    try:
        await bot.send_message(ADMIN_ID, "Кто-то открыл приложение!")
    except Exception as e:
        logging.error(f"Ошибка отправки: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.send_message(ADMIN_ID, "Приложение запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
