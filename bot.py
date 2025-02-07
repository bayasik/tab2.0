import asyncio
import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from openai import OpenAI, OpenAIError

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токены из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Создаём объекты бота и диспетчера
bot = Bot(token=TOKEN)
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

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)


@dp.message(lambda message: message.text == "Анализ задачи")
async def request_task(message: types.Message):
    await message.answer("Отправь текст задачи для анализа:")


@dp.message(lambda message: message.text not in ["Анализ задачи", "Создать WARNORD", "Погода"])
async def process_task(message: types.Message):
    user_text = message.text.strip()

    if not user_text:
        await message.answer("Ошибка: Задача не может быть пустой.")
        return

    await message.answer("Анализирую задачу...")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Разбей задачу на 5W (who, what, where, when, why)"},
                {"role": "user", "content": user_text}
            ]
        )

        result_text = response.choices[0].message.content.strip()

        # Проверяем, является ли результат валидным JSON
        try:
            result_data = json.loads(result_text)
        except json.JSONDecodeError:
            await message.answer("Ошибка: получен некорректный формат данных от AI.")
            return

        formatted_result = f"""
🔍 **Результат анализа:**
**Кто:** {result_data.get("who", "Не указано")}
**Что:** {result_data.get("what", "Не указано")}
**Где:** {result_data.get("where", "Не указано")}
**Когда:** {result_data.get("when", "Не указано")}
**Почему:** {result_data.get("why", "Не указано")}
"""

        await message.answer(formatted_result)

    except OpenAIError as e:
        logging.error(f"Ошибка при вызове OpenAI API: {e}")
        await message.answer("Произошла ошибка при анализе задачи. Попробуй позже.")


@dp.message(lambda message: message.text == "Создать WARNORD")
async def create_warnord(message: types.Message):
    await message.answer("Функция создания WARNORD пока не реализована.")


@dp.message(lambda message: message.text == "Погода")
async def weather_info(message: types.Message):
    await message.answer("Функция погоды пока не реализована.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())