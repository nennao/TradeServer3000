import time
from math import sin

STOCKS = (
    'StockA',
)


def get_stock_prices():
    results = {}
    for s in STOCKS:
        results[s] = compute_price()
    return results


def compute_price():
    now = int(time.time()) - 1500000000
    d = now / 600.0
    return 4 + (
        sin(2*d) / 2 +
        sin(3*d) / 3 +
        sin(5*d) / 4 +
        sin(7*d) / 5 +
        sin(11*d) / 6 +
        sin(13*d) / 7 +
        sin(17*d) / 8 +
        sin(19*d) / 9
    )
