import json
import pendulum
import requests
import logging

from secrets import app_key, app_secret, token
from constants import base_url


class OverseaTransactionProcessor:
    def __init__(self):
        pass

    # https://apiportal.koreainvestment.com/apiservice/apiservice-overseas-stock#L_6d715b38-566f-4045-a08c-4a594d3a3314
    def search(self,
               account_id: str,
               account_product_code: str,
               ticker: str):

        url = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-ccnl"

        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}",
            "appKey": app_key,
            "appSecret": app_secret,
            "tr_id": "JTTT3001R"
        }

        start_date = pendulum.date(2022, 1, 1).format('YYYYMMDD')
        end_date = pendulum.now("Asia/Seoul").format('YYYYMMDD')

        params = {
            "CANO": account_id,
            "ACNT_PRDT_CD": account_product_code,
            "PDNO": ticker,
            "ORD_STRT_DT": start_date,
            "ORD_END_DT": end_date,
            "SLL_BUY_DVSN": "00",  # sell buy 전부
            "CCLD_NCCS_DVSN": "01",  # 체결 미체결 전부
            "OVRS_EXCG_CD": "%",  # 거래소 전부
            "SORT_SQN": "AS",  # 정렬 방향 (DS: 정방향, AS: 역방향)
            "ORD_DT": "",
            "ORD_GNO_BRNO": "",
            "ODNO": "",
            "CTX_AREA_NK200": "",
            "CTX_AREA_FK200": ""
        }

        res = requests.get(url, headers=headers, params=params)

        assert int(res.json()['rt_cd']) == 0
        return res.json()['output']

    def search_not_traded(self,
        account_id: str,
        account_product_code: str,
        ticker: str):

        url = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-nccs"

        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}",
            "appKey": app_key,
            "appSecret": app_secret,
            "tr_id": "JTTT3018R"
        }

        params = {
            "CANO": account_id,
            "ACNT_PRDT_CD": account_product_code,
            "OVRS_EXCG_CD": "%",  # 거래소 전부
            "SORT_SQN": "AS",  # 정렬 방향 (DS: 정방향, AS: 역방향)
            "CTX_AREA_NK200": "",
            "CTX_AREA_FK200": ""
        }

        res = requests.get(url, headers=headers, params=params)

        assert int(res.json()['rt_cd']) == 0
        return res.json()['output']


