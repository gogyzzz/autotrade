import logging
import json
import requests

from order_processor import OrderProcessor
from constants import base_url, trade_id
from secrets import app_key, app_secret, token


# https://apiportal.koreainvestment.com/apiservice/apiservice-overseas-stock#L_e4a7e5fd-eed5-4a85-93f0-f46b804dae5f
class OverseaOrderProcessor(OrderProcessor):
    def __init__(self):
        # dollar
        self.max_sell_price = 1000
        self.max_buy_price = 1000

    def create_sell_request_body(self,
                                account_number: str,
                                account_product_code: str,
                                exchange: str,
                                ticker: str,
                                amount: int,
                                price: float):

        return {
            "CANO": account_number,
            "ACNT_PRDT_CD": account_product_code,
            "OVRS_EXCG_CD": exchange,
            "PDNO": ticker,
            "ORD_QTY": str(amount),
            "OVRS_ORD_UNPR": "0" if price == 0.0 else "%.02f"%(price),
            "SLL_TYPE": "00",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "03" # 최유리 지정가
        }

    def sell(self,
             request_body: dict,
             hash_key: str
             ):
        url = f"{base_url}/uapi/overseas-stock/v1/trading/order"

        headers = {"Content-Type": "application/json",
                   "authorization": f"Bearer {token}",
                   "appKey": app_key,
                   "appSecret": app_secret,
                   "tr_id": trade_id["미국 매도 주문"],
                   "hashkey": hash_key}

        result = requests.post(url, headers=headers, data=json.dumps(request_body))
        if int(result.json()['rt_cd']) != 0:
            logging.info(json.dumps(request_body, ensure_ascii=False))
            logging.info(json.dumps(result.json(), ensure_ascii=False))
            assert int(result.json()['rt_cd']) == 0
        return result.json()['output']

    def create_buy_request_body(self,
                                account_number: str,
                                account_product_code: str,
                                exchange: str,
                                ticker: str,
                                amount: int,
                                price: float):

        return {
            "CANO": account_number,
            "ACNT_PRDT_CD": account_product_code,
            "OVRS_EXCG_CD": exchange,
            "PDNO": ticker,
            "ORD_QTY": str(int(amount)),
            "OVRS_ORD_UNPR": "0" if price == 0.0 else "%.02f"%(price),
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "00"
        }

    def buy(self,
            request_body: dict,
            hash_key: str
            ):
        url = f"{base_url}/uapi/overseas-stock/v1/trading/order"

        headers = {
                   "content-type": "application/json",
                   "authorization": f"Bearer {token}",
                   "appkey": app_key,
                   "appsecret": app_secret,
                   "tr_id": "JTTT1002U", #trade_id["미국 매수 주문"],
                   "hashkey": hash_key}

        result = requests.post(url, headers=headers, data=json.dumps(request_body))
        if int(result.json()['rt_cd']) != 0:
            logging.info(json.dumps(request_body, ensure_ascii=False))
            logging.info(json.dumps(result.json(), ensure_ascii=False))
            assert int(result.json()['rt_cd']) == 0
        return result.json()['output']
