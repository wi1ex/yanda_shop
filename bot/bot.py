from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp
import asyncio
import logging
import os

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.send_message(os.getenv('ADMIN_ID'), "Приложение запущено!")
    await dp.start_polling(bot)

@dp.message.register(Command("upload"))
async def cmd_upload(message: types.Message):
    await message.reply("Ответом на это сообщение отправьте CSV + в тексте укажите тип:\n"
                        "`shoe`, `clothing` или `accessory`", parse_mode="Markdown")

@dp.message.register(content_types=types.ContentType.DOCUMENT)
async def handle_csv(message: types.Message):
    # получаем строку-тип из reply_to
    if not message.reply_to_message or not message.reply_to_message.text:
        return await message.reply("Сначала дайте команду /upload и ответьте на неё CSV.")
    typ = message.reply_to_message.text.strip().lower()
    if typ not in ("shoe","clothing","accessory"):
        return await message.reply("Неверный тип, должен быть shoe, clothing или accessory.")

    # скачиваем файл
    file = await bot.get_file(message.document.file_id)
    buf  = await bot.download_file(file.file_path)

    data = aiohttp.FormData()
    data.add_field("type", typ)
    data.add_field("file", buf, filename=message.document.file_name, content_type="text/csv")

    async with aiohttp.ClientSession() as sess:
        async with sess.post("https://shop.yanda.twc1.net/api/import_products", data=data) as resp:
            if resp.status == 201:
                await message.reply("✅ Импорт выполнен успешно.")
            else:
                text = await resp.text()
                await message.reply(f"❌ Ошибка {resp.status}: {text}")

if __name__ == "__main__":
    asyncio.run(main())
