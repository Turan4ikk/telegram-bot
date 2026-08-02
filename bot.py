import asyncio
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8623221406:AAF42kKkHeHWABjs0eUBAdhs1rlZ6EBQgCg"

app = Flask('')
@app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ============ БОТ ============
bot = Bot(token=TOKEN)
dp = Dispatcher()  # ← УБРАЛИ bot ВНУТРИ!

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Бот работает!")

@dp.message(Command("rules"))
async def rules(message: types.Message):
    await message.answer("📋 Правила клуба...")

@dp.message(Command("mute"))
async def mute(message: types.Message):
    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение пользователя!")
        return
    user = message.reply_to_message.from_user
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /mute 5m Спам")
        return
    await message.answer(f"🔇 {user.first_name} замучен!")

@dp.message(Command("ban"))
async def ban(message: types.Message):
    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение пользователя!")
        return
    user = message.reply_to_message.from_user
    await message.answer(f"🚫 {user.first_name} забанен!")

@dp.message(Command("warn"))
async def warn(message: types.Message):
    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение пользователя!")
        return
    user = message.reply_to_message.from_user
    await message.answer(f"⚠️ {user.first_name} получил предупреждение!")

async def main():
    print("🚀 БОТ ЗАПУЩЕН!")
    await dp.start_polling(bot)  # ← bot ПЕРЕДАЁТСЯ СЮДА

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(main())
