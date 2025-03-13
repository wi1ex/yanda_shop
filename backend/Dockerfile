FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80

ARG BOT_TOKEN
ENV BOT_TOKEN=${BOT_TOKEN}
ARG ADMIN_ID
ENV ADMIN_ID=${ADMIN_ID}

CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]