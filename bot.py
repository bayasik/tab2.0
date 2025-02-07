import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import openai
import json

# Логирование
logging.basicConfig(level=logging.INFO)

# Токены
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Создание бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройка клавиатуры
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Анализ задачи")],
        [KeyboardButton(text="⚔ Создать WARNORD")],
        [KeyboardButton(text="🌤 Погода")],
    ],
    resize_keyboard=True,
)

# OpenAI API
openai.api_key = OPENAI_API_KEY

# === ФУНКЦИЯ АНАЛИЗА ЗАДАЧИ (5W) ===
async def analyze_task(task_text):
    prompt = f"""
    Ты военный аналитик. Проанализируй задачу по схеме 5W:
    {task_text}
    Ответь в JSON-формате:
    {{
        "who": "Кто выполняет задачу",
        "what": "Что нужно сделать",
        "where": "Где это выполняется",
        "when": "Когда выполняется",
        "why": "Зачем это выполняется"
    }}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.5
    )
    return json.loads(response["choices"][0]["message"]["content"])

# === ФУНКЦИЯ АНАЛИЗА СИТУАЦИИ (METT-TC, OCOKA, ASCOPE, ПОГОДА) ===
async def analyze_situation(task_text):
    prompt = f"""
    Ты военный аналитик. Проанализируй задачу по военной системе METT-TC, включая анализ местности (OCOKA), гражданского фактора (ASCOPE) и погодных условий.  
    В JSON-формате:
    {{
        "METT-TC": {{
            "mission": "Анализ цели и приоритетов",
            "enemy": "Данные о противнике",
            "terrain": "Оценка местности",
            "troops": "Состояние своих сил",
            "time": "Оценка времени",
            "civilians": "Влияние гражданского фактора"
        }},
        "OCOKA": {{
            "observation": "Секторы наблюдения",
            "cover": "Возможности маскировки",
            "obstacles": "Преграды",
            "key_terrain": "Ключевые точки",
            "avenues": "Маршруты передвижения"
        }},
        "ASCOPE": {{
            "area": "Территория с населением",
            "structures": "Здания и сооружения",
            "capabilities": "Гражданская инфраструктура",
            "organization": "Группы влияния",
            "people": "Роли гражданских",
            "events": "Важные события"
        }},
        "weather": {{
            "visibility": "Видимость",
            "wind": "Ветер",
            "precipitation": "Осадки",
            "cloudiness": "Тучность",
            "temperature": "Температура и влажность"
        }}
    }}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.5
    )
    return json.loads(response["choices"][0]["message"]["content"])

# === ФУНКЦИЯ ГЕНЕРАЦИИ WARNORD ===
async def generate_warnord(task_text):
    task_analysis = await analyze_task(task_text)
    situation_analysis = await analyze_situation(task_text)

    warnord = f"""
🛑 **WARNORD** 🛑  
📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}  

## **1. СИТУАЦИЯ**  
📍 **Зона интереса:** {situation_analysis["METT-TC"]["terrain"]}  
🔻 **Противник:** {situation_analysis["METT-TC"]["enemy"]}  
🟢 **Дружественные силы:** {situation_analysis["METT-TC"]["troops"]}  
🏢 **Гражданский фактор:** {situation_analysis["METT-TC"]["civilians"]}  
🌍 **Анализ местности:** {situation_analysis["OCOKA"]["key_terrain"]}  

## **2. ЗАДАНИЕ**  
👥 **Кто:** {task_analysis["who"]}  
⚔ **Что:** {task_analysis["what"]}  
📍 **Где:** {task_analysis["where"]}  
⏳ **Когда:** {task_analysis["when"]}  
🎯 **Зачем:** {task_analysis["why"]}  

## **3. ВЫПОЛНЕНИЕ**  
📌 **Концепция:** {situation_analysis["OCOKA"]["avenues"]}  
🎯 **Главные задачи:** {task_analysis["what"]}  
🛠 **Подразделения и роли:** {situation_analysis["METT-TC"]["troops"]}  

## **4. ЛОГИСТИЧЕСКОЕ ОБЕСПЕЧЕНИЕ**  
🩺 **Медицина:** {situation_analysis["ASCOPE"]["capabilities"]}  
🎒 **Снабжение:** {situation_analysis["ASCOPE"]["structures"]}  
🚛 **Транспорт:** {situation_analysis["OCOKA"]["obstacles"]}  

## **5. КОМАНДОВАНИЕ И СВЯЗЬ**  
📡 **Средства связи:** Стандартные каналы  
🔑 **Кодовые сигналы:** По инструкции  
🆘 **Экстренные меры:** Отход по резервному маршруту  
"""
    return warnord

# === ОБРАБОТКА КОМАНД ===
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)

@dp.message_handler(lambda message: message.text == "📊 Анализ задачи")
async def handle_task_analysis(message: types.Message):
    await message.answer("Отправь текст боевой задачи для анализа.")

@dp.message_handler(lambda message: message.text == "⚔ Создать WARNORD")
async def handle_warnord(message: types.Message):
    await message.answer("Отправь текст боевой задачи для генерации полного WARNORD.")

@dp.message_handler(lambda message: message.text == "🌤 Погода")
async def handle_weather(message: types.Message):
    await message.answer("Функция погоды пока не реализована.")

@dp.message_handler()
async def process_text_message(message: types.Message):
    if "боевой задачи" in message.reply_to_message.text:
        analysis = await analyze_task(message.text)
        await message.answer(f"📊 **Результат анализа:**\n{json.dumps(analysis, indent=4, ensure_ascii=False)}")
    elif "WARNORD" in message.reply_to_message.text:
        warnord = await generate_warnord(message.text)
        await message.answer(warnord)

# === ЗАПУСК БОТА ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())