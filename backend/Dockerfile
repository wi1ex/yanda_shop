FROM python:3.11-slim
WORKDIR /app

# Установите зависимости
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируйте код
COPY . .

# Запуск приложения
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]