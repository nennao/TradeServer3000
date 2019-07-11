import time
from math import sin

STOCKS = (
    'StockA',
    'StockB',
)


def get_stock_prices():
    results = {}
    for i, s in enumerate(STOCKS):
        results[s] = round(compute_price(i), 3)
    return results


def compute_price(i):
    now = int(time.time()) - 1500000000
    d = now / 300.0
    return 4 + (
        sin(2*(d+i)) / 2 +
        sin(3*(d+i)) / 3 +
        sin(5*(d+i)) / 4 +
        sin(7*(d+i)) / 5 +
        sin(11*(d+i)) / 6 +
        sin(13*(d+i)) / 7 +
        sin(17*(d+i)) / 8 +
        sin(19*(d+i)) / 9
    )
