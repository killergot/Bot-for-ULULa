from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from functools import lru_cache

from app.api import ApiClient
from app.lexicon.lexicon import LEXICON_RU
from app.keyboard.keyboard import kb_main
from app.repositoryes.user_repository import UserRepository
router = Router()

import httpx

API_URL = "http://localhost:8000/auth"

async def login_user(email: str, password: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_URL}/login", json={"email": email, "password": password})
        resp.raise_for_status()
        return resp.json()

async def verify_2fa(code: str, session_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_URL}/verify-2fa", json={"code": code, "session_token": session_token})
        resp.raise_for_status()
        return resp.json()

async def get_user_profile(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = await client.get(f"{API_URL}/users/me", headers=headers)
        if resp.status_code == 401:
            raise Exception("Token expired")  # Здесь можно триггернуть обновление
        resp.raise_for_status()
        return resp.json()


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

class LoginStates(StatesGroup):
    email = State()
    password = State()
    code = State()


@router.message(Command("login"))
async def login_handler(message: Message, state: FSMContext):
    await message.answer("Введите email:")
    await state.set_state(LoginStates.email)


@router.message(LoginStates.email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите пароль:")
    await state.set_state(LoginStates.password)


@router.message(LoginStates.password)
async def get_password(message: Message, state: FSMContext):
    data = await state.get_data()
    email = data["email"]
    password = message.text

    try:
        login_response = await login_user(email, password)
        temp_token = login_response["session_token"]
        await state.update_data(temp_token=temp_token)
        await message.answer("Введите 2FA код:")
        await state.set_state(LoginStates.code)
    except Exception:
        await message.answer("Ошибка логина")
        await state.clear()


@router.message(LoginStates.code)
async def handle_2fa_code(message: Message, state: FSMContext, db_session: AsyncSession):
    data = await state.get_data()
    temp_token = data.get("temp_token")
    code = message.text

    try:
        tokens = await verify_2fa(code, temp_token)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Сохраняем токены в БД по Telegram ID
        user_repo = UserRepository(db_session)
        await user_repo.save_tokens(
            telegram_id=message.from_user.id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        await db_session.commit()
        await message.answer("✅ Успешный вход в систему!")
    except httpx.HTTPStatusError as e:
        await message.answer("❌ Неверный код или ошибка при входе.")
    finally:
        await state.clear()


@router.message(Command('test'))
async def get_email(message: Message, db_session: AsyncSession):
    client = ApiClient(
        telegram_id=message.from_user.id,
        session=db_session,
    )
    try:
        resp = await client.get("/users/get_me")
        profile = resp.json()
        await message.answer(f"👤 Профиль:{profile}")
    except Exception as e:
        await message.answer("Ошибка при получении профиля.")


