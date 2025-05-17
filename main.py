import asyncio
import logging

from aiogram import Bot, Dispatcher
from app.config_data.config import Config, load_config
from app.handlers import router
from app.middleware.db import DbSessionMiddleware

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()
    dp.message.middleware(DbSessionMiddleware())
    # Регистриуем роутеры в диспетчере
    dp.include_router(router)


    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())