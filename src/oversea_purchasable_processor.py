import requests

from constants import base_url
from secrets import app_key, app_secret, token


class OverseaPurchasableProcessor:
    def get_purchasable_amount(self, account_id: str, account_product_code: str, exchange: str, ticker: str, price: float) -> int:
        url = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-psamount"
        headers = {"Content-Type": "application/json",
                   "authorization": f"Bearer {token}",
                   "appKey": app_key,
                   "appSecret": app_secret,
                   "tr_id": "JTTT3007R"}

        params = {
            "CANO": account_id,
            "ACNT_PRDT_CD": account_product_code,
            "OVRS_EXCG_CD": exchange,
            "OVRS_ORD_UNPR": str(price),
            "ITEM_CD": ticker,
        }

        res = requests.get(url, headers=headers, params=params)

        assert int(res.json()['rt_cd']) == 0
        # 달러만 고려
        # purchasable_quantity = float(res.json()['output']['ord_psbl_qty'])
        # 원화, 달러 통합
        purchasable_quantity = int(res.json()['output']['ovrs_max_ord_psbl_qty'])

        return purchasable_quantity
