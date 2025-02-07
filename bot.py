import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
import openai

# Загрузка переменных окружения (для локального теста)
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Получаем токены из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not BOT_TOKEN:
    raise Exception("Переменная BOT_TOKEN не установлена!")
if not OPENAI_API_KEY:
    raise Exception("Переменная OPENAI_API_KEY не установлена!")

openai.api_key = OPENAI_API_KEY

# Инициализация бота, диспетчера и хранилища состояний
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Главное меню (клавиатура)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Анализ задачи")],
        [KeyboardButton(text="Создать WARNORD")],
        [KeyboardButton(text="Погода")],
    ],
    resize_keyboard=True
)

# Определяем FSM для ожидания текста задачи
class Form(StatesGroup):
    waiting_for_task_text = State()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Отправь мне текст задачи для анализа по принципу 5W.", reply_markup=main_menu)

# Обработчик кнопки "Анализ задачи" – перевод в состояние ожидания текста
@dp.message(lambda message: message.text == "Анализ задачи")
async def ask_for_task(message: types.Message, state: FSMContext):
    await message.answer("Отправь текст задачи для анализа:")
    await state.set_state(Form.waiting_for_task_text)

# Обработка текста задачи и вызов OpenAI для анализа по принципу 5W
@dp.message(Form.waiting_for_task_text)
async def process_task(message: types.Message, state: FSMContext):
    task_text = message.text
    await message.answer("Анализирую задачу...")

    prompt = (
        "Проанализируй следующий текст задачи по принципу 5W. "
        "Выдели информацию по следующим пунктам: Who (Кто?), What (Что?), Where (Где?), When (Когда?), Why (Почему?). "
        "Ответь в формате JSON с ключами: 'who', 'what', 'where', 'when', 'why'.\n\n"
        f"Текст задачи: {task_text}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник, который анализирует текст задачи по принципу 5W."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        analysis = response.choices[0].message.content.strip()
        await message.answer(f"Результат анализа:\n{analysis}", reply_markup=main_menu)
    except Exception as e:
        logging.exception("Ошибка при вызове OpenAI API")
        await message.answer("Произошла ошибка при анализе задачи.", reply_markup=main_menu)
    await state.clear()

# Обработчик кнопки "Создать WARNORD" (пока-заглушка)
@dp.message(lambda message: message.text == "Создать WARNORD")
async def create_warnord(message: types.Message):
    await message.answer("Функция создания WARNORD пока не реализована.", reply_markup=main_menu)

# Обработчик кнопки "Погода" (пока-заглушка)
@dp.message(lambda message: message.text == "Погода")
async def weather_handler(message: types.Message):
    await message.answer("Функция погоды пока не реализована.", reply_markup=main_menu)

# Главная функция запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
