import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import openai
import json

# Логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токены
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# API-ключ OpenAI
openai.api_key = OPENAI_API_KEY

# Клавиатура
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Анализ задачи")],
        [KeyboardButton(text="Создать WARNORD")],
        [KeyboardButton(text="Погода")]
    ],
    resize_keyboard=True
)

# /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)

# Анализ задачи (5W)
@dp.message(lambda message: message.text == "Анализ задачи")
async def analyze_task_command(message: types.Message):
    await message.answer("Отправь текст задачи для анализа:")

@dp.message(lambda message: message.text and message.text not in ["Анализ задачи", "Создать WARNORD", "Погода"])
async def process_task(message: types.Message):
    await message.answer("🔍 Анализирую задачу...")

    prompt = f"""
    Разбери задачу по принципу 5W:
    {message.text}
    Формат:
    {{
      "who": "...",
      "what": "...",
      "where": "...",
      "when": "...",
      "why": "..."
    }}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )

        analysis = json.loads(response["choices"][0]["message"]["content"])

        result_text = (
            f"📌 **Результат анализа:**\n"
            f"1️⃣ Кто? {analysis['who']}\n"
            f"2️⃣ Что? {analysis['what']}\n"
            f"3️⃣ Где? {analysis['where']}\n"
            f"4️⃣ Когда? {analysis['when']}\n"
            f"5️⃣ Почему? {analysis['why']}"
        )

        await message.answer(result_text)

    except Exception as e:
        logging.error(f"Ошибка при анализе: {e}")
        await message.answer("⚠ Ошибка при анализе задачи.")

# **Создание WARNORD**
@dp.message(lambda message: message.text == "Создать WARNORD")
async def create_warnord_command(message: types.Message):
    await message.answer("Отправь текст задачи для генерации полного WARNORD:")

@dp.message(lambda message: message.text and message.text not in ["Анализ задачи", "Создать WARNORD", "Погода"])
async def generate_warnord(message: types.Message):
    await message.answer("📜 Генерирую WARNORD...")

    prompt = f"""
    Составь полный WARNORD по задаче:
    {message.text}

    **Формат ответа:**
    **WARNORD**
    1️⃣ **СИТУАЦИЯ**
    - Зона интереса: ...
    - Зона операции: ...
    - Местность: ...
    - Погодные условия: ...
    - Вражеское окружение: ...
    - Дружественные силы: ...
    - Гражданский фактор: ...

    2️⃣ **ЗАДАНИЕ**
    - Что: ...
    - Кто: ...
    - Где: ...
    - Когда: ...
    - Почему: ...

    3️⃣ **ВЫПОЛНЕНИЕ**
    - Концепция: ...
    - Основной удар: ...
    - Этапы: ...
    - Роли в группе: ...
    - Ожидаемый результат: ...

    4️⃣ **ЛОГИСТИКА**
    - Медицинская поддержка: ...
    - Обеспечение ресурсами: ...
    - Транспорт: ...
    - Техническое обслуживание: ...

    5️⃣ **КОМАНДОВАНИЕ И СВЯЗЬ**
    - Командование: ...
    - Связь: ...
    - Кодовые слова: ...
    - Связь в ЧС: ...
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )

        warnord_text = response["choices"][0]["message"]["content"]
        await message.answer(warnord_text)

    except Exception as e:
        logging.error(f"Ошибка при генерации WARNORD: {e}")
        await message.answer("⚠ Ошибка при генерации WARNORD.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())