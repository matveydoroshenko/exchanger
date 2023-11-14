def start_keyboard():
    keyboard = {
        "_": "ReplyKeyboardMarkup",
        "keyboard": [
            [
                "💼 Кошелек",
                "📊 Обмен"
            ],
            [
                "🔷 О сервисе"
            ],
        ],
        "resize_keyboard": True,
    }
    return keyboard


def currency_choose():
    keyboard = {
        "_": "ReplyKeyboardMarkup",
        "keyboard": [
            [
                "Рубли"
            ],
            [
                "ETH"
            ],
            [
                "USDT"
            ],
            [
                "BTC"
            ],
            [
                "Назад"
            ]
        ],
        "resize_keyboard": True,
    }
    return keyboard
