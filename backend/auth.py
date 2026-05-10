from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime
from database import Base, SessionLocal, engine
import os

# Секретный ключ для JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 дней

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# ========== МОДЕЛЬ WEB-ПОЛЬЗОВАТЕЛЯ ==========

class WebUser(Base):
    __tablename__ = 'web_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    telegram_id = Column(Integer, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


# Создание таблицы
Base.metadata.create_all(engine)


# ========== ФУНКЦИИ АВТОРИЗАЦИИ ==========

def get_db():
    """Получить сессию БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ========== ЗАВИСИМОСТИ ==========

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получить текущего пользователя из токена"""
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(WebUser).filter(WebUser.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


# ========== CRUD ДЛЯ WEB ПОЛЬЗОВАТЕЛЕЙ ==========

def create_web_user(db: Session, email: str, password: str, first_name: str, telegram_id: int = None):
    """Создать веб-пользователя"""
    # Проверка существования
    existing = db.query(WebUser).filter(WebUser.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    user = WebUser(
        email=email,
        password_hash=get_password_hash(password),
        first_name=first_name,
        telegram_id=telegram_id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    """Аутентификация пользователя"""
    user = db.query(WebUser).filter(WebUser.email == email).first()
    
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    
    return user
