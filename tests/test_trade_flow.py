import os.path
import unittest
from trade_service import TradeService


class TestTradeFlow(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TradeService()
        self.test_DB_생성()
        self.test_테이블_생성()
        self.test_테이블_제거()
        self.test_테이블_생성()

    def test_특정주식의_마지막_체결기록_조회(self):
        transaction = self.service.search_traded_latest_order(ticker='PBR/A')
        self.assertIsNotNone(transaction)
        transaction = self.service.search_traded_latest_order(ticker='APPL')
        self.assertIsNone(transaction)

    def test_특정주식의_잔고_조회(self):
        ticker = 'PBR/A'
        balance = self.service.get_balance(ticker)
        self.assertEqual(balance['ovrs_pdno'], ticker)

    def test_특정주식의_현재가_조회(self):
        price = self.service.current_price(exchange='NYS', ticker='PBR/A')
        self.assertGreater(price, 7.00)
        self.assertLess(price, 10.00)

    def test_구매가능한_수량(self):
        purchasable_amount = self.service.get_purchasable_amount(exchange='NYSE', ticker='PBR/A', price=8.80)
        self.assertGreaterEqual(purchasable_amount, 1)
        purchasable_amount = self.service.get_purchasable_amount(exchange='NASD', ticker='AAPL', price=120.80)
        self.assertEqual(purchasable_amount, 0)

    def test_설정정보_불러오기(self):
        config = self.service.get_config()
        self.assertIsNotNone(config)

    def test_DB_생성(self):
        db_path = 'tmp/test.db'
        db_path = self.service.create_db(db_path)
        self.assertTrue(os.path.exists(db_path))

    def test_테이블_생성(self):
        table_name = 'orders'
        table_names = self.service.create_table(table_name=table_name)

        self.assertIn(table_name, [t['name'] for t in table_names])

    def test_테이블_제거(self):
        table_name = 'orders'
        table_names = self.service.delete_table(table_name=table_name)
        self.assertNotIn(table_name, [t['name'] for t in table_names])

    def test_DB_초기화(self):
        # 주식잔고의 평균단가를 가져와서 BUY 타입으로 세팅

        table_name = 'orders'
        ticker = 'AAPL'
        stock_name = 'apple'
        average_price = 8.9
        amount = 10
        buy_order_code = '00000000'
        loss_to_buy = -0.05
        profit_to_sell = 1.00
        new_row = self.service.init_new_stock(table_name=table_name,
                                              ticker=ticker,
                                              stock_name=stock_name,
                                              average_price=average_price,
                                              amount=amount,
                                              buy_order_code=buy_order_code,
                                              loss_to_buy=loss_to_buy,
                                              profit_to_sell=profit_to_sell
                                              )
        self.assertEqual(new_row['ticker'], "AAPL")
        self.assertEqual(new_row['buy_price'] * (1 + loss_to_buy),  new_row['should_buy_price'])
        self.assertEqual(new_row['buy_price'] * (1 + profit_to_sell), new_row['should_sell_price'])

    def test_현재_차수_정보(self):
        self.test_DB_초기화()
        table_name = 'orders'
        ticker = 'AAPL'
        row = self.service.current_stage_row(table_name=table_name,
                                             ticker=ticker)
        self.assertEqual(row['stage'], 1)
        
    def test_현재가_기준_매수_판단(self):
        self.test_DB_초기화()
        table_name = 'orders'
        ticker = 'AAPL'
        current_price = 7.00
        purchasable_amount = 1
        current_stage_row = self.service.current_stage_row(table_name=table_name,
                                                           ticker=ticker)
        should_buy = self.service.should_buy(row=current_stage_row,
                                             purchasable_amount=purchasable_amount,
                                             current_price=current_price)
        self.assertEqual(should_buy, True)

        current_price = 9.00
        should_buy = self.service.should_buy(row=current_stage_row,
                                             purchasable_amount=purchasable_amount,
                                             current_price=current_price)
        self.assertEqual(should_buy, False)

    def test_현재가_기준_매도_판단(self):
        self.test_DB_초기화()
        table_name = 'orders'
        ticker = 'AAPL'
        current_price = 7.00
        current_stage_row = self.service.current_stage_row(table_name=table_name,
                                                           ticker=ticker)
        should_sell = self.service.should_sell(row=current_stage_row,
                                               current_price=current_price)
        self.assertEqual(should_sell, False)

        current_price = 20.0
        should_sell = self.service.should_sell(row=current_stage_row,
                                               current_price=current_price)
        self.assertEqual(should_sell, True)

    def test_추가_매수_기록(self):
        self.test_DB_초기화()
        table_name = 'orders'
        ticker = 'AAPL'
        current_price = 7.00
        purchasable_amount = 1
        current_stage_row = self.service.current_stage_row(table_name=table_name,
                                                           ticker=ticker)
        should_buy = self.service.should_buy(row=current_stage_row,
                                             purchasable_amount=purchasable_amount,
                                             current_price=current_price)
        self.assertEqual(should_buy, True)

        # 시장가 매수 주문
        buy_price = 7.01
        next_stage = current_stage_row['stage'] + 1
        buy_order_code = '00000001'
        stock_name = 'apple'
        loss_to_buy = -0.05
        profit_to_sell = 0.03

        new_row = self.service.insert_buy_row(table_name,
                                              ticker,
                                              stock_name,
                                              buy_order_code,
                                              purchasable_amount,
                                              buy_price,
                                              next_stage,
                                              loss_to_buy,
                                              profit_to_sell,
                                              )
        self.assertEqual(round(new_row['buy_price'] * (1 + loss_to_buy), 2),  new_row['should_buy_price'])
        self.assertEqual(round(new_row['buy_price'] * (1 + profit_to_sell), 2), new_row['should_sell_price'])
        self.assertGreater(new_row['stage'], current_stage_row['stage'])

    def test_매도_주문_기록(self):
        self.test_DB_초기화()
        table_name = 'orders'
        ticker = 'AAPL'
        current_price = 20.0
        current_stage_row = self.service.current_stage_row(table_name=table_name,
                                                           ticker=ticker)
        should_sell = self.service.should_sell(row=current_stage_row,
                                               current_price=current_price)
        self.assertEqual(should_sell, True)

        # 시장가 매도 체결
        sell_price = 19.0
        sell_order_code = '00000003'
        net_profit = round(sell_price - current_stage_row['buy_price'], 2)  # 수수료 안맞을 거긴 하지만 여튼,

        finished_row = self.service.update_row(table_name,
                                               sell_order_code,
                                               sell_price,
                                               net_profit,
                                               )
        self.assertEqual(finished_row['net_profit'], net_profit)

    def test_완료된_차수_조회(self):
        self.test_추가_매수_기록()
        table_name = 'orders'
        ticker = 'AAPL'
        start_date = '2023-01-01'
        end_date = '2023-01-31'
        finished_rows = self.service.finished_stage_rows(table_name=table_name,
                                                         ticker=ticker,
                                                         start_date=start_date,
                                                         end_date=end_date)
        self.assertEqual(len(finished_rows), 0)

        self.test_테이블_제거()
        self.test_테이블_생성()
        self.test_매도_주문_기록()
        finished_rows = self.service.finished_stage_rows(table_name=table_name,
                                                         ticker=ticker,
                                                         start_date=start_date,
                                                         end_date=end_date)
        self.assertEqual(len(finished_rows), 1)


if __name__ == '__main__':
    unittest.main()
