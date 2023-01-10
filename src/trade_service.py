
from trade_config import config
from oversea_transaction_processor import OverseaTransactionProcessor
from oversea_order_processor import OverseaOrderProcessor
from hashkey_processor import HashKeyProcessor
from oversea_price_processor import OverseaPriceProcessor
from oversea_purchasable_processor import OverseaPurchasableProcessor
from database_processor import DatabaseProcessor
from oversea_decision_processor import OverseaDecisionProcessor
from oversea_balance_processor import OverseaBalanceProcessor
from utils import parse_account


account_id, account_product_code = parse_account(config['account'])


class TradeService:
    def __init__(self):
        self.hash_key_processor = HashKeyProcessor()
        self.transaction_processor = OverseaTransactionProcessor()
        self.balance_processor = OverseaBalanceProcessor()
        self.order_processor = OverseaOrderProcessor()
        self.price_processor = OverseaPriceProcessor()
        self.purchasable_processor = OverseaPurchasableProcessor()
        self.database_processor = DatabaseProcessor()
        self.decision_processor = OverseaDecisionProcessor()

    def search_traded_latest_order(self, ticker: str):
        results = self.transaction_processor.search(account_id, account_product_code, ticker)
        if results:
            return results[0]
        else:
            return None

    def search_not_traded_latest_order(self, ticker: str):
        results = self.transaction_processor.search_not_traded(account_id, account_product_code, ticker)
        matches = list(filter(lambda _r: _r['pdno'] == ticker, results))
        if matches:
            return sorted(matches, key=lambda d: d['odno'])[0]
        else:
            return None

    def get_balance(self, ticker):
        return self.balance_processor.get_balance(account_id, account_product_code, ticker)

    def current_price(self, exchange: str, ticker: str):
        price = self.price_processor.get_current_price(exchange, ticker)
        return price

    def get_purchasable_amount(self, exchange: str, ticker: str, price: float) -> int:
        return self.purchasable_processor.get_purchasable_amount(account_id, account_product_code, exchange, ticker, price)

    def get_config(self):
        return config

    def create_db(self, db_path: str):
        db_path = self.database_processor.create_db(db_path)
        return db_path

    def create_table(self, table_name: str):
        table_names = self.database_processor.create_table(table_name)
        return table_names

    def delete_table(self, table_name: str):
        table_names = self.database_processor.delete_table(table_name)
        return table_names

    def init_new_stock(self,
                       table_name: str,
                       ticker: str,
                       stock_name: str,
                       average_price: float,
                       amount: int,
                       buy_order_code: str,
                       loss_to_buy: float,
                       profit_to_sell: float,
                       ):
        return self.database_processor.init_new_stock(
            table_name=table_name,
            ticker=ticker,
            stock_name=stock_name,
            average_price=average_price,
            amount=amount,
            buy_order_code=buy_order_code,
            loss_to_buy=loss_to_buy,
            profit_to_sell=profit_to_sell
        )

    def current_stage_row(self, table_name: str, ticker: str):
        return self.database_processor.current_stage_row(table_name=table_name,
                                                         ticker=ticker)
    
    def should_buy(self, row: dict, purchasable_amount: int, current_price: float):
        return self.decision_processor.should_buy(row, purchasable_amount, current_price)

    def should_sell(self, row: dict, current_price: float):
        return self.decision_processor.should_sell(row, current_price)

    def insert_buy_row(self,
                       table_name: str,
                       ticker: str,
                       stock_name: str,
                       buy_order_code: str,
                       amount: int,
                       buy_price: float,
                       stage: int,
                       loss_to_buy: float,
                       profit_to_sell: float,
                       ):
        return self.database_processor.insert_buy_row(table_name,
                                                      ticker,
                                                      stock_name,
                                                      buy_order_code,
                                                      amount,
                                                      buy_price,
                                                      stage,
                                                      loss_to_buy,
                                                      profit_to_sell,
                                                      )

    def update_row(self,
                   table_name: str,
                   buy_order_code: str,
                   sell_order_code: str,
                   sell_price: float,
                   net_profit: float,
                   ):
        return self.database_processor.update_row(table_name, buy_order_code, sell_order_code, sell_price, net_profit)

    def finished_stage_rows(self,
                            table_name: str,
                            ticker: str,
                            start_date: str,
                            end_date: str):
        return self.database_processor.finished_stage_rows(table_name, ticker, start_date, end_date)

    def buy(self, exchange: str, ticker: str, amount: int, price: float):
        request_body = self.order_processor.create_buy_request_body(account_id, account_product_code, exchange, ticker, amount, price)
        hash_key = self.hash_key_processor.to_hash(request_body)
        result = self.order_processor.buy(request_body, hash_key)
        return result
    def sell(self, exchange: str, ticker: str, amount: int, price: float):
        request_body = self.order_processor.create_sell_request_body(account_id, account_product_code, exchange, ticker, amount, price)
        hash_key = self.hash_key_processor.to_hash(request_body)
        result = self.order_processor.sell(request_body, hash_key)
        return result


