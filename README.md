# 📋 TaskManager - Система управления задачами

Полноценный веб-сервис для управления задачами с интеграцией Telegram-бота, графиками и аналитикой.

## 🎯 Описание проекта

TaskManager - это современное веб-приложение для планирования и отслеживания задач, которое включает:
- 🌐 Веб-интерфейс на FastAPI + Bootstrap
- 📱 Telegram-бот для быстрого управления задачами
- 📊 Графики и статистика (Chart.js + Matplotlib)
- 🔐 JWT авторизация
- 🏷️ Категории, теги и фильтры
- ⏰ Дедлайны и приоритеты

## 🏗️ Архитектура проекта

```
task-manager/
├── backend/
│   ├── database.py       # SQLAlchemy модели (User, Task, Comment)
│   ├── crud.py           # CRUD операции с БД
│   ├── auth.py           # JWT авторизация
│   ├── models.py         # Pydantic схемы для API
│   ├── main.py           # FastAPI приложение
│   ├── bot.py            # Telegram бот (aiogram)
│   └── charts.py         # Matplotlib графики
│
├── frontend/
│   ├── static/
│   │   └── css/style.css
│   └── templates/
│       ├── index.html       # Главная страница
│       ├── login.html       # Вход/Регистрация
│       ├── dashboard.html   # Дашборд с графиками
│       └── tasks.html       # Управление задачами
│
├── .env                  # Переменные окружения
├── requirements.txt      # Зависимости
├── tasks.db             # SQLite база данных
└── README.md
```

## 📦 Технологический стек

### Backend:
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **Aiogram 3** - Telegram Bot API
- **JWT** (python-jose) - авторизация
- **Matplotlib** - генерация графиков
- **Uvicorn** - ASGI сервер

### Frontend:
- **Bootstrap 5** - UI фреймворк
- **Chart.js** - интерактивные графики
- **Vanilla JavaScript** - логика фронтенда

### База данных:
- **SQLite** - для разработки
- **PostgreSQL** - для production (опционально)

## 🚀 Установка и запуск

### 1. Клонирование проекта

```bash
git clone <your-repo>
cd task-manager
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка .env файла

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token_here
SECRET_KEY=your-secret-key-for-jwt
```

**Как получить BOT_TOKEN:**
1. Откройте Telegram
2. Найдите @BotFather
3. Отправьте `/newbot`
4. Следуйте инструкциям
5. Скопируйте токен в `.env`

### 4. Запуск Telegram-бота

```bash
cd backend
python bot.py
```

Бот будет доступен в Telegram!

### 5. Запуск веб-сервера

В новом терминале:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Веб-интерфейс доступен по адресу: `http://localhost:8000`

## 📱 Использование Telegram-бота

### Команды бота:

- `/start` - Начать работу и зарегистрироваться
- `/add` - Добавить новую задачу (пошагово)
- `/list` - Показать все задачи
- `/pending` - Активные задачи
- `/completed` - Выполненные задачи
- `/stats` - Текстовая статистика
- `/charts` - Графики статистики (Matplotlib)
- `/help` - Справка по командам

### Пример использования:

```
Вы: /add
Бот: Введите название задачи
Вы: Купить молоко
Бот: Введите описание (или - для пропуска)
Вы: В магазине на углу
Бот: Выберите приоритет:
     [🔴 Высокий] [🟡 Средний] [🟢 Низкий]
Вы: *нажимаете 🟡*
Бот: ✅ Задача #1 создана!
```

## 🌐 Веб-интерфейс

### Страницы:

1. **Главная** (`/`) - Лендинг с описанием
2. **Вход/Регистрация** (`/login`) - Авторизация
3. **Дашборд** (`/dashboard`) - Статистика и графики
4. **Задачи** (`/tasks`) - Управление задачами

### Возможности веб-версии:

- ✅ Создание, редактирование, удаление задач
- 🏷️ Категории и теги
- 🔍 Фильтрация по статусу, приоритету, категории
- 📊 Интерактивные графики (Chart.js)
- ⏰ Установка дедлайнов
- 💬 Комментарии к задачам (опционально)

## 🔐 Авторизация

### Регистрация:
1. Перейдите на `/login`
2. Выберите вкладку "Регистрация"
3. Заполните форму (email, пароль, имя)
4. Опционально: укажите Telegram ID для синхронизации

### Вход:
1. Введите email и пароль
2. Получите JWT токен
3. Токен сохраняется в localStorage

### Связка с Telegram:
При регистрации можно указать Telegram ID (узнать: @userinfobot), чтобы задачи синхронизировались между ботом и веб-версией.

## 📊 Графики и статистика

### В Telegram (Matplotlib):
Команда `/charts` генерирует PNG с 4 графиками:
- Круговая диаграмма статусов
- Столбчатая диаграмма приоритетов
- Линейный график продуктивности
- Топ категорий

### В веб-интерфейсе (Chart.js):
Интерактивные графики на дашборде:
- Статус задач (doughnut)
- Продуктивность за неделю (line)
- Задачи по категориям (bar)
- Обновление в реальном времени

## 🗄️ Структура базы данных

### Таблица `users`:
```sql
- telegram_id (INT, PRIMARY KEY)
- username (VARCHAR)
- first_name (VARCHAR)
- created_at (DATETIME)
```

### Таблица `web_users`:
```sql
- id (INT, PRIMARY KEY)
- email (VARCHAR, UNIQUE)
- password_hash (VARCHAR)
- first_name (VARCHAR)
- telegram_id (INT, UNIQUE, NULLABLE)
- created_at (DATETIME)
```

### Таблица `tasks`:
```sql
- id (INT, PRIMARY KEY)
- telegram_id (INT)
- title (VARCHAR)
- description (TEXT)
- priority (ENUM: низкий, средний, высокий)
- status (ENUM: в процессе, выполнено, отменено)
- category (VARCHAR)
- tags (VARCHAR)
- deadline (DATETIME)
- created_at (DATETIME)
- completed_at (DATETIME)
```

### Таблица `comments`:
```sql
- id (INT, PRIMARY KEY)
- task_id (INT)
- telegram_id (INT)
- text (TEXT)
- created_at (DATETIME)
```

## 🔧 API Endpoints

### Авторизация:
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход (получение токена)
- `GET /api/auth/me` - Информация о пользователе

### Задачи:
- `GET /api/tasks` - Список всех задач
- `POST /api/tasks` - Создать задачу
- `GET /api/tasks/{id}` - Получить задачу
- `PATCH /api/tasks/{id}/complete` - Отметить выполненной
- `DELETE /api/tasks/{id}` - Удалить задачу

### Статистика:
- `GET /api/statistics` - Полная статистика с графиками

## 🎓 Соответствие критериям проекта

### Этап 1 (30%): ✅ ВЫПОЛНЕНО
- ✅ Консольное приложение (Telegram бот)
- ✅ Базовые операции: добавить/удалить/отметить
- ✅ Хранение в БД (SQLite)
- ✅ Работа с типами данных, функции

### Этап 2 (60%): ✅ ВЫПОЛНЕНО
- ✅ Веб-приложение (FastAPI)
- ✅ ООП модели (Task, User, Comment)
- ✅ CRUD через веб-интерфейс
- ✅ Продвинутый модуль: Telegram API интеграция

### Этап 3 (100%): ✅ ВЫПОЛНЕНО
- ✅ Категории, теги, фильтры
- ✅ Визуализация (Chart.js + Matplotlib)
- ✅ Комментарии к задачам
- ✅ JWT авторизация
- ✅ Красивый фронтенд (Bootstrap)
- ✅ Готовность к deploy

## 🚀 Deploy (Production)

### Вариант 1: Railway.app

1. Создайте аккаунт на railway.app
2. Подключите GitHub репозиторий
3. Настройте переменные окружения
4. Deploy автоматически!

### Вариант 2: Render.com

1. Создайте Web Service
2. Укажите команду: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. Добавьте переменные окружения
4. Deploy!

### Вариант 3: VPS (DigitalOcean, AWS, etc.)

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите с помощью gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Или используйте Docker
docker build -t taskmanager .
docker run -p 8000:8000 taskmanager
```

## 📝 TODO (Улучшения)

- [ ] Email уведомления о дедлайнах
- [ ] Экспорт задач в PDF/Excel
- [ ] Telegram Web App (веб внутри бота)
- [ ] Повторяющиеся задачи (cron)
- [ ] Совместные задачи (несколько пользователей)
- [ ] Прикрепление файлов к задачам
- [ ] Темная тема
- [ ] Mobile приложение
