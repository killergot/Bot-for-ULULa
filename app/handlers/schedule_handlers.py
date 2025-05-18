import datetime

from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter

from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession


from app.api import ApiClient
from app.keyboard.keyboard import create_inline_kb

router = Router()

def format_schedule(schedule):
    if not schedule or not schedule[0]:
        return "На сегодня пар нет 🎉"

    formatted = "📅 *Расписание на сегодня:*\n"
    for i, lesson in enumerate(schedule[0], start=1):
        formatted += (
            f"\n*{i}. {lesson['subject']}*\n"
            f"🕒 {lesson['time_start']}–{lesson['time_end']}\n"
            f"👨‍🏫 {lesson['teacher']}\n"
            f"📍 {lesson['place']}\n"
        )
    return formatted

@router.message(Command('schedule'))
async def get_ask_day(message: Message, bot: Bot):
    await message.answer('Какое расписание хотите посмотреть?',
                         reply_markup=create_inline_kb([
                             'Сегодня',
                             'Завтра'
                         ]))
    await message.delete()

@router.callback_query(F.data == 'Сегодня')
async def schedule(callback: CallbackQuery,db_session: AsyncSession):
    client = ApiClient(
        telegram_id=callback.from_user.id,
        session=db_session,
    )
    try:
        resp = await client.get("/schedule/get_for_current_student/1")
        now = datetime.datetime.now()
        weekday = now.strftime('%A').lower()
        profile = resp.json()
        await callback.message.edit_text(format_schedule(profile[weekday]),
                                                parse_mode='Markdown')
    except Exception as e:
        await callback.answer("Ошибка при получении профиля." + str(e))
        await callback.message.delete()

@router.callback_query(F.data == 'Завтра')
async def schedule(callback: CallbackQuery,db_session: AsyncSession):
    client = ApiClient(
        telegram_id=callback.from_user.id,
        session=db_session,
    )
    try:
        resp = await client.get("/schedule/get_for_current_student/1")
        now = datetime.datetime.now() + datetime.timedelta(days=1)
        weekday = now.strftime('%A').lower()
        profile = resp.json()
        await callback.message.edit_text(format_schedule(profile[weekday]),
                                                parse_mode='Markdown')
    except Exception as e:
        await callback.answer("Ошибка при получении профиля." + str(e))
        await callback.message.delete()