import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from datetime import datetime

# Импорт наших функций
from crud import (
    create_user, get_user_tasks, create_task,
    complete_task, delete_task, get_statistics, get_task
)
from database import Priority, Status

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Состояния для создания задачи
class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_priority = State()


# ========== КОМАНДЫ ==========

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработка команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Создаём или получаем пользователя
    create_user(user_id, username, first_name)

    # Кнопка для открытия веб-интерфейса
    from aiogram.types import WebAppInfo
    
    # ВАЖНО: Замени URL на свой (ngrok или railway)
    WEB_APP_URL = "https://shredder-confined-pester.ngrok-free.dev"  # <-- ИЗМЕНИ ЭТО!
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌐 Открыть веб-интерфейс",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ])

    await message.answer(
        f"👋 Привет, {first_name}!\n\n"
        f"Я бот-планировщик задач. Помогу тебе организовать дела!\n\n"
        f"🌐 Нажми кнопку ниже для открытия веб-интерфейса\n"
        f"💬 Или используй команды:\n\n"
        f"📋 Доступные команды:\n"
        f"/add - Добавить новую задачу\n"
        f"/list - Показать все задачи\n"
        f"/stats - Моя статистика\n"
        f"/charts - Графики\n"
        f"/help - Помощь",
        reply_markup=keyboard
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь"""
    await message.answer(
        "📖 <b>Справка по командам:</b>\n\n"
        "/add - Добавить задачу (шаг за шагом)\n"
        "/list - Список всех задач\n"
        "/stats - Статистика выполнения\n"
        "/pending - Только активные задачи\n"
        "/completed - Только выполненные\n\n"
        "Используй кнопки под задачами для управления!",
        parse_mode="HTML"
    )


# ========== ДОБАВЛЕНИЕ ЗАДАЧИ ==========

@dp.message(Command("add"))
async def cmd_add_task(message: Message, state: FSMContext):
    """Начать создание задачи"""
    await state.set_state(TaskStates.waiting_for_title)
    await message.answer(
        "📝 <b>Создание новой задачи</b>\n\n"
        "Шаг 1/3: Введи название задачи:",
        parse_mode="HTML"
    )


@dp.message(TaskStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    """Получение названия"""
    await state.update_data(title=message.text)
    await state.set_state(TaskStates.waiting_for_description)

    await message.answer(
        "📝 Шаг 2/3: Введи описание задачи\n"
        "(или отправь '-' чтобы пропустить):"
    )


@dp.message(TaskStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Получение описания"""
    description = None if message.text == '-' else message.text
    await state.update_data(description=description)
    await state.set_state(TaskStates.waiting_for_priority)

    # Кнопки выбора приоритета
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Высокий", callback_data="priority_high"),
            InlineKeyboardButton(text="🟡 Средний", callback_data="priority_medium"),
            InlineKeyboardButton(text="🟢 Низкий", callback_data="priority_low")
        ]
    ])

    await message.answer(
        "📝 Шаг 3/3: Выбери приоритет:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("priority_"))
async def process_priority(callback: CallbackQuery, state: FSMContext):
    """Получение приоритета и создание задачи"""
    priority_map = {
        "priority_high": Priority.HIGH.value,
        "priority_medium": Priority.MEDIUM.value,
        "priority_low": Priority.LOW.value
    }

    priority = priority_map[callback.data]
    data = await state.get_data()

    # Создаём задачу
    task_id = create_task(
        telegram_id=callback.from_user.id,
        title=data['title'],
        description=data.get('description'),
        priority=priority
    )

    await state.clear()

    priority_emoji = {"высокий": "🔴", "средний": "🟡", "низкий": "🟢"}

    await callback.message.edit_text(
        f"✅ <b>Задача #{task_id} создана!</b>\n\n"
        f"📌 {data['title']}\n"
        f"{priority_emoji[priority]} Приоритет: {priority}",
        parse_mode="HTML"
    )

    await callback.answer()


# ========== ПРОСМОТР ЗАДАЧ ==========

@dp.message(Command("list"))
async def cmd_list_tasks(message: Message):
    """Показать все задачи"""
    tasks = get_user_tasks(message.from_user.id)

    if not tasks:
        await message.answer("📭 У тебя пока нет задач!\n\nИспользуй /add чтобы создать первую.")
        return

    await send_tasks_list(message, tasks, "📋 Все твои задачи:")


@dp.message(Command("pending"))
async def cmd_pending_tasks(message: Message):
    """Показать активные задачи"""
    tasks = get_user_tasks(message.from_user.id, status=Status.PENDING.value)

    if not tasks:
        await message.answer("✨ Нет активных задач! Ты всё сделал!")
        return

    await send_tasks_list(message, tasks, "⏳ Активные задачи:")


@dp.message(Command("completed"))
async def cmd_completed_tasks(message: Message):
    """Показать выполненные задачи"""
    tasks = get_user_tasks(message.from_user.id, status=Status.COMPLETED.value)

    if not tasks:
        await message.answer("Пока нет выполненных задач.")
        return

    await send_tasks_list(message, tasks, "✅ Выполненные задачи:")


async def send_tasks_list(message: Message, tasks: list, header: str):
    """Отправить список задач с кнопками"""
    priority_emoji = {"высокий": "🔴", "средний": "🟡", "низкий": "🟢"}
    status_emoji = {"в процессе": "⏳", "выполнено": "✅", "отменено": "❌"}

    for task in tasks[:10]:  # Показываем по 10 задач
        text = (
            f"{status_emoji.get(task['status'], '❓')} <b>Задача #{task['id']}</b>\n\n"
            f"📌 {task['title']}\n"
        )

        if task['description']:
            text += f"📝 {task['description']}\n"

        text += f"{priority_emoji.get(task['priority'], '⚪')} Приоритет: {task['priority']}\n"
        text += f"🗓 Создана: {task['created_at'].strftime('%d.%m.%Y %H:%M')}"

        # Кнопки управления
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        if task['status'] == Status.PENDING.value:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="✅ Выполнено", callback_data=f"complete_{task['id']}"),
                InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task['id']}")
            ])
        else:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task['id']}")
            ])

        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    if len(tasks) > 10:
        await message.answer(f"... и ещё {len(tasks) - 10} задач")


# ========== УПРАВЛЕНИЕ ЗАДАЧАМИ ==========

@dp.callback_query(F.data.startswith("complete_"))
async def callback_complete_task(callback: CallbackQuery):
    """Отметить задачу выполненной"""
    task_id = int(callback.data.split('_')[1])

    success = complete_task(task_id, callback.from_user.id)

    if success:
        await callback.message.edit_text(
            f"✅ <b>Задача #{task_id} выполнена!</b>\n\n"
            f"Отличная работа! 🎉",
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Ошибка: задача не найдена", show_alert=True)

    await callback.answer()


@dp.callback_query(F.data.startswith("delete_"))
async def callback_delete_task(callback: CallbackQuery):
    """Удалить задачу"""
    task_id = int(callback.data.split('_')[1])

    success = delete_task(task_id, callback.from_user.id)

    if success:
        await callback.message.edit_text(
            f"🗑 Задача #{task_id} удалена"
        )
    else:
        await callback.answer("❌ Ошибка: задача не найдена", show_alert=True)

    await callback.answer()


# ========== СТАТИСТИКА ==========

@dp.message(Command("stats"))
async def cmd_statistics(message: Message):
    """Показать статистику"""
    stats = get_statistics(message.from_user.id)

    await message.answer(
        f"📊 <b>Твоя статистика:</b>\n\n"
        f"📋 Всего задач: {stats['total']}\n"
        f"✅ Выполнено: {stats['completed']}\n"
        f"⏳ В процессе: {stats['pending']}\n"
        f"🔴 Высокий приоритет: {stats['high_priority']}\n\n"
        f"💪 Процент выполнения: {stats['completion_rate']}%",
        parse_mode="HTML"
    )


@dp.message(Command("charts"))
async def cmd_charts(message: Message):
    """Показать графики статистики"""
    from charts import create_statistics_chart
    from aiogram.types import BufferedInputFile
    
    # Генерируем дашборд
    buffer = create_statistics_chart(message.from_user.id)
    
    # Отправляем как фото
    photo = BufferedInputFile(buffer.read(), filename='statistics.png')
    
    await message.answer_photo(
        photo=photo,
        caption="📊 <b>Подробная статистика</b>\n\n"
                "Используй /stats для текстовой версии",
        parse_mode="HTML"
    )


# ========== ЗАПУСК БОТА ==========

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())