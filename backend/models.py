from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ========== USER MODELS ==========

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    telegram_id: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    telegram_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ========== TASK MODELS ==========

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "средний"
    category: Optional[str] = None
    tags: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    category: Optional[str]
    tags: Optional[str]
    deadline: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ========== COMMENT MODELS ==========

class CommentCreate(BaseModel):
    task_id: int
    text: str


class CommentResponse(BaseModel):
    id: int
    task_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== STATISTICS ==========

class StatisticsResponse(BaseModel):
    total: int
    completed: int
    pending: int
    high_priority: int
    completion_rate: float
    tasks_by_category: dict
    tasks_per_day: dict
