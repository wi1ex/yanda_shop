FROM python:3.11
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000", "--workers", "1", "--timeout", "30"]
