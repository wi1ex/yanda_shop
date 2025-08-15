# Yanda Shop (Flask + Vue 3 + PostgreSQL/Redis/MinIO)

Проект «под ключ»: публичный REST API, SPA-фронтенд, админ-инструменты, импорты из Google Sheets, собственная объектная медиа-витрина на MinIO, Redis-кэш и счётчики, e-mail-аутентификация, интеграция Telegram Mini App, резервное копирование и автодеплой.

---

## Оглавление

1. [О проекте](#о-проекте)
2. [Возможности для пользователей](#ключевые-возможности-для-пользователей)
3. [Админ-возможности и импорт контента](#админ-возможности-и-импорт-контента)
4. [Технологический стек](#технологический-стек)
5. [Инфраструктура, CI/CD и бэкапы](#инфраструктура-cicd-и-бэкапы)
6. [Структура репозитория](#структура-репозитория)

---

## О проекте

* **Backend (Flask)**

  * Архитектура приложения (`create_app`, Blueprints `general/product/auth/admin`), расширения и инициализация (`SQLAlchemy`, `JWT`, `Flask-Mail`, `Redis`, `MinIO`).
  * **JWT-аутентификация по коду e-mail**: генерация кода, TTL 10 мин, повторный запрос — с кулдауном по e-mail и IP в Redis.
  * Профили, адреса, заказы, отзывы, список желаемого, корзина в Redis, сериализация товаров.
  * Кэширование параметров и опций доставки в Redis; сервисные валидаторы и нормализация данных.
  * Объектное хранилище MinIO: загрузка/очистка/синхронизация медиа, безопасные имена файлов.
  * Логирование изменений (ChangeLog), учёт посещений по часам в Redis (total/unique).
  * Импорт из Google Sheets: разбор, валидация, нормализация, сопоставление с моделями и загрузка в БД/MinIO.

* **Frontend (Vue 3 + Vite)**

  * SPA с роутингом, Pinia-хранилищами (`user`, `cart`, `product`, `admin`, `global`), модульным SCSS.
  * Интерфейс каталога (категории/подкатегории/сортировка/пагинация), карточка товара, поиск/заявка с загрузкой файла, корзина/избранное, профиль, заказы и адреса.
  * **Auth-модалка с одноразовым кодом**, счётчиком повторной отправки, **тихий refresh** access-токена в axios-интерцепторе.
  * Админ-страница: синхронизации, заказы/статусы, пользователи, заявки, настройки, просмотр логов и посещаемости.

* **Интеграции**

  * **Telegram-бот** на `aiogram` (стартовые сценарии + связка с backend).
  * **SMTP e-mail** через `Flask-Mail` и **самостоятельно развёрнутую почтовую подсистему** (Docker Mailserver + RainLoop веб-клиент) — для отправки кодов входа и сервисных писем.

* **Инфраструктура и эксплуатация**

  * **Docker Compose** для всех сервисов: PostgreSQL, Redis, MinIO, Backend (Gunicorn), Frontend (Vite build), Nginx (reverse proxy, security headers), Mailserver, Webmail.
  * **Nginx** с HSTS, X-Frame-Options, Referrer-Policy и шаблонной CSP; SPA-роутинг и проксирование API.
  * **Миграции БД (Alembic)** и сервисные скрипты **резервного копирования/восстановления** PostgreSQL/Redis/MinIO (с блокировками и checksum).
  * **Автодеплой из GitHub Actions** (секреты через `secrets.*`, деплой без хранения приватных данных в репозитории).

---

## Возможности для пользователей

* **Каталог и карточки**: категории/подкатегории, фильтры и сортировки, пагинация, вариации (SKU), медиагалереи из MinIO.
* **Корзина/избранное**: хранение в Redis, быстрая синхронизация с клиентом.
* **Оформление заказа**: REST-создание, статусы, расчёт итогов и доставки.
* **Профиль**: данные, загрузка/удаление аватара, адреса доставки, список заказов.
* **Отзывы и заявки**: публикация отзывов; форма «найти товар», загрузка изображения (проверка размера).

---

## Админ-возможности и импорт контента

* **Импорт из Google Sheets**
  Разбор строк, **валидации** (SKU, gender/category/subcategory, длины и типы), нормализация, сопоставление с типами товаров `Shoe/Clothing/Accessory`, загрузка и обновление записей в БД.
  Контроль консистентности наборов изображений, карта русских → англ. подкатегорий, поиск дубликатов SKU.

* **Медиа-менеджмент в MinIO**
  Загрузка/очистка/синхронизация, удаление «осиротевших» объектов, проверка соответствий.

* **Операции админа (REST)**
  Пользователи/роли, заказы (получение/статусы/отмена/удаление), заявки, отзывы, настройки, **логи изменений** и **почасовая посещаемость** из Redis.

---

## Технологический стек

**Backend:** Python 3, Flask, SQLAlchemy, Alembic (Flask-Migrate), Gunicorn, Flask-JWT-Extended, Flask-Mail, requests, tenacity
**Storage:** PostgreSQL, Redis, MinIO (S3-совместимое хранилище)
**Frontend:** Vue 3, Vite, Pinia, Vue Router, Axios, SCSS
**Proxy:** Nginx
**Инфра:** Docker / Docker Compose, GitHub Actions

> Конкретные версии — в `backend/requirements.txt` и `frontend/package.json`.

---

## Инфраструктура, CI/CD и бэкапы

* **Docker Compose**: изоляция сервисов и **именованные volumes** для персистентности (БД/Redis/MinIO/почта).
* **Nginx**: единая точка входа для SPA и API (reverse proxy), TLS/заголовки безопасности, SPA history-fallback.
* **Mail-стек (опционально)**: Docker Mailserver (готовность к DKIM/SpamAssassin/ClamAV/Postgrey) + RainLoop webmail.
* **CI/CD (GitHub Actions)**: деплой по push в `main`, секреты через `secrets.*`, без утечки конфиденциальных данных в репозиторий; выборочная пересборка сервисов (backend/frontend) по изменившимся путям.
* **Бэкапы (`scripts/backup_all.sh`)**: PostgreSQL (dump + sha256), Redis (RDB snapshot), MinIO (mirror + архив).
* **Восстановление (`scripts/restore_all.sh`)**: пошаговый restore с проверками checksum; блокировки, чтобы избежать гонок.

---

## Структура репозитория

```
backend/                         # Flask API
  app.py                         # точка входа (Gunicorn: app:app)
  Dockerfile
  requirements.txt
  migrations/                    # Alembic миграции
  shop/
    __init__.py                  # create_app(), регистрация blueprints, JWT, CORS
    core/
      config.py                  # конфиг из env
      logging.py                 # настройка логера
    extensions.py                # Redis / MinIO / Mail + ensure_bucket_exists()
    models.py                    # Users, Orders, Reviews, Settings, BaseProduct→Shoe/Clothing/Accessory
    routes/
      general.py                 # профиль, заказы, заявки, параметры, отзывы, upload
      product.py                 # каталог, карточка, корзина, избранное
      auth.py                    # email-код, verify, refresh (JWT)
      admin.py                   # операции админа: синхронизации, заказы, пользователи, настройки, логи, визиты
    utils/
      route_utils.py             # валидация args/json, универсальный error handler
      db_utils.py                # session_scope(), агрегаты по пользователю
      cache_utils.py             # кэш параметров/доставки в Redis
      product_serializer.py      # сериализация товаров и ссылок на медиа
      google_sheets.py           # парсинг и валидация строк, маппинги категорий/подкатегорий
      validators.py              # набор строгих валидаторов
      storage_utils.py           # работа с MinIO (upload/cleanup/sync), ZIP/CSV
      logging_utils.py           # ChangeLog writer
      redis_utils.py             # счётчики посещений (total/unique)
frontend/                        # Vue 3 + Vite SPA
  vite.config.mjs
  index.html
  src/
    main.js
    App.vue
    assets/                      # иконки, изображения
    styles/                      # SCSS-модули, переменные
    components/                  # Header, Footer, Cart, Auth, Search ...
    views/                       # Home, Catalog, Product, Checkout, Profile, Admin, ...
    store/
      apiRoutes.js               # маршруты API
      *.js                       # pinia-модули: user/cart/product/admin/global
    services/
      api.js                     # axios + silent refresh
nginx/
  Dockerfile
  nginx.conf                     # reverse proxy, security headers, SPA routing
bot/
  bot.py                         # aiogram: /start и базовые сценарии
  Dockerfile
scripts/                         # эксплуатационные утилиты
  backup_all.sh
  restore_all.sh
.github/workflows/
  deploy.yml                     # CI/CD деплой (секреты: secrets.*)
docker-compose.yml               # все сервисы
.env.example                     # пример env (без секретов)
LICENSE
README.md
```

---
