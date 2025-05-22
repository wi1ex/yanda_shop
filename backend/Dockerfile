FROM python:3.11
WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000", "--workers", "3"]
# CMD ["python", "app.py"]
