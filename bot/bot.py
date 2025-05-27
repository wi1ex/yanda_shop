import os
import asyncio
import logging
from aiogram import Bot, Dispatcher

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.send_message(os.getenv('ADMIN_ID'), "Приложение запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
