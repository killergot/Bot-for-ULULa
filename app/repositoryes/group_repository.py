import logging

from sqlalchemy import select


from app.database.models.groups import Group
from app.repositoryes.template import TemplateRepository

log = logging.getLogger(__name__)

class GroupRepository(TemplateRepository):
    async def get_all(self):
        data = select(Group)
        users = await self.db.execute(data)
        return users.scalars().all()

    async def get_id(self, group: str):
        data = select(Group).where(Group.number == group)
        users = await self.db.execute(data)
        return users.scalars().first()

    async def create(self, group: str):
        data = Group(number=group)
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)
        return data

