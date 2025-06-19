# Yanda Shop

> 🚀 Готовое к продакшену решение интернет-магазина: backend и frontend, интеграция с Telegram‑ботом, контейнеризация через Docker & Docker‑Compose.

---

## ✨ Оглавление

1. [Сервисы Docker-Compose](#сервисы-docker-compose)  
2. [Переменные окружения](#переменные-окружения)  
3. [Справочник API](#справочник-api)  
4. [Быстрый старт](#быстрый-старт)  
   4.1. [Подготовка сервера](#41-подготовка-сервера)  
   4.2. [Клон и конфигурация](#42-клон-и-конфигурация)  
   4.3. [SSL через Certbot](#43-ssl-через-certbot)  
   4.4. [Запуск и миграции](#44-запуск-и-миграции)  
5. [Скрипты](#5-скрипты)  
6. [Автодеплой (GitHub Actions)](#6-автодеплой-проекта-на-сервер-с-помощью-github-actions)  


---

## Сервисы Docker‑Compose

| Сервис       | Назначение               | Порт   |
| ------------ | ------------------------ | ------ |
| **db**       | PostgreSQL               | 5432   |
| **redis**    | Redis                    | 6379   |
| **minio**    | S3-совместимое хранилище | 9000   |
| **backend**  | Flask-REST API           | 8000   |
| **bot**      | Telegram-бот             | –      |
| **frontend** | Vue.js                   | –      |
| **proxy**    | Nginx прокси и SSL       | 80,443 |

### Архитектурная схема

* Микросервисная топология: схема взаимодействия контейнеров в Docker Compose.
* Data flow: последовательность запросов от SPA → Nginx → Backend → DB/Redis/MinIO.

### Технологический стек

| Компонент             | Технология              | Версия     |
| --------------------- | ----------------------- | ---------- |
| Язык программирования | Python                  | 3.11       |
| Web-фреймворк         | Flask                   | 3.0        |
| WSGI-сервер           | Gunicorn                | 21.2       |
| ORM                   | SQLAlchemy              | 1.11       |
| Миграции              | Alembic                 | 3.1        |
| База данных           | PostgreSQL              | 17         |
| Кэш и сессии          | Redis                   | 7          |
| Объектное хранилище   | MinIO                   | latest     |
| SPA-фреймворк         | Vue.js                  | 3.3        |
| Сборщик               | Vite                    | 4.4        |
| State management      | Pinia                   | 3.0        |
| HTTP-клиент           | Axios                   | 1.6        |
| Telegram-бот          | Aiogram                 | 3.10       |
| Reverse proxy         | Nginx                   | 1.25.x     |

---

## Переменные окружения

| Переменная                                                             | Описание                                |
| ---------------------------------------------------------------------- | --------------------------------------- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`              | Параметры подключения к PostgreSQL      |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`                           | Параметры подключения к Redis           |
| `MINIO_HOST`, `MINIO_BUCKET`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` | Конфиг MinIO S3                         |
| `BOT_TOKEN`                                                            | Токен Telegram-бота                     |
| `BACKEND_URL`                                                          | Базовый URL API и ссылок на изображения |
| `ADMIN_IDS`                                                            | ID администраторов в Telegram           |

---

## Справочник API

Базовый URL: `https://shop.yourdomain.com/api`

| Endpoint                                            | Метод    | Описание                                            |
| --------------------------------------------------- | -------- | --------------------------------------------------- |
| `/`                                                 | GET      | Проверка статуса                                    |
| `/save_user`                                        | POST     | Лог посещения & сохранение Telegram-пользователя    |
| `/visits?date=YYYY-MM-DD`                           | GET      | Почасовые общие и уникальные посещения              |
| `/products?category=<shoes/clothing/accessories>`   | GET      | Список товаров (основная информация)                |
| `/product?category=&sku=`                           | GET      | Детали товара + URL-изображения                     |
| `/import_products`                                  | POST     | Импорт из CSV (form-data: file, author\_id, name)   |
| `/upload_images`                                    | POST     | Загрузка ZIP в MinIO                                |
| `/logs?limit=N`                                     | GET      | Последние логи изменений                            |
| `/user?user_id=`                                    | GET      | Профиль Telegram-пользователя                       |
| `/cart`                                             | GET/POST | Получить/сохранить корзину (Redis)                  |
| `/favorites`                                        | GET/POST | Получить/сохранить избранное (Redis)                |
| `/admin/sheet_urls`                                 | GET      | Получить URL Google Sheets                          |
| `/admin/sheet_url`                                  | POST     | Установить URL Google Sheets                        |
| `/import_sheet`                                     | POST     | Импорт товаров из Google Sheets                     |

---

## Быстрый старт

### 1. Подготовка сервера

```bash
# Обновление и утилиты
apt update && apt upgrade -y
apt install -y ca-certificates curl gnupg lsb-release ufw

# Фаервол
ufw allow OpenSSH
ufw allow 80,443/tcp
ufw --force enable

# Docker & Compose
apt install -y docker.io docker-compose
systemctl enable docker
```

*Добавление официального репозитория Docker и установка последних пакетов:*

```bash
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | tee /etc/apt/keyrings/docker.asc > /dev/null

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
   https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io \
               docker-buildx-plugin docker-compose-plugin
systemctl enable docker.socket
systemctl start docker.socket
systemctl restart docker
docker login --username <your-username> <your-password>
```

---

### 2. Клон и конфигурация

```bash
mkdir -p ~/app && cd ~/app
rm -rf yanda_shop
git clone https://<TOKEN>@github.com/wi1ex/yanda_shop.git
cd yanda_shop

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

---

### 3. SSL через Certbot

```bash
apt install -y certbot
certbot certonly --standalone -d yourdomain.example.com
# Для принудительного обновления:
certbot renew --force-renewal
```

---

### 4. Запуск и миграции

```bash
# npm install локально для обновления package-lock.json
# Запись домена (помимо .env) в store.js, nginx.conf и BotFather

# Обновляем код
cd /root/app/yanda_shop
git fetch --all
git reset --hard origin/main

# Останавливаем прежние контейнеры и чистим ненужное
docker-compose down
docker builder prune --filter "until=72h" --force
docker image prune --filter "until=72h" --force

# Для полной очистки
# docker-compose down --rmi all --volumes --remove-orphans
# docker system prune --all --volumes --force

# Обновление SSL-сертификатов (только если нужно)
certbot renew --noninteractive --standalone --agree-tos

# Пересобираем образы
docker-compose build --no-cache

# Поднимаем образы
docker-compose up -d

# Применяем миграции в свежесобранном образе
docker-compose run --rm backend flask db upgrade

# Финальная проверка и логи
docker-compose ps
docker-compose logs -f
```

*При первом запуске миграций (если ещё не применялись в проде):*

```bash
docker-compose up -d db backend
docker-compose exec backend flask db init
docker-compose exec backend flask db migrate -m "initial schema"
docker-compose exec backend flask db upgrade
docker-compose up -d
```

---

## Скрипты

### `backup_all.sh - резервное копирование PostgreSQL, Redis и MinIO`

```bash
1) Дамп PostgreSQL
2) RDB-файл Redis
3) Mirror и архив MinIO
4) Удаление бэкапов старше 7 дней
```

*Запускать по расписанию через cron или systemd-timer.*

---

### `restore_all.sh - восстановление из последних бэкапов`

```bash
1) Остановить сервисы
2) Восстановить Postgres из .dump
3) Восстановить Redis (RDB → volume)
4) Восстановить MinIO (tar.gz → mc mirror)
5) Запустить сервисы
```

---

## Автодеплой проекта на сервер с помощью GitHub Actions

На **сервере** выполните:

```bash
# Перейдите в корень проекта
cd path/to/yanda_shop

# Сгенерируйте ED25519-ключ (без пароля):
ssh-keygen -t ed25519 -f github_deploy_key -N ""

# создаём папку ~/.ssh, если её нет
mkdir -p ~/.ssh && chmod 700 ~/.ssh

# добавляем публичный ключ в авторизованные
cat ~/github_deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# удаляем временный файл
rm ~/github_deploy_key.pub

# чтобы GitHub Actions мог «доверять» вашему серверу
ssh-keyscan -H SERVER_HOST > known_hosts.txt
```

В веб-интерфейсе вашего репозитория:

```
Settings → Secrets and variables → Actions → New repository secret
```

Создайте четыре секрета:

| Имя               | Значение                                          |
| ----------------- | ------------------------------------------------- |
| SSH\_PRIVATE\_KEY | содержимое `github_deploy_key`                    |
| SSH\_KNOWN\_HOSTS | содержимое `known_hosts.txt`                      |
| SERVER\_HOST      | IP вашего сервера (например, `1.2.3.4`)           |
| SERVER\_USER      | имя SSH-пользователя (обычно `root`)              |

В корне репозитория заведите файл `.github/workflows/deploy.yml` со следующим содержимым:

```yaml
name: Deploy on push to main

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      # 1) Забираем код
      - name: Checkout code
        uses: actions/checkout@v4

      # 2) Пишем SSH-ключ и known_hosts в runner
      - name: Configure SSH key and known_hosts
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}"  > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key

          echo "${{ secrets.SSH_KNOWN_HOSTS }}"   > ~/.ssh/known_hosts
          chmod 600 ~/.ssh/known_hosts
        shell: bash

      # 3) Подключаемся по SSH и выполняем деплой-скрипт
      - name: Deploy on server
        run: |
          ssh -i ~/.ssh/deploy_key \
              -o StrictHostKeyChecking=yes \
              -l "${{ secrets.SERVER_USER }}" \
              "${{ secrets.SERVER_HOST }}" << 'EOF'
            set -euo pipefail
            cd /root/app/yanda_shop

            # 1. Синхронизируем код
            git fetch --all
            git reset --hard origin/main

            # 2. Останавливаем контейнеры и чистим образы
            docker-compose down
            docker builder prune --filter "until=72h" --force
            docker image prune   --filter "until=72h" --force

            # 3. (Опционально) обновляем SSL
            certbot renew --noninteractive --standalone --agree-tos

            # 4. Сборка и поднятие новых контейнеров
            docker-compose build --no-cache
            docker-compose up -d

            # 5. Миграции и финальная проверка
            docker-compose run --rm backend flask db upgrade
            docker-compose ps
          EOF
        shell: bash
```

После успешной настройки **удалите** из папки `/root/app/yanda_shop` все временные артефакты:

```bash
cd /root/app/yanda_shop
rm -f github_deploy_key github_deploy_key.pub known_hosts.txt
```
