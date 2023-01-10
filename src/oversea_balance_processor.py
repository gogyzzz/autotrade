import json
import pendulum
import requests
import logging

from secrets import app_key, app_secret, token
from constants import base_url


class OverseaBalanceProcessor:
    def __init__(self):
        pass

    # https://apiportal.koreainvestment.com/apiservice/apiservice-overseas-stock#L_0482dfb1-154c-476c-8a3b-6fc1da498dbf
    def get_balance(self,
               account_id: str,
               account_product_code: str,
               ticker: str):

        url = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-balance"

        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}",
            "appKey": app_key,
            "appSecret": app_secret,
            "tr_id": "JTTT3012R"
        }

        params = {
            "CANO": account_id,
            "ACNT_PRDT_CD": account_product_code,
            "OVRS_EXCG_CD": "NASD",  # 미국 전체
            "TR_CRCY_CD": "USD",
            "CTX_AREA_NK200": "",
            "CTX_AREA_FK200": ""
        }

        res = requests.get(url, headers=headers, params=params)

        assert int(res.json()['rt_cd']) == 0
        output = res.json()['output1']
        tickers = [o['ovrs_pdno'] for o in output]
        assert ticker in tickers
        return list(filter(lambda o: ticker == o['ovrs_pdno'], output))[0]
