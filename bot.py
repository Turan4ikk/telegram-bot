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

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Бот работает! Привет!")

@dp.message(Command("rules"))
async def rules(message: types.Message):
    await message.answer("📋 Правила клуба...")

async def main():
    print("🚀 БОТ ЗАПУЩЕН!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(main())
