from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

Base = declarative_base()


# Enum для приоритетов
class Priority(enum.Enum):
    LOW = "низкий"
    MEDIUM = "средний"
    HIGH = "высокий"


# Enum для статусов
class Status(enum.Enum):
    PENDING = "в процессе"
    COMPLETED = "выполнено"
    CANCELLED = "отменено"


# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(Integer, primary_key=True, unique=True)
    username = Column(String, nullable=True)
    first_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User {self.telegram_id} (@{self.username})>"


# Модель задачи
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False)  # Кому принадлежит
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(String, default=Priority.MEDIUM.value)
    status = Column(String, default=Status.PENDING.value)
    deadline = Column(DateTime, nullable=True)
    category = Column(String, nullable=True)  # Категория задачи
    tags = Column(String, nullable=True)  # Теги через запятую
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Task {self.id}: {self.title} ({self.status})>"


# Модель комментария
class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False)
    telegram_id = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Comment {self.id} for Task {self.task_id}>"


# Создание базы данных
engine = create_engine('sqlite:///tasks.db', echo=False)
Base.metadata.create_all(engine)

# Сессия для работы с БД
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """Получить сессию БД"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Закрытие будет в crud функциях