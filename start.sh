#!/bin/bash

echo "🚀 Запуск TaskManager..."
echo ""

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt --quiet

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте файл .env с токеном бота:"
    echo "BOT_TOKEN=your_token_here"
    echo "SECRET_KEY=your_secret_key_here"
    exit 1
fi

echo ""
echo "✅ Подготовка завершена!"
echo ""
echo "Выберите режим запуска:"
echo "1) Только Telegram-бот"
echo "2) Только Web-сервер"
echo "3) Оба сервиса (рекомендуется)"
echo ""
read -p "Введите номер (1-3): " choice

case $choice in
    1)
        echo "🤖 Запуск Telegram-бота..."
        cd backend
        python bot.py
        ;;
    2)
        echo "🌐 Запуск Web-сервера..."
        cd backend
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ;;
    3)
        echo "🚀 Запуск обоих сервисов..."
        echo "📱 Telegram-бот будет в фоне"
        echo "🌐 Web-сервер на http://localhost:8000"
        echo ""
        cd backend
        python bot.py &
        BOT_PID=$!
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        
        # При завершении убиваем бота
        trap "kill $BOT_PID" EXIT
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac
