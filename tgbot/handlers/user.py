import random
from sqlite3 import IntegrityError

import AaioAPI
import requests
from AaioAPI import Aaio
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.utils.markdown import hbold

from funcs.get_crypto_balances import convert_to_rubles
from funcs.payment import create_payoff
from tgbot.keyboards.inline import wallet_keyboard, settings_keyboard, choose_currency_keyboard, verif_keyboard, \
    about_service_keyboard, top_up_keyboard, invoice_keyboard, choose_method_keyboard, exchange_keyboard
from tgbot.keyboards.reply import start_keyboard, currency_choose
from tgbot.misc.states import Payment, Popoln, CurrencyExchange
from tgbot.services.sqlite import Database

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
    await message.answer_photo(photo=FSInputFile(path="/Users/matvejdoroshenko/PycharmProjects"
                                                      "/@Remitano_inbot/images/wallet_button.jpeg"),
                               caption=f"💼{hbold('Кошелек')}:\n"
                                       f"\n➖➖➖➖➖➖➖➖➖➖"
                                       f"\n📑 Верификация: {verification_status}"
                                       f"\n➖➖➖➖➖➖➖➖➖➖"
                                       f"\n{hbold(f'🏦 Общий баланс: {convert_to_rubles(usdt, eth, btc, user[4], currency)}{currency_sign}')}"
                                       f"\n{hbold(f'💵 Фиатный баланс: {round(convert_to_rubles(usdt, eth, btc, user[4], currency) - convert_to_rubles(usdt, eth, btc, 0, currency), 2)}{currency_sign}')}"
                                       f"\n{hbold(f'🗄 ID: {message.from_user.id}')}"
                                       f"\n➖➖➖➖➖➖➖➖➖➖"
                                       f"\n🔐 Криптопортфель:"
                                       f"\n\n💰{btc} BTC"
                                       f"\n💰{usdt} USDT"
                                       f"\n💰{eth} ETH"
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
    await call.message.answer_photo(photo=FSInputFile(path="/Users/matvejdoroshenko/PycharmProjects"
                                                           "/@Remitano_inbot/images/verification.jpeg"),
                                    caption=text,
                                    reply_markup=verif_keyboard(verified))


@user_router.callback_query(F.data == "delmsg")
async def delmsg(call: CallbackQuery):
    await call.message.delete()


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

    await message.answer_photo(photo=FSInputFile(path="/Users/matvejdoroshenko/PycharmProjects"
                                                      "/@Remitano_inbot/images/about_service.jpeg"),
                               caption=text,
                               reply_markup=about_service_keyboard())


@user_router.callback_query(F.data == "popoln")
async def popoln(call: CallbackQuery):
    await call.message.answer_photo(photo=FSInputFile(path="/Users/matvejdoroshenko/PycharmProjects"
                                                           "/@Remitano_inbot/images/top_up.jpeg"),
                                    caption="Выберите вариант пополнения баланса:",
                                    reply_markup=top_up_keyboard())


@user_router.callback_query(F.data == "deposit_card")
async def deposit_card(call: CallbackQuery, state: FSMContext):
    await call.message.edit_caption(caption=f"Введите сумму пополнения:\nМинимальная сумма - {hbold('1000₽')}")
    await state.set_state(Payment.sum)


@user_router.message(Payment.sum)
async def payment_sum(message: Message, state: FSMContext):
    if int(message.text) < 1000:
        await message.answer("Вы ввели сумму меньше 1000₽")
        return
    payment_id = f"{message.from_user.id}:{random.randint(100, 999)}"
    merchant_id = "46cdb37e-cb1d-45dd-b426-eca83015cfbe"
    secret_key = "7c51da4caad10af4210e95b255d38c91"
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
async def check_payment(call: CallbackQuery, state: FSMContext):
    payment = Aaio()
    data = await state.get_data()
    AaioAPI.check_payment(data.get("payment_url"), payment)
    if not payment.is_success():
        db = Database()
        top_up = data.get("top_up")
        await call.message.delete()
        await call.message.answer("Успешно оплачено!\n"
                                  "Деньги зачислены на счёт!")
        db.update_user_fiat_balance(user_id=call.message.chat.id,
                                    new_fiat_balance=int(top_up) + int(db.select_user(user_id=call.message.chat.id)[4]))
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
                                            f"\nМинимальная сумма - {hbold('1000₽')}"
                                            f"\nДоступный баланс: {convert_to_rubles(usdt, eth, btc, user[4], currency) - convert_to_rubles(usdt, eth, btc, 0, currency)}")
    await state.set_state(Popoln.sum)


@user_router.message(Popoln.sum)
async def popoln_sum(message: Message, state: FSMContext):
    db = Database()
    user = db.select_user(user_id=message.from_user.id)
    users_crypto_balance = db.select_crypto_balances(user_id=message.from_user.id)
    usdt = users_crypto_balance[2]
    eth = users_crypto_balance[3]
    btc = users_crypto_balance[4]
    currency = user[8]
    balance = convert_to_rubles(usdt, eth, btc, user[4], currency) - convert_to_rubles(usdt, eth, btc, 0, currency)
    if int(message.text) < 1000:
        await message.answer("Вы ввели сумму меньше 1000₽")
        return
    if int(message.text) > balance:
        await message.answer("Недостаточно баланса!")
        return
    await state.update_data(vivod_sum=message.text)
    text = "♻️ Вывод:" \
           f"\n\nСумма: {message.text}₽\n" \
           f"Выберите метод:"
    await message.answer(text, reply_markup=choose_method_keyboard())


@user_router.callback_query(F.data.startswith("choose_method:"))
async def choose_method(call: CallbackQuery, state: FSMContext):
    await state.update_data(method=call.data.split(":")[1])
    await call.message.answer("Отправь номер кошелька/карты:")
    await state.set_state(Popoln.wallet)


@user_router.message(Popoln.wallet)
async def popoln_wallet(message: Message, state: FSMContext):
    data = await state.get_data()
    vivod_sum = data.get("vivod_sum")
    method = data.get("method")
    if method == "USDT":
        method = "tether_trc20"
    elif method == "BTC":
        method = "bitcoin"
    elif method == "RUB":
        method = "cards_ru"
    create_payoff("864ef93a855b48a4520c4ebccf2e3435",
                  f"{message.from_user.id}:{random.randint(100, 999)}",
                  method,
                  vivod_sum,
                  message.text,
                  0)
    await message.answer("Вывод успешно создан!")


@user_router.message(F.text == "📊 Обмен")
async def exchange_reply_button(message: Message, state: FSMContext):
    await message.answer("Выбери валюту для обмена:", reply_markup=currency_choose())


@user_router.message(F.text == "Рубли")
async def rubles_exchange(message: Message, state: FSMContext):
    await state.update_data(currency="RUB")
    await message.answer("Сколько Вы хотите поменять?:")
    await state.set_state(CurrencyExchange.sum)


@user_router.message(F.text == "ETH")
async def rubles_exchange(message: Message, state: FSMContext):
    await state.update_data(currency="ETH")
    await message.answer("Сколько Вы хотите поменять?:")
    await state.set_state(CurrencyExchange.sum)


@user_router.message(F.text == "BTC")
async def rubles_exchange(message: Message, state: FSMContext):
    await state.update_data(currency="BTC")
    await message.answer("Сколько Вы хотите поменять?:")
    await state.set_state(CurrencyExchange.sum)


@user_router.message(F.text == "USD")
async def rubles_exchange(message: Message, state: FSMContext):
    await state.update_data(currency="USD")
    await message.answer("Сколько Вы хотите поменять?:")
    await state.set_state(CurrencyExchange.sum)


@user_router.message(CurrencyExchange.sum)
async def currency_exchange_sum(message: Message, state: FSMContext):
    data = await state.get_data()
    db = Database()
    await state.update_data(exchange_sum=message.text)
    user = db.select_user(user_id=message.from_user.id)
    users_crypto_balance = db.select_crypto_balances(user_id=message.from_user.id)
    usdt = users_crypto_balance[2]
    eth = users_crypto_balance[3]
    btc = users_crypto_balance[4]
    currency = user[8]
    balance = convert_to_rubles(usdt, eth, btc, user[4], currency) - convert_to_rubles(usdt, eth, btc, 0, currency)
    if int(message.text) > balance:
        await message.answer("Недостаточно баланса!")
        return
    currency = data.get("currency")
    await message.answer("Выберите валюту, которую хотите получить:", reply_markup=exchange_keyboard(currency))


@user_router.callback_query(F.data.startswith("exchange:"))
async def final_exchange(call: CallbackQuery, state: FSMContext):
    db = Database()
    data = await state.get_data()
    exchange_sum = int(data.get("exchange_sum"))
    user = db.select_user(user_id=call.message.chat.id)
    currency = data.get("currency")
    changing_currency = call.data.split(":")[1]
    users_crypto_balance = db.select_crypto_balances(user_id=call.message.chat.id)
    usdt = users_crypto_balance[2]
    eth = users_crypto_balance[3]
    btc = users_crypto_balance[4]
    extra_charge = int(db.select_extra_charge()[0][1])
    fiat_balance = round(convert_to_rubles(usdt, eth, btc, user[4], "RUB") - convert_to_rubles(usdt, eth, btc, 0, "RUB"))
    if currency == "RUB":
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=RUB")
        data = response.json()
        if changing_currency == "BTC":
            rate = data.get('data').get('rates').get('BTC')
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc + exchange_sum * (rate - rate * extra_charge))
        elif changing_currency == "ETH":
            rate = data.get('data').get('rates').get('ETH')
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth + exchange_sum * (rate - rate * extra_charge))
        elif changing_currency == "USDT":
            rate = data.get('data').get('rates').get('USDT')
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt + exchange_sum * (rate - rate * extra_charge))
    elif currency == "BTC":
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
        data = response.json()
        if changing_currency == "RUB":
            rate = data.get('data').get('rates').get('RUB')
            db.update_user_fiat_balance(user_id=call.message.chat.id,
                                        new_fiat_balance=fiat_balance + exchange_sum * (rate - rate * extra_charge))
        elif changing_currency == "ETH":
            rate = data.get('data').get('rates').get('ETH')
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth + exchange_sum * (rate - rate * extra_charge))
        elif changing_currency == "USDT":
            rate = data.get('data').get('rates').get('USDT')
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt + exchange_sum * (rate - rate * extra_charge))
    elif currency == "ETH":
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=ETH")
        data = response.json()
        if changing_currency == "BTC":
            rate = data.get('data').get('rates').get('BTC')
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc + exchange_sum * (rate + rate - extra_charge))
        elif changing_currency == "RUB":
            rate = data.get('data').get('rates').get('RUB')
            db.update_user_fiat_balance(user_id=call.message.chat.id,
                                        new_fiat_balance=fiat_balance + exchange_sum * (rate + rate - extra_charge))
        elif changing_currency == "USDT":
            rate = data.get('data').get('rates').get('USDT')
            db.update_usdt_balance(user_id=call.message.chat.id, new_usdt_balance=usdt + exchange_sum * (rate + rate - extra_charge))
    elif currency == "USDT":
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USDT")
        data = response.json()
        if changing_currency == "BTC":
            rate = data.get('data').get('rates').get('BTC')
            db.update_btc_balance(user_id=call.message.chat.id, new_btc_balance=btc + exchange_sum * (rate + rate - extra_charge))
        elif changing_currency == "RUB":
            rate = data.get('data').get('rates').get('RUB')
            db.update_user_fiat_balance(user_id=call.message.chat.id, new_fiat_balance=fiat_balance + exchange_sum * (rate - rate * extra_charge))
        elif changing_currency == "ETH":
            rate = data.get('data').get('rates').get('ETH')
            db.update_eth_balance(user_id=call.message.chat.id, new_eth_balance=eth + exchange_sum * (rate - rate * extra_charge))
    await call.message.answer("Успешно обменено!")