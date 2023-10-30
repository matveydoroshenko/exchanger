import requests


def get_usd_to_rubles_rate():
    response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USD")
    data = response.json()
    return data.get('data').get('rates').get('RUB')


def convert_to_rubles(amount_usdt, amount_eth, amount_btc, fiat_balance, currency):
    cryptos = ["USDT", "ETH", "BTC"]

    exchange_rates = {}

    for crypto in cryptos:
        response = requests.get(f"https://api.coinbase.com/v2/exchange-rates?currency=USD")
        if response.status_code == 200:
            data = response.json()
            exchange_rates[crypto] = data["data"]["rates"][crypto]
        else:
            print(f"Failed to get the exchange rate for {crypto}.")

    total_usd = (amount_usdt / float(exchange_rates["USDT"])) + (amount_eth / float(exchange_rates["ETH"])) + (amount_btc / float(exchange_rates["BTC"]))
    if currency == "USD":
        rate = 1
    else:
        rate = get_usd_to_rubles_rate()
    print(total_usd, fiat_balance)
    total_rubles = (total_usd + fiat_balance) * float(rate)
    return round(total_rubles, 2)
