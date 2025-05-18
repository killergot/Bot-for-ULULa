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
    access_token : Mapped[str] = mapped_column(String, nullable=True)
    refresh_token : Mapped[str] = mapped_column(String, nullable=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)

    group: Mapped["database.models.groups.Group"] = relationship("database.models.groups.Group", back_populates="users")

