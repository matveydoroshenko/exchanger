from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter
from tgbot.services.sqlite import Database

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    text = "/day - статистика за день\n" \
           "/all - за все время\n" \
           "/ban 'user_id' - забанить пользователя\n" \
           "/unban 'user_id' - разбанить пользователя\n" \
           "/balance 'user_id' '100' - выдать баланс\n" \
           "/verif 'user_id' - верифицировать юзера\n" \
           "/extra_charge 'процентов' - наценка" \
           "\n\n" \
           "Заменить в кавычках на нужное и убрать их!"
    await message.answer(text)


@admin_router.message(F.text == "/all")
async def all_users(message: Message):
    db = Database()
    users = db.select_all_users()
    if users:
        text = []
        for index, user in enumerate(users):
            text.append(f"{index + 1}. {user[0]} {user[1]}")
        text = "\n".join(text)
    else:
        await message.answer("Нет юзеров!")
        return
    await message.answer(text)


@admin_router.message(F.text == "/day")
async def all_users(message: Message):
    db = Database()
    users = db.select_all_users()
    if users:
        text = []
        for index, user in enumerate(users):
            if user[10] == str(datetime.today().date()):
                text.append(f"{index + 1}. {user[0]} {user[1]}")
        text = "\n".join(text)
    if not text:
        await message.answer("Нет юзеров!")
        return
    await message.answer(text)


@admin_router.message(F.text.startswith("/ban"))
async def ban(message: Message):
    db = Database()
    user_id = int(message.text.replace("/ban ", ""))
    db.blacklist_user(user_id=user_id)
    await message.answer("Успешно!")


@admin_router.message(F.text.startswith("/unban"))
async def ban(message: Message):
    db = Database()
    user_id = int(message.text.replace("/unban ", ""))
    db.unban(user_id=user_id)
    await message.answer("Успешно!")


@admin_router.message(F.text.startswith("/extra_charge"))
async def ban(message: Message):
    db = Database()
    extra_charge = int(message.text.replace("/extra_charge ", ""))
    db.update_extra_charge(position=1, new_extra_charge=extra_charge)
    await message.answer("Успешно!")


@admin_router.message(F.text.startswith("/balance "))
async def ban(message: Message):
    db = Database()
    user = message.text.replace("/balance ", "").split(" ")
    user_id = user[0]
    balance = user[1]
    db.update_user_fiat_balance(user_id=int(user_id), new_fiat_balance=float(balance))
    await message.answer("Успешно!")
