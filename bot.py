import asyncio
import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import openai

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
        [KeyboardButton(text="📊 Анализ задачи")],
        [KeyboardButton(text="⚔ Создать WARNORD")],
        [KeyboardButton(text="🌤 Погода")],
    ],
    resize_keyboard=True
)

openai.api_key = OPENAI_API_KEY

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я тактический ассистент. Выбери действие:", reply_markup=menu)

@dp.message()
async def handle_messages(message: types.Message):
    text = message.text.lower()

    if text == "📊 анализ задачи":
        await message.answer("Отправь текст боевой задачи для анализа (5W, METT-TC, OCOKA, ASCOPE, анализ погоды).", reply_markup=menu)
    elif text == "⚔ создать warnord":
        await message.answer("Отправь текст боевой задачи для генерации полного WARNORD.", reply_markup=menu)
    elif text == "🌤 погода":
        weather_report = await analyze_weather()
        await message.answer(weather_report, parse_mode="Markdown", reply_markup=menu)
    else:
        if message.reply_to_message:
            if "для анализа" in message.reply_to_message.text:
                await message.answer("Анализирую задачу... 🔍", reply_markup=menu)
                analysis = await analyze_task(message.text)
                await message.answer(f"📊 **Результат анализа:**\n{analysis}", parse_mode="Markdown", reply_markup=menu)
            elif "для генерации полного WARNORD" in message.reply_to_message.text:
                await message.answer("Генерирую WARNORD... 🛠", reply_markup=menu)
                warnord = await generate_warnord(message.text)
                await message.answer(f"⚔ **WARNORD:**\n{warnord}", parse_mode="Markdown", reply_markup=menu)

### АНАЛИЗ ЗАДАЧИ
async def analyze_task(task_text: str):
    prompt = f"""Ты — тактический аналитик. Разбери боевую задачу по следующим параметрам:
1️⃣ **5W:** (Who, What, Where, When, Why)  
2️⃣ **METT-TC:** (Mission, Enemy, Terrain, Troops, Time, Civilians)  
3️⃣ **OCOKA:** (Observation, Cover & Concealment, Obstacles, Key Terrain, Avenues of Approach)  
4️⃣ **ASCOPE:** (Area, Structures, Capabilities, Organizations, People, Events)  
5️⃣ **Анализ погоды:** Влияние на выполнение миссии.  

Текст задачи: {task_text}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1000
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.OpenAIError as e:
        logging.error(f"Ошибка OpenAI API: {e}")
        return "❌ Ошибка при анализе задачи."

### ГЕНЕРАЦИЯ ПОЛНОГО WARNORD
async def generate_warnord(task_text: str):
    prompt = f"""Ты — военный штабной офицер. Сгенерируй полный WARNORD для этой боевой задачи, используя следующий формат:

1️⃣ **Ситуация**  
- Зона интереса  
- Зона операции  
- Описание местности (OCOKA)  
- Погодные условия (анализ влияния погоды)  
- Вражеское окружение (METT-TC)  
- Дружественные силы (METT-TC)  
- Гражданский фактор (ASCOPE)  

2️⃣ **Задание**  
- 5W (Кто, Что, Где, Когда, Почему)  

3️⃣ **Исполнение**  
- Общая концепция  
- Основные усилия  
- Фазы выполнения  
- Индивидуальные задачи бойцов  
- Ожидаемый результат  

4️⃣ **Логистика**  
- Медицинское обеспечение  
- Боеприпасы, топливо, питание  
- Средства передвижения  
- Техническое обеспечение  

5️⃣ **Командование и связь**  
- Командная структура  
- Каналы связи  
- Кодовые слова и экстренные сигналы  

**Текст боевой задачи:** {task_text}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1500
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.OpenAIError as e:
        logging.error(f"Ошибка OpenAI API: {e}")
        return "❌ Ошибка при генерации WARNORD."

### АНАЛИЗ ПОГОДЫ
async def analyze_weather():
    prompt = """Ты — военный метеоролог. Составь анализ погоды в таком формате:

📊 **Анализ погоды**
| Условия     | Влияние на нас        | Влияние на врага      | Вывод |
|-------------|----------------------|----------------------|-------|
| Видимость   | Ограничена дымкой     | Вражеские БПЛА сложнее применить | Уменьшенная видимость |
| Ветер       | 10 м/с, южный         | Ограничивает точность стрельбы | Ветер мешает снайперам |
| Осадки      | Моросящий дождь       | Размокание почвы      | Усложняет передвижение |
| Тучность    | Высокая               | Снижает точность дронов | Ограниченная аэроразведка |
| Температура | +5°C, влажность 80%   | Возможность переохлаждения | Требуется утепление |

Анализ погоды должен включать **видимость, ветер, осадки, тучность, температуру и влажность**, а также их влияние на обе стороны.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.OpenAIError as e:
        logging.error(f"Ошибка OpenAI API: {e}")
        return "❌ Ошибка при анализе погоды."

### ЗАПУСК БОТА
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())