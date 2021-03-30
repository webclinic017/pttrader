import datetime as dt

# TODO лучше сделать кошелек трейдера отдельным csv файлом
TRADER_DEPOSIT = {"USD": 1000.,
                  "EUR": 1000.,
                  "RUR": 10000.,
                  }


def trader_deposit_subtraction(currency, buy_order_price, amount):
    """

    :param currency:
    :param buy_order_price:
    :param amount:
    :return:
    """
    global TRADER_DEPOSITd

    TRADER_DEPOSIT[currency] -= buy_order_price * amount

    print(TRADER_DEPOSIT)
    pass


def buy_order_limit(ticker="UWGN", currency="RUR", buy_order_price=110.3, amount=1, created_at=dt.datetime.utcnow()):
    """
    This function make order to buy amount of stocks by ticker name
    specified at buy_order_price and wait until market price of stock ticker reach
    buy_order_price
    :param currency:
    :param created_at:
    :param ticker: ticker name
    :param buy_order_price: price to buy ticker
    :param amount: number of stocks to buy
    :return: order_id
    """

    order_data = [ticker, buy_order_price, amount, created_at]

    print("You place limit buy order ", ticker, "amount shares (!lots) is ", amount, "by price ",
          buy_order_price)
    trader_deposit_subtraction(currency, buy_order_price, amount)

    return order_data


def place_order_to_market(order_data):
    """
    Create order by individual id returned from buy_order_limit foo
    :param order_data:
    :param order_id:
    :return:
    """
    print("Order is placed", order_data)
    pass


def get_ticker_price(ticker):
    """
    This function get data from somewhere api and return ticker price

    """
    pass  # return ohlc price of the ticker


order_data = buy_order_limit()
place_order_to_market(order_data)
