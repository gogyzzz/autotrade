
import requests

from constants import base_url
from secrets import app_key, app_secret, token


class OverseaPriceProcessor:
    def __init__(self):
        pass

    def get_current_price(self, exchange: str, ticker: str):
        if exchange == 'NYSE' or exchange == 'NASD':
            exchange = exchange[:3]

        url = f"{base_url}/uapi/overseas-price/v1/quotations/price"
        headers = {"Content-Type": "application/json",
                   "authorization": f"Bearer {token}",
                   "appKey": app_key,
                   "appSecret": app_secret,
                   "tr_id": "HHDFS00000300"}

        params = {
            "AUTH": "",
            "EXCD": exchange,
            "SYMB": ticker
        }

        res = requests.get(url, headers=headers, params=params)

        assert int(res.json()['rt_cd']) == 0
        price = float(res.json()['output']['last'])

        return price
