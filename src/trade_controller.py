from time import sleep
import logging
import pendulum

from constants import (
    db_path,
    table_name,
    run_interval_in_seconds,
    trade_interval_in_seconds
)
from trade_config import config, stage_infos
from trade_service import TradeService


class TradeController:
    def __init__(self):
        self.service = TradeService()
        self.stocks = config['stocks']

    def setup(self):
        self.service.create_db(db_path)
        self.service.create_table(table_name)

    def init_stock(self, ticker: str):
        balance = self.service.get_balance(ticker)
        assert balance is not None

        row = self.service.database_processor.current_stage_row(table_name, ticker)

        if balance is not None and row is None:
            self.service.database_processor.init_new_stock(table_name,
                                                           ticker,
                                                           balance['ovrs_item_name'],
                                                           float(balance['pchs_avg_pric']),
                                                           int(balance['ord_psbl_qty']),
                                                           '0000000000',
                                                           stage_infos[ticker][0]['loss_to_buy'],
                                                           stage_infos[ticker][0]['profit_to_sell']
                                                           )
        return True

    def run(self):
        self.setup()
        while True:
            now = pendulum.now("Asia/Seoul")
            if pendulum.time(23, 30, 00) >= now.time() > pendulum.time(6, 00, 00):
                logging.info("장 개시 전 시각입니다.")
                sleep(run_interval_in_seconds)
                continue

            for s in self.stocks:
                ticker = s['ticker']
                exchange = s['exchange']
                budget_usd = s['budget_usd']

                self.init_stock(ticker)

                current_stage_row = self.service.database_processor.current_stage_row(table_name, ticker)
                current_price = self.service.current_price(exchange, ticker)
                logging.info(f'[{ticker}] 현재 차수: {current_stage_row["stage"]} 현재가: {current_price}')
                stage = current_stage_row['stage']

                # check 1
                purchasable_amount = self.service.get_purchasable_amount(exchange, ticker, current_price)
                should_buy_amount = budget_usd[stage] // current_price

                logging.info(f'사려고 하는 수량: {should_buy_amount}\t가능한 최대 수량: {purchasable_amount}')
                if should_buy_amount > purchasable_amount:
                    continue

                # check 2
                should_buy = self.service.should_buy(current_stage_row,
                                        should_buy_amount,
                                        current_price)

                if should_buy:
                    logging.info('매수 주문 체결 대기중입니다.')
                    buy_price = round(current_price * 1.005, 2)
                    output = self.service.buy(exchange, ticker, should_buy_amount, buy_price)
                    order_code = output['ODNO']
                    sleep(run_interval_in_seconds)
                    logging.info(f'매수 주문 번호: {order_code}')

                    transaction = self.service.search_traded_latest_order(ticker)
                    assert transaction['odno'] == order_code
                    stock_name = current_stage_row['stock_name']
                    buy_price = float(transaction['ft_ccld_unpr3'])
                    buy_amount = int(transaction['ft_ccld_qty'])
                    assert should_buy_amount == buy_amount
                    next_stage = current_stage_row['stage'] + 1
                    loss_to_buy = stage_infos[ticker][next_stage-1]['loss_to_buy']
                    profit_to_sell = stage_infos[ticker][next_stage-1]['profit_to_sell']

                    new_row = self.service.insert_buy_row(table_name,
                                                          ticker,
                                                          stock_name,
                                                          order_code,
                                                          buy_amount,
                                                          buy_price,
                                                          next_stage,
                                                          loss_to_buy,
                                                          profit_to_sell,
                                                          )
                    assert new_row is not None
                    continue

                should_sell = self.service.should_sell(current_stage_row, current_price)
                if should_sell:
                    sell_price = round(current_price * 0.995, 2)
                    logging.info(f'매도 주문 체결 대기중입니다. 가격: {sell_price}')
                    sell_amount = current_stage_row['amount']
                    output = self.service.sell(exchange, ticker, sell_amount, sell_price)

                    sell_order_code = output['ODNO']
                    sleep(run_interval_in_seconds)
                    logging.info(f'매도 주문 번호: {sell_order_code}')

                    transaction = self.service.search_traded_latest_order(ticker)
                    assert transaction['odno'] == sell_order_code

                    sell_price = float(transaction['ft_ccld_unpr3'])
                    sold_amount = int(transaction['ft_ccld_qty'])
                    assert sell_amount == sold_amount
                    net_profit = round(sell_amount * (sell_price - current_stage_row['buy_price']), 2)
                    buy_order_code = current_stage_row['buy_order_code']
                    logging.info(f"현재 차수{stage}의 매수 주문 번호: {buy_order_code}")

                    updated_row = self.service.update_row(table_name,
                                                          buy_order_code,
                                                          sell_order_code,
                                                          sell_price,
                                                          net_profit)
                    assert updated_row is not None

                sleep(trade_interval_in_seconds)
            sleep(run_interval_in_seconds)
