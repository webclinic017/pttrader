import datetime as dt
import time

# TODO лучше сделать кошелек трейдера отдельным csv файлом
TRADER_DEPOSIT = {"USD": 1000.,
                  "EUR": 1000.,
                  "RUR": 10000.,
                  }

NEW_ORDER_LIST = []


def trader_deposit_subtraction(currency, buy_order_price, amount):
    """
    This function subtract money from trader deposit by amount * buy_order_price BEFORE order complete at market
    :param currency: currency of order USD, RUR, etc
    :param buy_order_price:
    :param amount:
    :return: trader_deposit
    """
    global TRADER_DEPOSIT

    TRADER_DEPOSIT[currency] -= buy_order_price * amount

    print("return ", TRADER_DEPOSIT)
    pass


def trader_deposit_addition(currency, sell_order_price, amount):
    """
    This function add money to TRADER_DEPOSIT by amount * buy_order_price AFTER order complete at market
    :param currency: currency of order USD, RUR, etc
    :param sell_order_price:
    :param amount:
    :return: trader_deposit
    """
    global TRADER_DEPOSIT

    # order status must be DONE or SOLD

    TRADER_DEPOSIT[currency] += sell_order_price * amount

    print("return ", TRADER_DEPOSIT)
    pass


def order_buy_limit(ticker="UWGN", currency="RUR", buy_order_price=110.3, amount=1, created_at=dt.datetime.utcnow()):
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
    time.sleep(1)
    return order_data


def order_sell_limit(ticker="UWGN", currency="RUR", sell_order_price=110.3, amount=1, created_at=dt.datetime.utcnow()):
    """
    This function make order to sell amount of stocks by ticker name
    specified at sell_order_price and wait until market price of stock ticker reach
    sell_order_price
    :param currency:
    :param created_at:
    :param ticker: ticker name
    :param sell_order_price: price to buy ticker
    :param amount: number of stocks to buy
    :return: order_id #
    """

    order_data = [ticker, sell_order_price, amount, created_at]

    print("You place limit sell order ", ticker, "amount shares (!lots) is ", amount, "by price ",
          sell_order_price)
    trader_deposit_addition(currency, sell_order_price, amount)

    return order_data


def order_place_to_market(order_data):
    """
    Create order by individual id returned from buy_order_limit foo
    :param order_data:
    :param order_id:
    :return:
    """
    global NEW_ORDER_LIST

    NEW_ORDER_LIST.append(order_data)
    print("Order is placed", order_data)
    print("return ", NEW_ORDER_LIST)
    pass


def get_ticker_price(ticker):
    """
    This function get data from somewhere api and return ticker price

    """
    current_price = 120.
    print("Current price for ticker ", ticker, "price is ", current_price)
    return current_price  # return current price of the ticker


def check_order_status(order):
    """
    Checking ticker market price and order_price is will be meet conditions to buy:
    market_price is less or equal than order_price
    condition to to sell:
    market_price is greater or equal than order_price
    :param order:
    :return: True or False
    """
    ticker = order[0]
    market_price = get_ticker_price(ticker)
    order_price = order[1]
    order_status = False
    # condition for buy order
    print("Order status checking")
    if market_price >= order_price:
        print("mp>=op")
        order_status = True
        return order_status

    pass


def main():
    global NEW_ORDER_LIST
    #print(NEW_ORDER_LIST)
    while NEW_ORDER_LIST:
        for order in NEW_ORDER_LIST:
            print(order)
            order_status = check_order_status(order)
            if order_status:
                print("Order ", order, "status is True", )
                NEW_ORDER_LIST.remove(order)
                print(NEW_ORDER_LIST)

            else:
                print("Something goes wrong")
        if not NEW_ORDER_LIST:
            print("There are no new orders ",NEW_ORDER_LIST)

order_place_to_market(order_buy_limit())
order_place_to_market(order_buy_limit())
order_place_to_market(order_buy_limit())
#order_place_to_market(order_sell_limit())
main()