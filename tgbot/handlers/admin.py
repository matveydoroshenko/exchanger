import os

from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter
from tgbot.services.sqlite import Database

from aiogram.types.input_file import FSInputFile

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    text = "/day - статистика за день\n" \
           "/all - за все время\n" \
           "/ban 'user_id' - забанить пользователя\n" \
           "/unban 'user_id' - разбанить пользователя\n" \
           "/balance 'user_id' '100' - выдать баланс в долларах\n" \
           "/verif 'user_id' - верифицировать юзера\n" \
           "/extra_charge 'процентов' - наценка\n" \
           "/usdt 'user_id' '100' - выдать баланс USDT\n"\
           "/eth 'user_id' '100' - выдать баланс ETH\n" \
           "/btc 'user_id' '100' - выдать баланс BTC\n" \
           "\n\n" \
           "Заменить в кавычках на нужное и убрать их!"
    await message.answer(text)


@admin_router.message(F.text == "/all")
async def all_users(message: Message):
    db = Database()
    users = db.select_all_users()
    if users:
        for index, user in enumerate(users):
            with open("/exchanger/users.txt", "w") as file_object:
                for index, user in enumerate(users):
                    file_object.write(str(user[0]) + " " + str(user[1]) + '\n')
        await message.answer_document(document=FSInputFile(path="/exchanger/users.txt"))
        os.remove("/exchanger/users.txt")
    else:
        await message.answer("Нет юзеров!")
        return

@admin_router.message(F.text == "/day")
async def day_users(message: Message):
    db = Database()
    users = db.select_all_users()
    if users:
        with open("/exchanger/users.txt", "w") as file_object:
            for index, user in enumerate(users):
                if user[10] == str(datetime.today().date()):
                    file_object.write(str(user[0]) + " " + str(user[1]) + '\n')
        try:
            await message.answer_document(document=FSInputFile(path="/exchanger/users.txt"))
        except:
            await message.answer("Нет юзеров!")
        os.remove("/exchanger/users.txt")
        return


@admin_router.message(F.text.startswith("/verif"))
async def verif(message: Message):
    db = Database()
    user_id = int(message.text.replace("/verif ", ""))
    db.update_user_verification_status(user_id, "True")
    await message.answer("Успешно!")


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


@admin_router.message(F.text.startswith("/btc "))
async def ban(message: Message):
    db = Database()
    user = message.text.replace("/btc ", "").split(" ")
    user_id = user[0]
    balance = user[1]
    db.update_btc_balance(user_id=int(user_id), new_btc_balance=float(balance))
    await message.answer("Успешно!")


@admin_router.message(F.text.startswith("/eth "))
async def ban(message: Message):
    db = Database()
    user = message.text.replace("/eth ", "").split(" ")
    user_id = user[0]
    balance = user[1]
    db.update_eth_balance(user_id=int(user_id), new_eth_balance=float(balance))
    await message.answer("Успешно!")


@admin_router.message(F.text.startswith("/usdt "))
async def ban(message: Message):
    db = Database()
    user = message.text.replace("/usdt ", "").split(" ")
    user_id = user[0]
    balance = user[1]
    db.update_usdt_balance(user_id=int(user_id), new_usdt_balance=float(balance))
    await message.answer("Успешно!")

