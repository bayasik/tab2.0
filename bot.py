import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import openai
import json
from datetime import datetime

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токены
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

openai.api_key = OPENAI_API_KEY

# Создаем клавиатуру
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Анализ задачи")],
        [KeyboardButton(text="Создать WARNORD")],
        [KeyboardButton(text="Погода")],
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)

# Функция анализа задачи по 5W
async def analyze_task(task_text):
    prompt = f"""
    Разбей задачу на 5W:
    1. Кто? (who)
    2. Что нужно сделать? (what)
    3. Где? (where)
    4. Когда? (when)
    5. Почему? (why)

    Текст задачи:
    {task_text}

    Ответь в формате JSON.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Ты военный аналитик."},
                  {"role": "user", "content": prompt}]
    )

    return json.loads(response['choices'][0]['message']['content'])

# Функция для анализа боевой обстановки (METT-TC, OCOKA, ASCOPE, погода)
async def analyze_battlefield(task_details):
    prompt = f"""
    Проанализируй задачу по следующим критериям:

    **1. METT-TC:**
    - Mission (Задача)
    - Enemy (Противник)
    - Terrain (Местность)
    - Troops (Дружественные силы)
    - Time (Время)
    - Civilians (Гражданские)

    **2. OCOKA (Анализ местности):**
    - Observation & Fields of Fire
    - Cover & Concealment
    - Obstacles
    - Key Terrain
    - Avenues of Approach

    **3. ASCOPE (Анализ гражданского фактора):**
    - Area
    - Structures
    - Capabilities
    - Organizations
    - People
    - Events

    Текст задачи:
    {task_details}

    Ответь в структурированном формате.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Ты военный аналитик."},
                  {"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']

# Функция генерации WARNORD
async def generate_warnord(task_details):
    prompt = f"""
    Сформируй WARNORD по следующей задаче:

    {task_details}

    **WARNORD:**
    1. **Ситуация** (Обзор METT-TC, OCOKA, ASCOPE)
    2. **Задание** (5W)
    3. **Выполнение** (Основные этапы и тактика)
    4. **Логистика** (Обеспечение, транспорт, медицинская поддержка)
    5. **Командование и связь** (Ответственные лица, сигналы связи)

    Ответь в четко структурированном формате.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Ты офицер штаба, составляющий WARNORD."},
                  {"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']

# Обработчик анализа задачи
@dp.message(lambda message: message.text == "Анализ задачи")
async def process_analysis(message: types.Message):
    await message.answer("Отправь текст задачи для анализа:")

@dp.message(lambda message: message.text.startswith("Боевая задача:"))
async def analyze_and_respond(message: types.Message):
    await message.answer("Анализирую задачу...")
    analysis = await analyze_task(message.text)
    battlefield_info = await analyze_battlefield(message.text)

    response_text = f"""
📌 **Результат анализа:**
1️⃣ **Кто?** {analysis['who']}
2️⃣ **Что?** {analysis['what']}
3️⃣ **Где?** {analysis['where']}
4️⃣ **Когда?** {analysis['when']}
5️⃣ **Почему?** {analysis['why']}

⚠ **Анализ боевой обстановки:**
{battlefield_info}
"""
    await message.answer(response_text)

# Обработчик генерации WARNORD
@dp.message(lambda message: message.text == "Создать WARNORD")
async def warnord_request(message: types.Message):
    await message.answer("Отправь текст боевой задачи для генерации полного WARNORD:")

@dp.message(lambda message: message.text.startswith("Боевая задача:"))
async def generate_and_respond(message: types.Message):
    await message.answer("Генерирую WARNORD...")
    warnord = await generate_warnord(message.text)

    response_text = f"""
📌 **Предварительный боевой приказ (WARNORD):**
{warnord}
"""
    await message.answer(response_text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())