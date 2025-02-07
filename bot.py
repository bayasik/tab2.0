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

@dp.message(lambda message: message.text == "Создать WARNORD")
async def request_task(message: types.Message):
    await message.answer("Отправь текст боевой задачи, и я сформирую WARNORD.")

@dp.message(lambda message: message.text and message.text != "Создать WARNORD")
async def process_task(message: types.Message):
    task_text = message.text

    try:
        # Параграф 1: Ситуация (METT-TC, OCOKA, ASCOPE, погода)
        response_situation = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты военный аналитик. Проведи анализ METT-TC, OCOKA, ASCOPE и погоды для боевой задачи."},
                {"role": "user", "content": task_text}
            ]
        )
        situation = response_situation["choices"][0]["message"]["content"]

        # Параграф 2: Задание (5W)
        response_task = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты военный офицер. Сформулируй боевое задание по принципу 5W."},
                {"role": "user", "content": task_text}
            ]
        )
        task = response_task["choices"][0]["message"]["content"]

        # Параграф 3: Выполнение
        response_execution = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты военный стратег. Составь детальный план выполнения операции, разделив его на фазы."},
                {"role": "user", "content": task_text}
            ]
        )
        execution = response_execution["choices"][0]["message"]["content"]

        # Параграф 4: Логистика
        response_logistics = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты военный офицер снабжения. Опиши логистическое обеспечение операции."},
                {"role": "user", "content": task_text}
            ]
        )
        logistics = response_logistics["choices"][0]["message"]["content"]

        # Параграф 5: Командование и связь
        response_command = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты военный офицер связи. Опиши структуру командования и систему связи."},
                {"role": "user", "content": task_text}
            ]
        )
        command = response_command["choices"][0]["message"]["content"]

        # Отправка результатов
        await message.answer(f"📋 **WARNORD: Боевой приказ**")
        await message.answer(f"📌 **1. СИТУАЦИЯ:**\n\n{situation}")
        await message.answer(f"📌 **2. ЗАДАНИЕ:**\n\n{task}")
        await message.answer(f"📌 **3. ВЫПОЛНЕНИЕ:**\n\n{execution}")
        await message.answer(f"📌 **4. ЛОГИСТИКА:**\n\n{logistics}")
        await message.answer(f"📌 **5. КОМАНДОВАНИЕ И СВЯЗЬ:**\n\n{command}")

    except Exception as e:
        logging.error(f"Ошибка при вызове OpenAI API: {e}")
        await message.answer("Произошла ошибка при генерации WARNORD.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))