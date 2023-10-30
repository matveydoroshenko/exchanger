import hashlib
from urllib.parse import urlencode

import requests
from requests.exceptions import ConnectTimeout, ReadTimeout


def create_payment(merchant_id, amount, currency, secret, order_id, desc, lang):
    sign = f':'.join([
        str(merchant_id),
        str(amount),
        str(currency),
        str(secret),
        str(order_id)
    ])

    params = {
        'merchant_id': merchant_id,
        'amount': amount,
        'currency': currency,
        'order_id': order_id,
        'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
        'desc': desc,
        'lang': lang
    }
    return "https://aaio.io/merchant/pay?" + urlencode(params)


def create_payoff(api_key, my_id, method, amount, wallet, commission_type):
    url = 'https://aaio.io/api/create-payoff'

    params = {
        'my_id': my_id,
        'method': method,
        'amount': amount,
        'wallet': wallet,
        'commission_type': commission_type,
    }

    headers = {
        'Accept': 'application/json',
        'X-Api-Key': api_key
    }

    try:
        response = requests.post(url, data=params, headers=headers, timeout=(15, 60))
    except ConnectTimeout:
        return 'ConnectTimeout'
    except ReadTimeout:
        return 'ReadTimeout'

    if response.status_code in [200, 400, 401]:
        try:
            response_json = response.json()
        except:
            return 'Failed to parse the response'

        if response_json['type'] == 'success':
            return response_json
        else:
            return 'Error: ' + response_json['message']
    else:
        return 'Response code: ' + str(response.status_code)
