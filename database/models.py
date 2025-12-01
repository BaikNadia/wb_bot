from sqlalchemy import (
    create_engine,
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    DECIMAL,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from bot.config import config

# Создаём подключение к БД с использованием свойства
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Fine(Base):
    """Модель для хранения штрафов"""

    __tablename__ = "fines"

    id = Column(String(50), primary_key=True)
    date = Column(DateTime, nullable=False)
    type = Column(String(200), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    order_id = Column(String(50))
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(Boolean, default=False)


class Notification(Base):
    """Модель для логов уведомлений"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fine_id = Column(String(50))
    channel = Column(String(50), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)


def init_db():
    """Инициализация базы данных"""
    Base.metadata.create_all(bind=engine)
