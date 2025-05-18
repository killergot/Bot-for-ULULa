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