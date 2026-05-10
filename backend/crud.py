from sqlalchemy.orm import Session
from database import User, Task, Status, Priority, get_db
from datetime import datetime
from typing import List, Optional


# ========== ПОЛЬЗОВАТЕЛИ ==========

def create_user(telegram_id: int, username: str = None, first_name: str = ""):
    """Создать нового пользователя"""
    db = get_db()

    # Проверяем, существует ли
    existing = db.query(User).filter(User.telegram_id == telegram_id).first()
    if existing:
        db.close()
        return existing

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def get_user(telegram_id: int) -> Optional[User]:
    """Получить пользователя"""
    db = get_db()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    db.close()
    return user


# ========== ЗАДАЧИ ==========

def create_task(telegram_id: int, title: str, description: str = None,
                priority: str = Priority.MEDIUM.value, deadline: datetime = None):
    """Создать задачу"""
    db = get_db()

    task = Task(
        telegram_id=telegram_id,
        title=title,
        description=description,
        priority=priority,
        deadline=deadline
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()
    return task_id


def get_user_tasks(telegram_id: int, status: str = None) -> List[Task]:
    """Получить все задачи пользователя"""
    db = get_db()

    query = db.query(Task).filter(Task.telegram_id == telegram_id)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.created_at.desc()).all()

    # Копируем данные, чтобы избежать проблем после закрытия сессии
    result = []
    for task in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'deadline': task.deadline,
            'created_at': task.created_at
        })

    db.close()
    return result


def get_task(task_id: int) -> Optional[dict]:
    """Получить задачу по ID"""
    db = get_db()
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        db.close()
        return None

    result = {
        'id': task.id,
        'telegram_id': task.telegram_id,
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'status': task.status,
        'deadline': task.deadline,
        'created_at': task.created_at,
        'completed_at': task.completed_at
    }

    db.close()
    return result


def complete_task(task_id: int, telegram_id: int) -> bool:
    """Отметить задачу как выполненную"""
    db = get_db()

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.telegram_id == telegram_id
    ).first()

    if not task:
        db.close()
        return False

    task.status = Status.COMPLETED.value
    task.completed_at = datetime.now()
    db.commit()
    db.close()
    return True


def delete_task(task_id: int, telegram_id: int) -> bool:
    """Удалить задачу"""
    db = get_db()

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.telegram_id == telegram_id
    ).first()

    if not task:
        db.close()
        return False

    db.delete(task)
    db.commit()
    db.close()
    return True


def get_statistics(telegram_id: int) -> dict:
    """Получить статистику пользователя"""
    db = get_db()

    all_tasks = db.query(Task).filter(Task.telegram_id == telegram_id).all()

    total = len(all_tasks)
    completed = len([t for t in all_tasks if t.status == Status.COMPLETED.value])
    pending = len([t for t in all_tasks if t.status == Status.PENDING.value])

    # Статистика по приоритетам
    high_priority = len([t for t in all_tasks if t.priority == Priority.HIGH.value])

    db.close()

    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'high_priority': high_priority,
        'completion_rate': round(completed / total * 100, 1) if total > 0 else 0
    }