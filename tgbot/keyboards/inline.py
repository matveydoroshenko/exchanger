from aiogram.utils.keyboard import InlineKeyboardBuilder


def wallet_keyboard():
    keyboard = {
        "_": "InlineKeyboardMarkup",
        "inline_keyboard": [
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "📥 Пополнить",
                    "callback_data": "popoln"
                },
                {
                    "_": "InlineKeyboardButton",
                    "text": "📤 Вывести",
                    "callback_data": "vivod"
                }
            ],
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "🗃 Верификация",
                    "callback_data": "veref"
                },
                {
                    "_": "InlineKeyboardButton",
                    "text": "🔧 Настройки",
                    "callback_data": "settings"
                }
            ],
            [
                {
                   "_": "InlineKeyboardButton",
                   "text": "Курсы валют",
                   "callback_data": "rates"
                }
            ]
        ]
    }
    return keyboard


def settings_keyboard():
    keyboard = {
        "_": "InlineKeyboardMarkup",
        "inline_keyboard": [
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "🌐 Сменить валюту 🌐",
                    "callback_data": "cur"
                }
            ]
        ]
    }
    return keyboard


def choose_currency_keyboard():
    keyboard = {
        "_": "InlineKeyboardMarkup",
        "inline_keyboard": [
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "🇺🇸 USD",
                    "callback_data": "valut:USD"
                }
            ],
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "🇷🇺 RUB",
                    "callback_data": "valut:RUB"
                }
            ],
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "Назад",
                    "callback_data": "exchange_back"
                }
            ],
        ]
    }
    return keyboard


def verif_keyboard(verified):
    builder = InlineKeyboardBuilder()
    if not verified:
        builder.button(text="Пройти верификацию", url="http://t.me/who_is_seven")
    builder.button(text="Назад", callback_data="delmsg")
    builder.adjust(1, 1)
    return builder.as_markup()


def delete_keyboard_methods():
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data="delete_keyboard_methods")
    return builder.as_markup()

def about_service_keyboard():
    keyboard = {
        "_": "InlineKeyboardMarkup",
        "inline_keyboard": [
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "Условия",
                    "url": "https://telegra.ph/Soglashenie-dlya-otkrytiya-ECN-06-12"
                }
            ],
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "🧑🏻‍💻 Тех.Поддержка",
                    "url": "http://t.me/who_is_seven"
                }
            ],
        ]
    }
    return keyboard


def top_up_keyboard():
    keyboard = {
        "_": "InlineKeyboardMarkup",
        "inline_keyboard": [
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "Оплатить 💳",
                    "callback_data": "deposit_card"
                }
            ],
        ]
    }
    return keyboard


def invoice_keyboard(link, payment_id):
    keyboard = {
        "_": "InlineKeyboardMarkup",
        "inline_keyboard": [
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "Оплатить счёт",
                    "web_app": {
                        "_": "WebAppInfo",
                        "url": f"{link}"
                    }
                }
            ],
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "✅ Проверить",
                    "callback_data": f"check_payment:{payment_id}"
                }
            ],
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "❌ Отмена",
                    "callback_data": "back_pay"
                }
            ]
        ]
    }
    return keyboard


def choose_method_keyboard():
    keyboard = {
        "_": "InlineKeyboardMarkup",
        "inline_keyboard": [
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "USDT",
                    "callback_data": "choose_method:USDT"
                }
            ],
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "BTC",
                    "callback_data": "choose_method:BTC"
                }
            ],
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "RUB",
                    "callback_data": "choose_method:RUB"
                }
            ],
        ]
    }
    return keyboard


def exchange_keyboard(currency):
    if currency == "RUB":
        keyboard = {
            "_": "InlineKeyboardMarkup",
            "inline_keyboard": [
                [
                    {
                        "_": "InlineKeyboardButton",
                        "text": "USDT",
                        "callback_data": "exchange:USDT"
                    }
                ],
                [
                    {
                        "_": "InlineKeyboardButton",
                        "text": "BTC",
                        "callback_data": "exchange:BTC"
                    }
                ],
                [
                    {
                        "_": "InlineKeyboardButton",
                        "text": "ETH",
                        "callback_data": "exchange:ETH"
                    }
                ],
                [
                    {
                        "_": "InlineKeyboardButton",
                        "text": "Назад",
                        "callback_data": "exchange_back"
                    }
                ],
            ]
        }
    else:
        keyboard = {
            "_": "InlineKeyboardMarkup",
            "inline_keyboard": [
                [
                    {
                        "_": "InlineKeyboardButton",
                        "text": "RUB",
                        "callback_data": "exchange:RUB"
                    }
                ],
                [
                    {
                        "_": "InlineKeyboardButton",
                        "text": "Назад",
                        "callback_data": "exchange_back"
                    }
                ],
            ]
        }
    return keyboard


def exchange_back_keyboard():
    keyboard = {
        "_": "InlineKeyboardMarkup",
        "inline_keyboard": [
            [
                {
                    "_": "InlineKeyboardButton",
                    "text": "Назад",
                    "callback_data": "exchange_back"
                }
            ],
        ]
    }
    return keyboard
