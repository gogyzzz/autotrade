import sqlite3
import os
import pendulum
import logging
from typing import Optional


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


class DatabaseProcessor:
    def __init__(self):
        self.db_path = None
        self.con = None
        self.cursor = None

    def create_db(self, db_path: str):
        if not os.path.exists(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.con = sqlite3.connect(db_path)
        self.con.row_factory = dict_factory
        self.cursor = self.con.cursor()
        return self.db_path

    def create_table(self, table_name: str):
        query = (f"CREATE TABLE IF NOT EXISTS {table_name} ("
                 f"ticker, "
                 f"stock_name, "
                 f"buy_order_code, "
                 f"amount, "
                 f"buy_price, "
                 
                 f"stage, "
                 f"loss_to_buy, "
                 f"should_buy_price, "
                 f"profit_to_sell, "
                 f"should_sell_price, "
                 
                 f"sell_order_code, "
                 f"sell_price, "
                 f"net_profit, "
                 f"created_at, "
                 f"modified_at)")
        self.cursor.execute(query)
        res = self.cursor.execute("SELECT name FROM sqlite_master")
        table_names = res.fetchall()
        assert table_name in [t['name'] for t in table_names]
        return table_names

    def delete_table(self, table_name: str):
        query = f"DROP TABLE {table_name}"
        self.cursor.execute(query)
        res = self.cursor.execute("SELECT name FROM sqlite_master")
        table_names = res.fetchall()
        return table_names

    def insert_row(self, table_name: str,
                   ticker: str,
                   stock_name: str,
                   buy_order_code: str,
                   amount: int,
                   buy_price: float,

                   stage: int,
                   loss_to_buy: float,
                   should_buy_price: float,
                   profit_to_sell: float,
                   should_sell_price: float,

                   sell_order_code: Optional[str],
                   sell_price: Optional[float],
                   net_profit: Optional[float]):

        created_at = pendulum.now("Asia/Seoul").to_datetime_string()
        modified_at = created_at
        data = [
            (ticker,
             stock_name,
             buy_order_code,
             amount,
             buy_price,

             stage,
             loss_to_buy,
             should_buy_price,
             profit_to_sell,
             should_sell_price,

             sell_order_code,
             sell_price,
             net_profit,
             created_at,
             modified_at),
        ]
        query = (f"INSERT INTO {table_name}("
                 f"ticker, "
                 f"stock_name, "
                 f"buy_order_code, "
                 f"amount, "
                 f"buy_price, "
                 
                 f"stage, "
                 f"loss_to_buy, "
                 f"should_buy_price, "
                 f"profit_to_sell, "
                 f"should_sell_price, "
                 
                 f"sell_order_code, "
                 f"sell_price, "
                 f"net_profit, "
                 f"created_at, "
                 f"modified_at) "
                 f"VALUES("
                 f"?, ?, ?, ?, ?, "
                 f"?, ?, ?, ?, ?, "
                 f"?, ?, ?, ?, ?)")

        self.cursor.executemany(query, data)
        self.con.commit()
        query = (f"SELECT * "
                 f"FROM {table_name} "
                 f"WHERE buy_order_code = '{buy_order_code}'")
        res = self.cursor.execute(query)
        new_row = res.fetchone()

        assert new_row is not None
        return new_row

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

        should_buy_price = round(buy_price * (1 + loss_to_buy), 2)
        should_sell_price = round(buy_price * (1 + profit_to_sell), 2)

        new_row = self.insert_row(table_name=table_name,

                                  ticker=ticker,
                                  stock_name=stock_name,
                                  buy_order_code=buy_order_code,
                                  amount=amount,
                                  buy_price=buy_price,

                                  stage=stage,
                                  loss_to_buy=loss_to_buy,
                                  should_buy_price=should_buy_price,
                                  profit_to_sell=profit_to_sell,
                                  should_sell_price=should_sell_price,

                                  sell_order_code=None,
                                  sell_price=None,
                                  net_profit=None
                                  )
        return new_row

    def update_row(self,
                   table_name: str,
                   buy_order_code: str,
                   sell_order_code: str,
                   sell_price: float,
                   net_profit: float,
                   ):
        modified_at = pendulum.now("Asia/Seoul").to_datetime_string()
        query = (f"UPDATE {table_name} SET "
                 f"sell_order_code = '{sell_order_code}', "
                 f"sell_price = {sell_price}, "
                 f"net_profit = {net_profit},"
                 f"modified_at = '{modified_at}' "
                 f"WHERE buy_order_code = '{buy_order_code}'")
        self.cursor.execute(query)
        self.con.commit()
        res = self.cursor.execute(f""
                                  f"SELECT * "
                                  f"FROM {table_name} "
                                  f"WHERE sell_order_code = '{sell_order_code}'")

        updated_row = res.fetchone()
        assert updated_row
        return updated_row

    def init_new_stock(self,
                       table_name: str,
                       ticker: str,
                       stock_name: str,
                       average_price: float,
                       amount: int,
                       buy_order_code: str,
                       loss_to_buy: float,
                       profit_to_sell: float):
        new_row = self.insert_buy_row(table_name=table_name,
                                      ticker=ticker,
                                      stock_name=stock_name,
                                      buy_order_code=buy_order_code,
                                      amount=amount,
                                      buy_price=average_price,
                                      stage=1,
                                      loss_to_buy=loss_to_buy,
                                      profit_to_sell=profit_to_sell,
                                      )
        return new_row

    def current_stage_row(self,
                          table_name: str,
                          ticker: str):
        query = (f"SELECT * "
                 f"FROM {table_name} "
                 f"WHERE ticker = '{ticker}' "
                 f"AND sell_price IS NULL "
                 f"AND sell_order_code IS NULL "
                 f"AND net_profit IS NULL "
                 f"ORDER BY buy_order_code DESC")
        res = self.cursor.execute(query)
        current_stage_row = res.fetchone()
        return current_stage_row

    def finished_stage_rows(self,
                            table_name: str,
                            ticker: str,
                            start_date: str,
                            end_date: str):
        query = (f"SELECT * "
                 f"FROM {table_name} "
                 f"WHERE ticker = '{ticker}' "
                 f"AND sell_price > 0.0 "
                 f"AND sell_order_code IS NOT NULL "
                 f"AND net_profit > 0.0 "
                 f"AND created_at >= '{start_date}' "
                 f"AND modified_at <= '{end_date}' "
                 f"ORDER BY buy_order_code DESC")

        res = self.cursor.execute(query)
        rows = res.fetchall()
        return rows
