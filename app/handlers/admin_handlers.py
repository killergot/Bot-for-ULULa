from copy import deepcopy

from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.lexicon.lexicon import LEXICON_RU

from app.keyboard.keyboard import kb_main
router = Router()


@router.message(CommandStart())
async def start_command(message: Message,bot: Bot):
    await bot.send_message(chat_id=message.chat.id,
                            text=LEXICON_RU['/start'],
                            reply_markup=kb_main)

