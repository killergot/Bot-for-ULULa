from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from functools import lru_cache

from app.lexicon.lexicon import LEXICON_RU
from app.keyboard.keyboard import kb_main
from app.repositoryes.user_repository import UserRepository
router = Router()

@lru_cache()
async def _get_user(id,repo,bot,message):
    user = await repo.get(id)
    if not user:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Вас нет в нашей системе, нажмите /start чтобы зарегаться')
    return user


@router.message(CommandStart())
async def start_command(message: Message,
                        bot: Bot,
                        db_session: AsyncSession  # <-- подтянется из middleware
                        ):
    await bot.send_message(chat_id=message.chat.id,
                            text=LEXICON_RU['/start'],
                            reply_markup=kb_main)
    user_repo = UserRepository(db_session)
    user = await user_repo.get(message.from_user.id)
    if user:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Вы уже есть в нашей системе')
    else:
        user = await user_repo.create(message.from_user.id)
        if not user:
            await bot.send_message(chat_id=message.chat.id,
                                   text=f'Не получилось создать пользователя')

@router.message(Command('schedule'))
async def schedule_command(message: Message,
                           bot: Bot,
                           db_session: AsyncSession ):
    user_repo = UserRepository(db_session)
    user = await _get_user(message.from_user.id,user_repo, bot, message)


@router.message(Command('login'))
async def schedule_command(message: Message,
                           bot: Bot,
                           db_session: AsyncSession ):
    user_repo = UserRepository(db_session)
    user = await _get_user(message.from_user.id,user_repo, bot, message)



