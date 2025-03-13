FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3478

ARG BOT_TOKEN
ENV BOT_TOKEN=${BOT_TOKEN}
ARG ADMIN_ID
ENV ADMIN_ID=${ADMIN_ID}

CMD ["gunicorn", "-b", "0.0.0.0:3478", "run:app"]
