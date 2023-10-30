from aiogram.fsm.state import StatesGroup, State


class Payment(StatesGroup):
    sum = State()


class Popoln(StatesGroup):
    sum = State()
    wallet = State()


class CurrencyExchange(StatesGroup):
    currency = State()
    sum = State()
