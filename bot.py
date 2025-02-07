import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import openai
import json

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токены
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Создаём объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Меню команд
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Анализ задачи")],
        [KeyboardButton(text="Создать WARNORD")],
        [KeyboardButton(text="Погода")],
    ],
    resize_keyboard=True
)

# Инлайн-кнопки для генерации WARNORD
warnord_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Ситуация", callback_data="situation")],
        [InlineKeyboardButton(text="Задание", callback_data="mission")],
        [InlineKeyboardButton(text="Выполнение", callback_data="execution")],
        [InlineKeyboardButton(text="Логистика", callback_data="logistics")],
        [InlineKeyboardButton(text="Связь", callback_data="comms")],
        [InlineKeyboardButton(text="Экспортировать", callback_data="export_warnord")],
    ]
)

# Словарь для хранения данных WARNORD
warnord_data = {}

# Команда /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)

# Анализ задачи (5W)
@dp.message(lambda message: message.text == "Анализ задачи")
async def analyze_task(message: types.Message):
    await message.answer("Отправь текст задачи для анализа:")

@dp.message(lambda message: message.text and message.text != "Анализ задачи")
async def process_task(message: types.Message):
    await message.answer("Анализирую задачу...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Разбери задачу по методу 5W."},
                {"role": "user", "content": message.text}
            ]
        )
        task_analysis = json.loads(response["choices"][0]["message"]["content"])
        warnord_data["task"] = task_analysis

        formatted_analysis = (
            f"**Время задания:** {task_analysis.get('when', 'не указано')}\n\n"
            f"**Цель:**\n{task_analysis.get('what', 'не указано')}\n"
        )

        await message.answer(formatted_analysis, parse_mode="Markdown")
        await message.answer("Теперь можно создать WARNORD:", reply_markup=warnord_menu)
    
    except Exception as e:
        logging.error(f"Ошибка при анализе: {e}")
        await message.answer("Произошла ошибка при анализе задачи.")

# Генерация WARNORD по частям
@dp.callback_query(lambda c: c.data in ["situation", "mission", "execution", "logistics", "comms"])
async def generate_warnord(callback: types.CallbackQuery):
    section = callback.data

    warnord_templates = {
        "situation": "Параграф 1: СИТУАЦИЯ\nОперативная обстановка в зоне операции...",
        "mission": f"Параграф 2: ЗАДАНИЕ\n{warnord_data.get('task', {}).get('what', 'не указано')}",
        "execution": "Параграф 3: ВЫПОЛНЕНИЕ\nДетальный план действий...",
        "logistics": "Параграф 4: ЛОГИСТИКА\nОбеспечение боеприпасами, медицинская поддержка...",
        "comms": "Параграф 5: КОМАНДОВАНИЕ И СВЯЗЬ\nСредства связи и сигналы..."
    }

    warnord_data[section] = warnord_templates[section]
    await callback.message.answer(warnord_templates[section], parse_mode="Markdown")

# Экспорт полного WARNORD
@dp.callback_query(lambda c: c.data == "export_warnord")
async def export_warnord(callback: types.CallbackQuery):
    full_warnord = "\n\n".join([warnord_data.get(sec, f"{sec.upper()} не заполнен.") for sec in ["situation", "mission", "execution", "logistics", "comms"]])
    await callback.message.answer(f"**Полный WARNORD:**\n\n{full_warnord}", parse_mode="Markdown")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())