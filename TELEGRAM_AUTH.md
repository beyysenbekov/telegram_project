# 🔐 АВТОМАТИЧЕСКИЙ ВХОД ЧЕРЕЗ TELEGRAM

## Что добавлено:

1. ✅ Кнопка "Войти через Telegram" на главной и странице входа
2. ✅ Автоматическая регистрация при первом входе
3. ✅ JWT токен создается автоматически
4. ✅ Не нужен email и пароль!

---

## 📋 Настройка (ОБЯЗАТЕЛЬНО):

### Шаг 1: Настрой Telegram Login Widget у @BotFather

1. Открой Telegram
2. Найди **@BotFather**
3. Отправь команду: `/setdomain`
4. Выбери своего бота
5. Введи домен:
   - Для ngrok: `abc123.ngrok-free.app` (БЕЗ https://)
   - Для Railway: `your-app.railway.app`
   - Для localhost: `localhost` (только для теста!)

**Пример:**
```
Вы: /setdomain
BotFather: Choose a bot
Вы: @YourBot
BotFather: OK. Send me the new domain
Вы: abc123.ngrok-free.app
BotFather: Success! Domain updated.
```

---

### Шаг 2: Обнови telegram-login.html

Открой `frontend/templates/telegram-login.html` и найди строку:

```javascript
const botUsername = 'YOUR_BOT_USERNAME'; // <-- ИЗМЕНИ ЭТО!
```

**Замени на username ТВОЕГО бота (БЕЗ @):**

```javascript
const botUsername = 'mytaskmanager_bot'; // Например
```

**Где взять username:**
- Открой бота в Telegram
- Username это то что после @ (например: @mytaskmanager_bot → `mytaskmanager_bot`)

---

### Шаг 3: Перезапусти сервер

```bash
cd backend
# Останови (Ctrl+C)
# Запусти снова:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🚀 Как это работает:

### Сценарий 1: Вход через веб-сайт

1. Пользователь открывает http://localhost:8000
2. Нажимает "Войти через Telegram"
3. Видит синюю кнопку Telegram Login Widget
4. Нажимает → Telegram спрашивает разрешение
5. Подтверждает → автоматически создается аккаунт
6. Получает JWT токен → перенаправляется в дашборд

### Сценарий 2: Прямая ссылка из бота

Можно добавить команду в бота:

```python
@dp.message(Command("web"))
async def cmd_web(message: Message):
    """Открыть веб-версию"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    
    # Формируем URL с параметрами для автоматического входа
    url = f"https://your-domain.com/telegram-login?id={user_id}&first_name={first_name}&username={username}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть сайт", url=url)]
    ])
    
    await message.answer(
        "Нажми кнопку для входа на сайт через Telegram:",
        reply_markup=keyboard
    )
```

---

## 🎯 Что происходит при входе:

1. **Проверка:** Существует ли пользователь с таким `telegram_id`?
   
2. **Если НЕТ:**
   - Создается новый `WebUser`:
     ```python
     email = f"tg{telegram_id}@telegram.user"  # tg123456@telegram.user
     password = telegram_id (хешируется)
     telegram_id = твой ID
     first_name = твое имя из Telegram
     ```
   
3. **Если ДА:**
   - Просто входит

4. **Создается JWT токен** → Пользователь авторизован!

---

## 📊 Структура базы данных:

```sql
WebUsers:
┌────┬─────────────────────────┬──────────┬────────────┬─────────────┐
│ id │ email                   │ password │ first_name │ telegram_id │
├────┼─────────────────────────┼──────────┼────────────┼─────────────┤
│ 1  │ user@example.com        │ hashed   │ John       │ NULL        │  <- Обычная регистрация
│ 2  │ tg123456@telegram.user  │ hashed   │ Alice      │ 123456      │  <- Вход через Telegram
│ 3  │ tg789012@telegram.user  │ hashed   │ Bob        │ 789012      │  <- Вход через Telegram
└────┴─────────────────────────┴──────────┴────────────┴─────────────┘
```

---

## ✨ Преимущества:

✅ **Быстрый вход** - 1 клик вместо формы
✅ **Безопасно** - авторизация через Telegram API
✅ **Удобно** - не нужно запоминать пароль
✅ **Автоматически** - регистрация при первом входе
✅ **Синхронизация** - одна учетная запись для бота и сайта

---

## 🎓 Для презентации:

Покажи преподавателю:

1. **Обычный вход** (email + пароль)
2. **Вход через Telegram** (1 клик!)
3. **Автоматическая регистрация** - новый пользователь создается сам

**Это современный подход!** OAuth-подобная авторизация через мессенджер.

---

## 🐛 Возможные проблемы:

### Ошибка: "Bot domain invalid"

**Решение:**
1. Проверь что домен добавлен в @BotFather через `/setdomain`
2. Домен должен совпадать с тем, где открыта страница

### Кнопка Telegram не появляется

**Решение:**
1. Проверь что в `telegram-login.html` указан правильный `botUsername`
2. Проверь консоль браузера (F12) на ошибки

### "Не удалось получить Telegram ID"

**Решение:**
Telegram Login Widget работает только на настоящем домене (не localhost).
Используй ngrok для теста.

---

## 🔒 Безопасность:

- Telegram гарантирует подлинность данных через хеш
- JWT токен хранится в localStorage
- Пароль хешируется (bcrypt)
- Защита от подделки telegram_id

---

## 📝 API эндпоинты:

```
POST /api/auth/telegram-login
Body: {
  "telegram_id": 123456,
  "first_name": "John",
  "username": "john_doe"
}

Response: {
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "email": "tg123456@telegram.user",
    "first_name": "John",
    "telegram_id": 123456
  }
}
```

---

**🚀 Готово! Современная авторизация через Telegram!**
