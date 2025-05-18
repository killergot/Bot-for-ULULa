from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.api import ApiClient
from app.database.psql import AsyncSessionLocal
from app.repositoryes.group_repository import GroupRepository
from app.repositoryes.user_repository import UserRepository

scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)

async def send_broadcast(bot: Bot):
    text = "⏰ Ежечасная рассылка"
    session = await AsyncSessionLocal()
    repo = UserRepository(session)
    user_with_tokens = await repo.get_with_tokens()
    client = ApiClient(user_with_tokens.id,
                       session)
    group_repository = GroupRepository(session)
    groups = await group_repository.get_all()
    schedulers = dict()
    for group in groups:
        try:
            # Тут логика получения расписания
            pass
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение {group.id}: {e}")

    users = await repo.get_all()
    for user in users:
        temp = schedulers[user.group_id]



# === Настройка планировщика ===
def setup_scheduler(bot):
    # Каждые часы с 7 до 20 включительно
    scheduler.add_job(send_broadcast, CronTrigger(hour="7-20", minute="*/10"))
    scheduler.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
