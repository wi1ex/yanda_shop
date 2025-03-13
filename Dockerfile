# Базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем приложение через Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:80", "main:app"]