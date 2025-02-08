import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import openai

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем токены
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # ID чата для логов

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Анализ задачи")],
        [KeyboardButton(text="⚔ Создать WARNORD")],
        [KeyboardButton(text="🌤 Погода")],
        [KeyboardButton(text="🔄 Рестарт")]
    ],
    resize_keyboard=True
)

openai.api_key = OPENAI_API_KEY

async def send_log_to_telegram(log_text):
    """ Отправка логов в Telegram """
    try:
        await bot.send_message(ADMIN_CHAT_ID, f"📝 *Лог*: {log_text}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка отправки лога в Telegram: {e}")

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)

@dp.message()
async def handle_messages(message: types.Message):
    text = message.text.lower()
    logger.info(f"📩 Получено сообщение: {text}")
    await send_log_to_telegram(f"📩 Получено сообщение: `{text}`")

    if text == "📊 анализ задачи":
        await message.answer("Отправь текст боевой задачи для анализа.")
    elif text == "⚔ создать warnord":
        await message.answer("Отправь текст боевой задачи для генерации полного WARNORD.")
    elif text == "🌤 погода":
        await message.answer("⏳ Анализирую погоду...")
        weather_report = await analyze_weather()
        await message.answer(weather_report, parse_mode="Markdown")
    elif text == "🔄 рестарт":
        await message.answer("♻ Перезапуск бота...")
        await send_log_to_telegram("♻ Рестарт бота...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        if message.reply_to_message and "для анализа" in message.reply_to_message.text:
            await message.answer("⏳ Обрабатываю анализ задачи...")
            analysis = await analyze_task(message.text)
            await message.answer(f"📊 **Результат анализа:**\n{analysis}", parse_mode="Markdown")
        elif message.reply_to_message and "для генерации полного WARNORD" in message.reply_to_message.text:
            await message.answer("⏳ Генерирую полный WARNORD...")
            warnord = await generate_warnord(message.text)
            await message.answer(f"⚔ **WARNORD:**\n{warnord}", parse_mode="Markdown")

async def analyze_task(task_text: str):
    logger.info("🔍 Запрос на анализ задачи отправлен...")
    await send_log_to_telegram("🔍 Запрос на анализ задачи отправлен...")
    
    prompt = f"Ты тактический аналитик, анализируй задачу...\n{task_text}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1000
        )
        logger.info("✅ Анализ задачи завершен.")
        await send_log_to_telegram("✅ Анализ задачи завершен.")
        return response["choices"][0]["message"]["content"]
    except openai.OpenAIError as e:
        logger.error(f"❌ Ошибка OpenAI API: {e}")
        await send_log_to_telegram(f"❌ Ошибка OpenAI API: {e}")
        return "❌ Ошибка при анализе задачи."

async def generate_warnord(task_text: str):
    logger.info("📝 Запрос на генерацию WARNORD отправлен...")
    await send_log_to_telegram("📝 Запрос на генерацию WARNORD отправлен...")
    
    prompt = f"Ты штабной офицер, сгенерируй полный WARNORD...\n{task_text}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1500
        )
        logger.info("✅ WARNORD сгенерирован.")
        await send_log_to_telegram("✅ WARNORD сгенерирован.")
        return response["choices"][0]["message"]["content"]
    except openai.OpenAIError as e:
        logger.error(f"❌ Ошибка OpenAI API: {e}")
        await send_log_to_telegram(f"❌ Ошибка OpenAI API: {e}")
        return "❌ Ошибка при генерации WARNORD."

async def analyze_weather():
    logger.info("🌤 Запрос на анализ погоды отправлен...")
    await send_log_to_telegram("🌤 Запрос на анализ погоды отправлен...")
    
    prompt = """Ты военный метеоролог. Составь анализ погоды в таком формате:

📊 **Анализ погоды**
| Условия     | Влияние на нас        | Влияние на врага      | Вывод |
|-------------|----------------------|----------------------|-------|
| Видимость   | Ограничена дымкой     | Вражеские БПЛА сложнее применить | Уменьшенная видимость |
| Ветер       | 10 м/с, южный         | Ограничивает точность стрельбы | Ветер мешает снайперам |
| Осадки      | Моросящий дождь       | Размокание почвы      | Усложняет передвижение |
| Тучность    | Высокая               | Снижает точность дронов | Ограниченная аэроразведка |
| Температура | +5°C, влажность 80%   | Возможность переохлаждения | Требуется утепление |

В анализе погоды должны быть **видимость, ветер, осадки, тучность, температура и влажность** с влиянием на обе стороны.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=500
        )
        logger.info("✅ Анализ погоды завершен.")
        await send_log_to_telegram("✅ Анализ погоды завершен.")
        return response["choices"][0]["message"]["content"]
    except openai.OpenAIError as e:
        logger.error(f"❌ Ошибка OpenAI API: {e}")
        await send_log_to_telegram(f"❌ Ошибка OpenAI API: {e}")
        return "❌ Ошибка при анализе погоды."

async def main():
    logger.info("🚀 Запуск бота...")
    await send_log_to_telegram("🚀 Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())