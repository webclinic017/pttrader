import datetime as dt
import time
from random import randint

import login
import trader
import market

# TODO make trader deposit in csv file
TRADER_DEPOSIT = {"USD": 1000.,
                  "EUR": 1000.,
                  "RUR": 10000.,
                  }

NEW_ORDER_LIST = []
TRADING_HISTORY_LIST = []


def create_order_query(operation_type):
    """
    Get input parameters from trader:
    operation type: Buy or Sell from main cycle
    ticker
    buy_order_price
    sell_order_price
    amount
    created_at
    :return: order query
    """


    print("Enter ticker name:")
    ticker = str(input())
    if operation_type == "Buy":
        print("Enter price for Buy operation:")
        buy_order_price = float(input())
        print("Enter amount in lot's:")
        amount = int(input())
        created_at = dt.datetime.utcnow()
        order_query = [operation_type, ticker, buy_order_price, amount, created_at]
        print("You create order query: ", order_query)
        return order_query

    elif operation_type == "Sell":
        print("Enter price for Sell operation:")
        sell_order_price = float(input())
        print("Enter amount in lot's:")
        amount = int(input())
        created_at = dt.datetime.utcnow()
        order_query = [operation_type, ticker, sell_order_price, amount, created_at]
        print("You create order query: ", order_query)
        return order_query

    else:
        print("You do smth wrong")


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

    print("Trader deposit changed: ", TRADER_DEPOSIT)


def trader_deposit_addition(currency, sell_order_price, amount):
    """
    This function add money to TRADER_DEPOSIT by amount * buy_order_price AFTER order complete at market
    :param currency: currency of order USD, RUR, etc
    :param sell_order_price:
    :param amount:
    :return: trader_deposit
    """
    global TRADER_DEPOSIT

    # Before money will add to TRADER_DEPOSIT, order status must be DONE or SOLD

    TRADER_DEPOSIT[currency] += sell_order_price * amount

    print("Trader deposit changed: ", TRADER_DEPOSIT)


def order_buy_limit(operation_type="Buy", ticker="RSTK", buy_order_price=110.3, amount=1, currency="RUR",
                    created_at=dt.datetime.utcnow()):
    """
    This function make order to buy amount of stocks by ticker name
    specified at buy_order_price and wait until market price of stock ticker reach
    buy_order_price
    :param operation_type:
    :param currency:
    :param created_at:
    :param ticker: ticker name
    :param buy_order_price: price to buy ticker
    :param amount: number of stocks to buy
    :return: order_id
    """

    operation_type = order_data[0]
    ticker = order_data[1]
    buy_order_price = order_data[2]
    amount = order_data[3]
    currency = "RUR"
    created_at = order_data[4]
    buy_order_data = [operation_type, ticker, buy_order_price, amount, currency, created_at]
    print("You place limit buy order for: ", ticker, ", amount lot is: ", amount, ", by price: ",
          buy_order_price)
    trader_deposit_subtraction(currency, buy_order_price, amount)
    time.sleep(1)
    return buy_order_data


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


def order_place_to_market(type_order_data):
    """
    Create order by individual id returned from buy_order_limit foo
    :param type_order_data:
    :param order_data:
    :param order_id:
    :return:
    """
    global NEW_ORDER_LIST

    NEW_ORDER_LIST.append(type_order_data)
    print("Order is placed", type_order_data)
    print("return ", NEW_ORDER_LIST)


def get_ticker_price(ticker):
    """
    This function get data from somewhere api and return ticker price

    """
    current_price = market.get_stock_data(ticker)
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
    operation_type = order[0]
    ticker = order[1]
    market_price = get_ticker_price(ticker)
    order_price = order[2]
    flag = False
    # condition for buy order
    print("Order status checking")
    if operation_type == "Buy" and market_price <= order_price:
        print("Market price <= Order price condition for Buy is True")
        order_done_at = dt.datetime.utcnow()
        flag = True
        order_status = [flag, order_done_at]
        return order_status

    elif operation_type == "Sell" and market_price >= order_price:
        print("Market price >= Order price condition for Sell is True")
        order_done_at = dt.datetime.utcnow()
        flag = True
        order_status = [flag, order_done_at]
        return order_status
    else:
        print("Wrong condition")
        flag = False
        order_done_at = dt.datetime.utcnow()
        order_status = [flag, order_done_at]
        return order_status


def check_new_orders(new_order_list):

    for order in new_order_list:
        print(order)
        order_status = check_order_status(order)
        if order_status[0]:
            print("Order ", order, "status is True", )

            done_order = [order, order_status[1]]
            TRADING_HISTORY_LIST.append(done_order)

            NEW_ORDER_LIST.remove(order)
            print(NEW_ORDER_LIST)

        else:
            print("Checking...")
    if not NEW_ORDER_LIST:
        print("There are no new orders ", NEW_ORDER_LIST)
        print("Orders history here: ", TRADING_HISTORY_LIST)







def market_manager(user_account_id):
    """
    This is main cycle

    """

    current_user_id = user_account_id
    user_logged_in = True
    print("Type: Help, to see available commands or hit Enter to pass")
    user_input = input()
    if user_input == "":
        print("Passed")
    else:
        print("You type: ", user_input)

    while user_logged_in: # waiting for user commands and checking orders status


        # there list of available user's commands:
        if user_input == "Help":
            print("List of commands: \n"
                  "buy \n"
                  "sell \n")
            # wait for user new input:
            print("Type: available command or hit Enter to pass")
            user_input = input()
            if user_input == "":
                print("Passed")
            else:
                print("You type: ", user_input)
        elif user_input == "":
            print("Waiting for user command")
            user_input = input(">>")
        elif user_input == "buy":
            create_order_query("Buy")
            print("Try to buy")
        #check_user_input()


        #check_new_orders()
        time.sleep(5) # make pause for 5 sec for checking price changes
        #print("Sleep 5 sec")


if __name__ == "__main__":
    # starting program, waiting for User log in
    account_id = login.wait_logging()
    print(account_id) # TODO delete this
    # main cycle
    market_manager(account_id)

    # check if account_id have portfolio -> show portfolio status
    current_trader_portfolio = trader.Portfolio()
    current_trader_portfolio.show()
    # check if account_id have wallet -> show wallet status
    current_trader_wallet = trader.Wallet()
    current_trader_wallet.show()


    # Wait for commands from trader
    #market.get_stock_data("UWGN")
    get_ticker_price()