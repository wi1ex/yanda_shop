# Yanda Shop

> 🚀 Готовое к продакшену решение интернет-магазина: backend и frontend, интеграция с Telegram‑ботом, контейнеризация через Docker & Docker‑Compose.

---

## ✨ Оглавление

1. [Сервисы Docker-Compose](#сервисы-docker-compose)
2. [Переменные окружения](#переменные-окружения)
3. [Справочник API](#справочник-api)
4. [Быстрый старт](#быстрый-старт)
   - [1. Подготовка сервера](#1-подготовка-сервера)
   - [2. Клон и конфигурация](#2-клон-и-конфигурация)
   - [3. SSL через Certbot](#3-ssl-через-certbot)
   - [4. Запуск и миграции](#4-запуск-и-миграции)
5. [Скрипты](#скрипты)
   - [`deploy.sh`](#deploysh)
   - [`backup_all.sh`](#backup_allsh)
   - [`restore_all.sh`](#restore_allsh)

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
cd /root/app/yanda_shop

# npm install локально для обновления package-lock.json
# Запись домена (помимо .env) в store.js, nginx.conf и BotFather

# Дать права на запуск деплой-скрипта
chmod +x deploy.sh

# Полный деплой
./deploy.sh
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

### `deploy.sh`

> **Обновление и деплой всех сервисов**

```bash
1) Обновляем код
2) Останавливаем прежние контейнеры
2) Чистим старый кэш (если есть)
4) Обновление SSL-сертификатов (если нужно)
5) Пересобираем образы
6) Поднимаем образы
7) Применяем миграции в свежесобранном образе
8) Финальная проверка и логи
```

---

### `backup_all.sh`

> **Резервное копирование PostgreSQL, Redis и MinIO**

```bash
1) Дамп PostgreSQL
2) RDB-файл Redis
3) Mirror и архив MinIO
4) Удаление бэкапов старше 7 дней
```

*Запускать по расписанию через cron или systemd-timer.*

---

### `restore_all.sh`

> **Восстановление из последних бэкапов**

```bash
1) Остановить сервисы
2) Восстановить Postgres из .dump
3) Восстановить Redis (RDB → volume)
4) Восстановить MinIO (tar.gz → mc mirror)
5) Запустить сервисы
```

---
