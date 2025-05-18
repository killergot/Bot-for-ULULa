from sqlalchemy import  String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.psql import Base

class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(Integer, unique=True,primary_key=True,
                                    nullable=False, autoincrement=True)
    number : Mapped[str] = mapped_column(String, nullable=True)
    users: Mapped["app.database.models.users.User"] = relationship("app.database.models.users.User",
                                                                            back_populates="group")  # type: ignore

