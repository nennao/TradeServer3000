import os
import pymysql
from sqlalchemy.engine.url import make_url


DB_URL = os.environ.get('CLEARDB_DATABASE_URL') or os.environ.get('LOCAL_DATABASE_URL')


class SQLConnection(object):
    def __init__(self, url=None):
        if not url:
            url = DB_URL
        self.url = make_url(url)

    def __enter__(self):
        self.db = pymysql.connect(
            db=self.url.database, host=self.url.host, user=self.url.username, password=self.url.password
        )
        self.cursor = self.db.cursor()
        return self

    def __exit__(self, *exc):
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()

    def get_account_balance(self, account_id):
        sql = f"SELECT BALANCE FROM ACCOUNTS WHERE ACCOUNT_ID='{account_id}';"
        self.cursor.execute(sql)
        balance, = self.cursor.fetchone()
        return balance

    def get_account_stock(self, account_id):
        sql = f"SELECT STOCK, QTY FROM STOCKS WHERE ACCOUNT_ID='{account_id}';"
        self.cursor.execute(sql)
        return {stock: qty for stock, qty in self.cursor.fetchall()}

    def get_account_trades(self, account_id):
        sql = f"SELECT * FROM TRADES WHERE ACCOUNT_ID='{account_id}' ORDER BY TRANSACTION_TS DESC;"
        self.cursor.execute(sql)
        cols = [item[0] for item in self.cursor.description]
        return [{col: value for col, value in zip(cols, row)} for row in self.cursor.fetchall()]

    def create_account(self, account_id):
        sql = f"INSERT INTO ACCOUNTS (ACCOUNT_ID) VALUES('{account_id}');"
        self.cursor.execute(sql)
        self.db.commit()

    def buy(self, account_id, stock, price, qty_bought, cash_required, new_balance, new_stock_qty):
        existing_stocks = self.get_account_stock(account_id).get(stock)
        if existing_stocks is None:
            stocks_sql = f"INSERT INTO STOCKS (ACCOUNT_ID, STOCK, QTY) VALUES ('{account_id}', '{stock}', {new_stock_qty})"
        else:
            stocks_sql = f"UPDATE STOCKS SET QTY={new_stock_qty} WHERE ACCOUNT_ID='{account_id}' AND STOCK='{stock}'"

        accounts_sql = f"UPDATE ACCOUNTS SET BALANCE={new_balance} WHERE ACCOUNT_ID='{account_id}'"
        trades_sql = (
            "INSERT INTO TRADES "
            "(ACCOUNT_ID, STOCK, QTY, PRICE, ABS_AMOUNT, BUY) "
            f"VALUES ('{account_id}', '{stock}', {qty_bought}, {price}, {cash_required}, 1)"
        )
        try:
            self.cursor.execute(stocks_sql)
            self.cursor.execute(accounts_sql)
            self.cursor.execute(trades_sql)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    # TODO see if can be refactored to prevent the duplication between buy and sell
    def sell(self, account_id, stock, price, qty_sold, cash_value, new_balance, new_stock_qty):
        stocks_sql = f"UPDATE STOCKS SET QTY={new_stock_qty} WHERE ACCOUNT_ID='{account_id}' AND STOCK='{stock}'"
        accounts_sql = f"UPDATE ACCOUNTS SET BALANCE={new_balance} WHERE ACCOUNT_ID='{account_id}'"
        trades_sql = (
            "INSERT INTO TRADES "
            "(ACCOUNT_ID, STOCK, QTY, PRICE, ABS_AMOUNT, BUY) "
            f"VALUES ('{account_id}', '{stock}', {qty_sold}, {price}, {cash_value}, 0)"
        )
        try:
            self.cursor.execute(stocks_sql)
            self.cursor.execute(accounts_sql)
            self.cursor.execute(trades_sql)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
