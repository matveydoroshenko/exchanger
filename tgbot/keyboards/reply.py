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
            [
                "💱 Купить криптовалюту"
            ]
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
            ]
        ],
        "resize_keyboard": True,
    }
    return keyboard
