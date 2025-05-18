from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.api import ApiClient


scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)

async def send_broadcast(user_ids, bot: Bot, session: AsyncSession, message: Message):
    text = "⏰ Ежечасная рассылка"
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение {user_id}: {e}")

# === Настройка планировщика ===
def setup_scheduler():
    # Каждые часы с 7 до 20 включительно
    scheduler.add_job(send_broadcast, CronTrigger(hour="7-20", minute="*/10"))
    scheduler.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
