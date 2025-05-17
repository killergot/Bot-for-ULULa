from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, TIMESTAMP, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.psql import Base
import uuid
from datetime import datetime
#from database.models.students import Student

# Модель пользователей (users)
class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(Integer, unique=True,primary_key=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)