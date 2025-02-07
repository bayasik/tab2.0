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
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Создаём бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаём клавиатуру меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Анализ задачи")],
        [KeyboardButton(text="Создать WARNORD")],
        [KeyboardButton(text="Погода")],
    ],
    resize_keyboard=True
)

# Функция анализа задачи по 5W
async def analyze_task(task_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Разбери задачу по принципу 5W."},
                {"role": "user", "content": f"Проанализируй задачу:\n{task_text}"}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        return "Ошибка при анализе задачи."

# Функция анализа погоды
async def analyze_weather():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Сформируй анализ погоды в военном формате."},
                {"role": "user", "content": "Опиши военное влияние погодных условий."}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        return "Ошибка при анализе погоды."

# Функция генерации WARNORD
async def generate_warnord(task_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Создай полный боевой приказ (WARNORD)."},
                {"role": "user", "content": f"Сформируй WARNORD для задачи:\n{task_text}"}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        return "Ошибка при генерации WARNORD."

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)

# Обработчик кнопки "Анализ задачи"
@dp.message(lambda message: message.text == "Анализ задачи")
async def request_task_analysis(message: types.Message):
    await message.answer("Отправь текст задачи для анализа:")

# Обработчик кнопки "Погода"
@dp.message(lambda message: message.text == "Погода")
async def weather_info(message: types.Message):
    await message.answer("Анализирую погодные условия...")
    weather_result = await analyze_weather()
    await message.answer(f"🌦 **Анализ погоды:**\n{weather_result}")

# Обработчик кнопки "Создать WARNORD"
@dp.message(lambda message: message.text == "Создать WARNORD")
async def request_warnord_creation(message: types.Message):
    await message.answer("Отправь текст задачи для генерации полного WARNORD.")

# Обработчик входящего текста (анализ задачи)
@dp.message(lambda message: message.text and not message.text.startswith("/"))
async def process_task(message: types.Message):
    await message.answer("Анализирую задачу...")
    analysis_result = await analyze_task(message.text)
    await message.answer(f"📌 **Результат анализа:**\n{analysis_result}")

# Обработчик входящего текста (генерация WARNORD)
@dp.message(lambda message: message.text and message.text.startswith("WARNORD:"))
async def process_warnord(message: types.Message):
    await message.answer("📋 Генерирую полный WARNORD...")
    warnord_result = await generate_warnord(message.text)
    await message.answer(f"📋 **Сгенерированный WARNORD:**\n{warnord_result}")

# Основной цикл
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())