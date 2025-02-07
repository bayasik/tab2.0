# Используем официальный Python-образ
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота
CMD ["python", "bot.py"]
