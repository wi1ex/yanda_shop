FROM python:3.11
WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3478

CMD ["gunicorn", "--bind", "0.0.0.0:3478", "app:app"]