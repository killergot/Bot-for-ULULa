from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import logging
import pytz
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import ApiClient
from app.database.psql import AsyncSessionLocal
from app.repositoryes.group_repository import GroupRepository
from app.repositoryes.user_repository import UserRepository

scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)

async def send_broadcast(bot: Bot):
    session = AsyncSessionLocal()
    repo = UserRepository(session)
    user_with_tokens = await repo.get_with_tokens()
    client = ApiClient(user_with_tokens.telegram_id, session)
    group_repository = GroupRepository(session)
    groups = await group_repository.get_all()
    schedulers = dict()

    # Установим временную зону и получим текущие время и интервал
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz)
    interval_end = now + timedelta(hours=1)

    current_day = now.strftime("%A").lower()

    for group in groups:
        try:
            resp = await client.get(f'/schedule/get_by_number?group_number={group.number}&week_number=1')
            data = resp.json()

            lessons_today = data.get(current_day, [[]])[0]

            for lesson in lessons_today:
                # Парсим строку времени в datetime
                lesson_start_str = lesson["time_start"]
                lesson_start = datetime.strptime(lesson_start_str, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day, tzinfo=tz
                )

                # Проверка: попадает ли начало пары в заданный интервал
                print(now, lesson_start, interval_end)
                lesson_start = datetime.strptime(lesson["time_start"], "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day, tzinfo=tz
                )
                if now <= lesson_start < interval_end:
                    schedulers[group.id] = (
                        f"🎓 В {lesson['time_start']} у вас пара: {lesson['subject']} в {lesson['place']}"
                    )
                    break  # Достаточно одной пары
        except Exception as e:
            logger.warning(f"Ошибка при обработке группы {group.id}: {e}")

    print(schedulers)

    users = await repo.get_all()
    for user in users:
        message = schedulers.get(user.group_id)
        if message:
            try:
                print(user.telegram_id)
                await bot.send_message(chat_id=user.telegram_id, text=message)
            except Exception as e:
                logger.warning(f"Ошибка отправки пользователю {user.telegram_id}: {e}")



# === Настройка планировщика ===
def setup_scheduler(bot):
    # Каждые часы с 7 до 20 включительно
    scheduler.add_job(send_broadcast, CronTrigger(hour="7-20", minute="*/10"), [bot])
    scheduler.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
