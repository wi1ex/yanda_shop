# Yanda Shop

> 🚀 Готовое к продакшену решение интернет-магазина: backend и frontend, интеграция с Telegram‑ботом, контейнеризация через Docker & Docker‑Compose.

---

## ✨ Оглавление

1. [Сервисы Docker-Compose](#сервисы-docker-compose)  
2. [Переменные окружения](#переменные-окружения)  
3. [Справочник API](#справочник-api)  
4. [Быстрый старт](#быстрый-старт)  
   4.1. [Подготовка сервера](#1-подготовка-сервера)  
   4.2. [Клон и конфигурация](#2-клон-и-конфигурация)  
   4.3. [SSL через Certbot](#3-ssl-через-certbot)  
   4.4. [Запуск](#4-запуск)  
5. [Скрипты](#5-скрипты)  
6. [Автодеплой (GitHub Actions)](#6-автодеплой-проекта-на-сервер-с-помощью-github-actions)

---

## 1. Сервисы Docker-Compose

| Сервис       | Назначение               | Порт   |
| ------------ | ------------------------ | ------ |
| **db**       | PostgreSQL               | 5432   |
| **redis**    | Redis                    | 6379   |
| **minio**    | S3-хранилище (MinIO)     | 9000   |
| **backend**  | Flask-REST API           | 8000   |
| **bot**      | Telegram-бот             | –      |
| **frontend** | Vue.js SPA               | –      |
| **proxy**    | Nginx + SSL              | 80,443 |

### Архитектурная схема

* Микросервисная топология: схема взаимодействия контейнеров в Docker Compose.
* Data flow: последовательность запросов от SPA → Nginx → Backend → DB/Redis/MinIO.

### Технологический стек

| Компонент             | Технология              | Версия         |
|-----------------------| ----------------------- | -------------- |
| Язык программирования | Python                  | 3.11           |
| Веб-фреймворк         | Flask                   | 3.1.1          |
| CORS                  | flask-cors              | 6.0.1          |
| WSGI-сервер           | Gunicorn                | 23.0.0         |
| ORM                   | Flask-SQLAlchemy        | 3.1.1          |
| Драйвер PostgreSQL    | psycopg2-binary         | 2.9.10         |
| Миграции              | Flask-Migrate / Alembic | 4.1.0 / 1.16.2 |
| Клиент Redis          | redis-py                | 6.2.0          |
| Клиент MinIO          | minio                   | 7.2.15         |
| HTTP-клиент           | requests                | 2.32.4         |
| Retry-логика          | tenacity                | 9.1.2          |
| JWT-аутентификация    | Flask-JWT-Extended      | 4.7.1          |
| Telegram-бот          | aiogram                 | 3.10.0         |
| База данных           | PostgreSQL              | 17             |
| Кэш и сессии          | Redis                   | 7              |
| Объектное хранилище   | MinIO                   | latest         |
| Reverse proxy         | Nginx                   | 1.25.x         |
| Рантайм фронтенда     | Node.js                 | 20.x           |
| SPA-фреймворк         | Vue.js                  | 3.5.17         |
| Маршрутизация         | Vue Router              | 4.5.1          |
| State management      | Pinia                   | 3.0.3          |
| HTTP-клиент (фронт)   | Axios                   | 1.10.0         |
| Сборщик               | Vite                    | 7.0.0          |
| Плагин Vue для Vite   | @vitejs/plugin-vue      | 6.0.0          |
| CSS-препроцессор      | Sass                    | 1.89.2         |
| Статический сервер    | serve                   | 14.2.4         |


---

## 2. Переменные окружения

| Переменная                                                             | Описание                                |
| ---------------------------------------------------------------------- | --------------------------------------- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`              | Параметры подключения к PostgreSQL      |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`                           | Параметры подключения к Redis           |
| `MINIO_HOST`, `MINIO_BUCKET`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` | Конфиг MinIO S3                         |
| `SECRET_KEY`                                                           | Секретный JWT-ключ                      |
| `BOT_TOKEN`                                                            | Токен Telegram-бота                     |
| `BACKEND_URL`                                                          | Базовый URL API и ссылок на изображения |

---

## 3. Справочник API

Базовый URL: `https://shop.yourdomain.com/api`

### /api/general

| Endpoint                    | Method | Description                        |
|-----------------------------|--------|------------------------------------|
| `/general/`                 | GET    | Health check                       |
| `/general/save_user`        | POST   | Сохранить/обновить TG-пользователя |
| `/general/get_user_profile` | GET    | Получить данные профиля            |
| `/general/update_profile`   | PUT    | обновить данные профиля            |
| `/general/get_parameters`   | GET    | получить публичные настройки       |
| `/general/list_reviews`     | GET    | получить список отзывов            |
| `/general/create_request`   | POST   | отправить заявку на поиск товара   |
| `/general/get_user_orders`  | GET    | получить список заказов            |
| `/general/get_user_order`   | GET    | получить детали заказа             |
| `/general/list_addresses`   | GET    | получить список адресов            |
| `/general/add_address`      | POST   | добавить адрес                     |
| `/general/update_address`   | PUT    | обновить данные дареса             |
| `/general/delete_address`   | DELETE | удалить адрес                      |

### /api/product

| Endpoint                  | Method | Description                   |
| ------------------------- | ------ | ----------------------------- |
| `/product/list_products`  | GET    | Список товаров по категории   |
| `/product/get_product`    | GET    | Детали товара по variant\_sku |
| `/product/get_cart`       | GET    | Загрузка корзины (из Redis)   |
| `/product/save_cart`      | POST   | Сохранение корзины            |
| `/product/get_favorites`  | GET    | Избранное (загрузка)          |
| `/product/save_favorites` | POST   | Избранное (сохранение)        |

### /api/auth

| Endpoint                          | Method | Description                   |
|-----------------------------------| ------ |-------------------------------|
| `/auth/request_registration_code` | POST   | Регистрация: запрос кода      |
| `/auth/verify_registration_code`  | POST   | Регистрация: верификация кода |
| `/auth/request_login_code`        | POST   | Авторизация: запрос кода      |
| `/auth/verify_login_code`         | POST   | Авторизация: верификация кода |

### /api/admin

| Endpoint                  | Method | Description                           |
|---------------------------| ------ |---------------------------------------|
| `/admin/set_user_role`    | GET    | Установить пользователю роль          |
| `/admin/get_daily_visits` | GET    | Статистика посещений по часам (Redis) |
| `/admin/get_logs`         | GET    | Логи изменений (Postgres)             |
| `/admin/sync_all`         | POST   | Проверка и загрузка Sheets и ZIP      |
| `/admin/get_settings`     | GET    | Список настроек                       |
| `/admin/update_setting`   | POST   | Изменение настроек                    |
| `/admin/delete_setting`   | DELETE | Удаление настроек                     |
| `/admin/create_review`    | POST   | Создание отзыва                       |
| `/admin/delete_review`    | DELETE | Удаление отзыва                       |
| `/admin/list_requests`    | GET    | Список заявок на поиск товара         |
| `/admin/delete_request`   | DELETE | Удаление заявки на поиск товара       |
| `/admin/list_users`       | GET    | Список пользователей                  |

---

## 4. Быстрый старт

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
docker login --username <your-username>
```

---

### 2. Клон и конфигурация

```bash
mkdir -p ~/app && cd ~/app
rm -rf yanda_shop
git clone https://<TOKEN>@github.com/wi1ex/yanda_shop.git
cd yanda_shop
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'

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

### 4. Запуск

```bash
# npm install локально для обновления package-lock.json
# Запись домена (помимо .env) в store.js, nginx.conf и BotFather

# Обновляем код
cd /root/app/yanda_shop
git fetch --all
git reset --hard origin/main

# Останавливаем прежние контейнеры и чистим ненужное
docker-compose down
docker network prune --filter "until=24h" --force
docker container prune --filter "until=24h" --force
docker image prune --all --filter "until=24h" --force
docker builder prune --all --filter "until=24h" --force

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

*Миграции:*

```bash
docker-compose up -d db backend
docker-compose exec backend flask db init
docker-compose exec backend flask db migrate -m "initial schema"
docker-compose exec backend flask db upgrade
docker-compose up -d
```


*MinIO и Redis:*

```bash
# если mc ещё не установлена, на сервере:
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
# затем прописать алиас к вашему MinIO
./mc alias set myminio http://127.0.0.1:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
# Установить anonymous-политику для бакета
./mc anonymous set download myminio/images

# Включить vm.overcommit_memory для Redis
# Создадим конфиг для sysctl
echo "vm.overcommit_memory = 1" | sudo tee /etc/sysctl.d/99-redis-overcommit.conf
# Применим сразу, без перезагрузки
sudo sysctl --system
```

---

## 5. Скрипты

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

## 6. Автодеплой проекта на сервер с помощью GitHub Actions

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
    env:
      BACKEND_URL: ${{ secrets.BACKEND_URL }}
      # etc.

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Write SSH key and known_hosts
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          echo "${{ secrets.SSH_KNOWN_HOSTS }}" > ~/.ssh/known_hosts
          chmod 600 ~/.ssh/known_hosts
        shell: bash

      - name: Create .env from Secrets
        run: |
          cat > .env <<EOF
          BACKEND_URL=${BACKEND_URL}
          # etc.
          EOF
        shell: bash

      - name: Copy .env to server
        run: |
          scp -i ~/.ssh/deploy_key \
            -o StrictHostKeyChecking=yes \
            ./.env \
            "${{ secrets.SERVER_USER }}"@"${{ secrets.SERVER_HOST }}":/root/app/yanda_shop/.env
        shell: bash

      - name: Deploy via SSH
        run: |
          ssh -i ~/.ssh/deploy_key \
              -o StrictHostKeyChecking=yes \
              -l "${{ secrets.SERVER_USER }}" \
              "${{ secrets.SERVER_HOST }}" << 'EOF'
            set -euo pipefail
            # all scripts..
          EOF
        shell: bash
```

После успешной настройки **удалите** из папки `/root/app/yanda_shop` все временные артефакты:

```bash
cd /root/app/yanda_shop
rm -f github_deploy_key github_deploy_key.pub known_hosts.txt
```
