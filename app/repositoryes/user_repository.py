import uuid
from typing import Optional
import logging

from sqlalchemy import select

from uuid import UUID
from app.database.models.users import User
from app.repositoryes.template import TemplateRepository

log = logging.getLogger(__name__)

class UserRepository(TemplateRepository):
    async def get_all(self):
        data = select(User)
        users = await self.db.execute(data)
        return users.scalars().all()

    async def get_by_telegram(self, telegram_id: int):
        data = select(User).where(User.telegram_id == telegram_id)
        user = await self.db.execute(data)
        return user.scalars().first()

    async def get(self, user_id: int):
        return await self.db.get(User, user_id)

    async def get_with_tokens(self):
        data = select(User).where(User.access_token != None)
        users = await self.db.execute(data)
        return users.scalars().first()

    async def create(self,telegram_id) -> User:
        new_user = User(telegram_id=telegram_id)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def save_tokens(self, telegram_id: int, access_token: str, refresh_token: str):
        user = await self.get(telegram_id)

        user.access_token = access_token
        user.refresh_token = refresh_token

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        await self.db.delete(await self.get(user_id))
        await self.db.commit()
        return True