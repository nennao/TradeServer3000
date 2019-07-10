from flask import Flask, request, jsonify
from flask_cors import CORS
from mysql_utils import SQLConnection
from price_utils import STOCKS, get_stock_prices


app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return '<h1>Welcome to Trade Server 3000!</h1>'


@app.route("/prices", methods=["GET"])
def get_prices():
    return jsonify(get_stock_prices())


@app.route("/options", methods=["GET"])
def get_options():
    return jsonify(STOCKS)


@app.route("/position", methods=["GET"])
def get_position():
    account_id = request.args["accountId"]

    with SQLConnection() as db:
        try:
            balance = db.get_account_balance(account_id)
        except TypeError:
            return jsonify(f"Account not found: {account_id}"), 404

        stock = db.get_account_stock(account_id)

    return jsonify({
        "balance": balance,
        "stock": stock,
    })


@app.route("/trades", methods=["GET"])
def get_trades():
    account_id = request.args["accountId"]

    with SQLConnection() as db:
        trades = db.get_account_trades(account_id)
    return jsonify(trades)


@app.route("/create_account", methods=["POST"])
def create_account():
    account_id = request.args["accountId"]
    try:
        with SQLConnection() as db:
            db.create_account(account_id)
        return 'OK', 200
    except Exception as e:
        print(e)
        return f'Something went wrong: {e}', 500


@app.route("/buy", methods=["POST"])
def post_buy():
    account_id = request.args["accountId"]
    stock = request.args["stock"]
    if stock not in STOCKS:
        return jsonify(f"Stock not found: {stock}"), 404

    try:
        amount = int(request.args["amount"])
    except Exception as e:
        print(e)
        return jsonify("Amount should be an integer"), 400

    with SQLConnection() as db:
        try:
            balance = db.get_account_balance(account_id)
        except TypeError:
            return jsonify(f"Account not found: {account_id}"), 404

        try:
            price = get_stock_prices()[stock]
            cash_required = amount * price

            if balance < cash_required:
                return jsonify(f"Not enough cash! (amount required: {cash_required}, your balance: {balance})"), 400

            print(f"account: {account_id} buying {amount}...")
            stock_qty = db.get_account_stock(account_id).get(stock, 0)
            new_balance = balance - cash_required
            new_stock_qty = stock_qty + amount

            db.buy(account_id, stock, price, amount, cash_required, new_balance, new_stock_qty)
            return jsonify("buy order was successful!"), 200
        except Exception as e:
            print(e)
            return f'Something went wrong :( Error: {e}', 500


@app.route("/sell", methods=["POST"])  # TODO see if can refactor the duplication between buy and sell
def post_sell():
    account_id = request.args["accountId"]
    stock = request.args["stock"]
    if stock not in STOCKS:
        return jsonify(f"Stock not found: {stock}"), 404

    try:
        amount = int(request.args["amount"])
    except Exception as e:
        print(e)
        return jsonify("Amount should be an integer"), 400

    with SQLConnection() as db:
        try:
            balance = db.get_account_balance(account_id)
        except TypeError:
            return jsonify(f"Account not found: {account_id}"), 404

        try:
            price = get_stock_prices()[stock]
            stock_qty = db.get_account_stock(account_id).get(stock, 0)

            if stock_qty < amount:
                return jsonify(f"Not enough stocks! (amount required: {amount}, your stock quantity: {stock_qty})"), 400

            print(f"account: {account_id} selling {amount}...")
            cash_value = amount * price
            new_balance = balance + cash_value
            new_stock_qty = stock_qty - amount

            db.sell(account_id, stock, price, amount, cash_value, new_balance, new_stock_qty)
            return jsonify("sell order was successful!"), 200
        except Exception as e:
            print(e)
            return f'Something went wrong :( Error: {e}', 500


if __name__ == '__main__':
    app.run()
