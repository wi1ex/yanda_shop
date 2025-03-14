FROM python:3.11
WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
ENV ADMIN_ID=${ADMIN_ID}
ENV BOT_TOKEN=${BOT_TOKEN}
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
