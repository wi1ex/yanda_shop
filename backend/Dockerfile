FROM python:3.11
WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
CMD ["gunicorn", "-w", "4", "--preload", "-b", "0.0.0.0:80", "app:app"]
