FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "backend:app", "-b", "0.0.0.0:8000", "--workers", "3", "--timeout", "30"]
