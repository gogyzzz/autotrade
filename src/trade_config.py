import json
import logging
import os.path
from constants import log_path, config_path


class TradeConfig:
    def __init__(self, config: str):
        with open(config) as f:
            self.data = json.load(f)
        self.validate_config()
        self.stage_infos = {
            stock['ticker']: self.get_stage_info(stock)
            for stock in self.data['stocks']
        }
        self.export_stage_info()

    def get_config(self):
        return self.data

    def get_stage_infos(self):
        return self.stage_infos

    def validate_config(self):
        account_id, account_product_code = self.data["account"].split('-')
        assert len(account_id) == 8
        assert len(account_product_code) == 2
        assert len(self.data["stocks"]) > 0
        for stock in self.data["stocks"]:
            assert len(stock["budget_usd"]) == 6
            assert len(stock["loss_to_buy"]) == 7
            for l in stock["loss_to_buy"]:
                assert l <= 0
            self.validate_profit_to_sell(stock["profit_to_sell"])

    def validate_profit_to_sell(self, profit_to_sell):
        assert len(profit_to_sell) == 7
        for l in profit_to_sell:
            assert l > 0

    def get_stage_info(self, stock: dict):
        loss_to_buy = stock['loss_to_buy']
        profit_to_sell = stock['profit_to_sell']

        stages = []
        for profit, loss in zip(profit_to_sell, loss_to_buy):
            stages.append({
                    'loss_to_buy': loss,
                    'profit_to_sell': profit
                })

        return stages

    def export_stage_info(self):
        for stock in self.data['stocks']:
            stage_info_path = f"tmp/stage_info/{stock['ticker'].replace('/', '_')}.json"
            stage_info = self.get_stage_info(stock)
            if os.path.exists(stage_info_path):
                os.remove(stage_info_path)
            os.makedirs(os.path.dirname(stage_info_path), exist_ok=True)
            with open(stage_info_path, 'w') as f:
                f.write(json.dumps(stage_info, indent=4))


FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=log_path, encoding='utf-8', level=logging.INFO, format=FORMAT)

trade_config = TradeConfig(config_path)
config = trade_config.get_config()
stage_infos = trade_config.get_stage_infos()
