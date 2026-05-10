from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

# Импорты из нашего проекта
from models import (
    UserCreate, UserLogin, UserResponse, Token,
    TaskCreate, TaskUpdate, TaskResponse,
    CommentCreate, CommentResponse, StatisticsResponse
)
from auth import (
    get_db, get_current_user, create_access_token,
    authenticate_user, create_web_user, WebUser
)
from database import Task, Status, Priority, get_db as get_db_session
from crud import (
    create_task, get_user_tasks, complete_task,
    delete_task, get_statistics, get_task
)

# Инициализация приложения
app = FastAPI(title="Task Manager API", version="1.0.0")

# Подключение статических файлов и шаблонов
import os
from pathlib import Path

# Определяем корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))


# ========== ВЕБОРИГИНАЛЫ СТРАНИЦЫ ==========

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Дашборд (требует авторизации)"""
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    """Страница задач"""
    return templates.TemplateResponse(request=request, name="tasks.html")


@app.get("/webapp", response_class=HTMLResponse)
async def webapp_page(request: Request):
    """Telegram Web App - упрощенная версия для Telegram"""
    return templates.TemplateResponse(request=request, name="webapp.html")


@app.get("/telegram-login", response_class=HTMLResponse)
async def telegram_login_page(request: Request):
    """Страница авторизации через Telegram"""
    return templates.TemplateResponse(request=request, name="telegram-login.html")


# ========== АВТОРИЗАЦИЯ API ==========

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    new_user = create_web_user(
        db=db,
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        telegram_id=user.telegram_id
    )
    return new_user


@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Вход пользователя"""
    authenticated_user = authenticate_user(db, user.email, user.password)
    
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаём токен
    access_token = create_access_token(data={"sub": authenticated_user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: WebUser = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@app.post("/api/auth/telegram-login")
async def telegram_login(data: dict, db: Session = Depends(get_db)):
    """
    Автоматический вход через Telegram ID
    Создает пользователя если не существует
    """
    telegram_id = data.get('telegram_id')
    first_name = data.get('first_name', 'Пользователь')
    username = data.get('username')
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Telegram ID обязателен")
    
    # Ищем пользователя с таким telegram_id
    user = db.query(WebUser).filter(WebUser.telegram_id == telegram_id).first()
    
    # Если нет - создаём автоматически
    if not user:
        # Генерируем уникальный email на основе telegram_id
        email = f"tg{telegram_id}@telegram.user"
        
        user = WebUser(
            email=email,
            password_hash=get_password_hash(str(telegram_id)),  # Пароль = telegram_id
            first_name=first_name,
            telegram_id=telegram_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Создаём JWT токен
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "telegram_id": user.telegram_id
        }
    }


# ========== ЗАДАЧИ API ==========

@app.post("/api/tasks", response_model=dict)
async def api_create_task(
    task: TaskCreate,
    current_user: WebUser = Depends(get_current_user)
):
    """Создать задачу"""
    task_id = create_task(
        telegram_id=current_user.telegram_id or current_user.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        deadline=task.deadline
    )
    
    return {"id": task_id, "message": "Задача создана"}


# ========== ПУБЛИЧНЫЕ API ДЛЯ TELEGRAM WEBAPP (без JWT) ==========

@app.post("/api/telegram/tasks")
async def telegram_create_task(data: dict):
    """Создать задачу через Telegram WebApp (без JWT)"""
    task_id = create_task(
        telegram_id=data.get('telegram_id'),
        title=data.get('title'),
        description=data.get('description'),
        priority=data.get('priority', 'средний'),
        deadline=None
    )
    return {"id": task_id, "message": "Задача создана"}


@app.get("/api/telegram/tasks/{telegram_id}")
async def telegram_get_tasks(telegram_id: int):
    """Получить задачи по telegram_id (для WebApp)"""
    tasks = get_user_tasks(telegram_id=telegram_id)
    return tasks


@app.patch("/api/telegram/tasks/{task_id}/complete")
async def telegram_complete_task(task_id: int, data: dict):
    """Отметить задачу выполненной через Telegram"""
    success = complete_task(
        task_id=task_id,
        telegram_id=data.get('telegram_id')
    )
    if not success:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"message": "Задача выполнена"}


@app.get("/api/tasks", response_model=List[dict])
async def api_get_tasks(
    status: str = None,
    current_user: WebUser = Depends(get_current_user)
):
    """Получить все задачи пользователя"""
    tasks = get_user_tasks(
        telegram_id=current_user.telegram_id or current_user.id,
        status=status
    )
    return tasks


@app.get("/api/tasks/{task_id}", response_model=dict)
async def api_get_task(
    task_id: int,
    current_user: WebUser = Depends(get_current_user)
):
    """Получить задачу по ID"""
    task = get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Проверка владельца
    user_id = current_user.telegram_id or current_user.id
    if task['telegram_id'] != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
    
    return task


@app.patch("/api/tasks/{task_id}/complete")
async def api_complete_task(
    task_id: int,
    current_user: WebUser = Depends(get_current_user)
):
    """Отметить задачу как выполненную"""
    success = complete_task(
        task_id=task_id,
        telegram_id=current_user.telegram_id or current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return {"message": "Задача выполнена"}


@app.delete("/api/tasks/{task_id}")
async def api_delete_task(
    task_id: int,
    current_user: WebUser = Depends(get_current_user)
):
    """Удалить задачу"""
    success = delete_task(
        task_id=task_id,
        telegram_id=current_user.telegram_id or current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return {"message": "Задача удалена"}


# ========== СТАТИСТИКА API ==========

@app.get("/api/statistics")
async def api_statistics(current_user: WebUser = Depends(get_current_user)):
    """Получить статистику пользователя"""
    stats = get_statistics(current_user.telegram_id or current_user.id)
    
    # Дополнительная статистика для графиков
    tasks = get_user_tasks(current_user.telegram_id or current_user.id)
    
    # Задачи по дням (за последние 7 дней)
    tasks_per_day = {}
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%d.%m')
        count = len([
            t for t in tasks 
            if t.get('completed_at') and 
            t['completed_at'].date() == (datetime.now() - timedelta(days=i)).date()
        ])
        tasks_per_day[date] = count
    
    # Задачи по категориям
    tasks_by_category = {}
    for task in tasks:
        category = task.get('category', 'Без категории') or 'Без категории'
        tasks_by_category[category] = tasks_by_category.get(category, 0) + 1
    
    stats['tasks_per_day'] = tasks_per_day
    stats['tasks_by_category'] = tasks_by_category
    
    return stats


# ========== HEALTH CHECK ==========

@app.get("/api/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "timestamp": datetime.now()}


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
