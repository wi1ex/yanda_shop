import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_admin_message():
    await bot.send_message(ADMIN_ID, "Кто-то открыл приложение!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await send_admin_message()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
