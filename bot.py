import asyncio
import logging
import os
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Создаём объекты бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Настраиваем клавиатуру меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Анализ задачи")],
        [KeyboardButton(text="Создать WARNORD")],
        [KeyboardButton(text="Погода")],
    ],
    resize_keyboard=True
)

# Устанавливаем API-ключ OpenAI
openai.api_key = OPENAI_API_KEY

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)

@dp.message(lambda message: message.text == "Анализ задачи")
async def request_task(message: types.Message):
    await message.answer("Отправь текст задачи для анализа:")

@dp.message(lambda message: message.text and message.text != "Анализ задачи")
async def process_task(message: types.Message):
    task_text = message.text

    try:
        # Запрос к OpenAI для анализа по 5W
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты военный аналитик. Анализируй задачу по 5W (Who, What, Where, When, Why) в стиле военного приказа."},
                {"role": "user", "content": task_text}
            ]
        )
        order = response["choices"][0]["message"]["content"]

        # Запрос к OpenAI для разведданных и рекомендаций
        intel_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты военный стратег. Дай разведданные и рекомендации по выполнению задачи."},
                {"role": "user", "content": task_text}
            ]
        )
        intel = intel_response["choices"][0]["message"]["content"]

        await message.answer(f"📜 **Боевой приказ:**\n\n{order}")
        await message.answer(f"🔍 **Разведданные и рекомендации:**\n\n{intel}")

    except Exception as e:
        logging.error(f"Ошибка при вызове OpenAI API: {e}")
        await message.answer("Произошла ошибка при анализе задачи.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))