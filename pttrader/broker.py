import datetime
import market
import trader
import json
from random import randint
import pandas as pd


# input data may be primary from trader: buy_request, sell_request
def create_order_query(order_query):
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
    # ct stores current time
    ct = datetime.datetime.now()
    # ts store timestamp of current time
    ts = ct.timestamp()
    operation_type = order_query[0]
    print("Enter ticker name:")
    ticker = str(input(">>"))
    print("Current price:", market.get_ticker_price(ticker))
    if operation_type == "Buy":
        print("Enter price for Buy operation:")
        buy_order_price = float(input(">>"))
        lot_size = market.get_ticker_lot_size(ticker)
        print("1 lot size:", lot_size)
        print("Enter amount in lot's:")
        amount = int(input())
        currency = market.get_ticker_currency(ticker)
        money_to_subtract = buy_order_price * lot_size * amount
        created_at = ts
        current_user_id = order_query[1]
        order_query = [operation_type, current_user_id, ticker, buy_order_price, amount, currency, money_to_subtract, created_at]
        print("You create buy order: ", order_query)
        # need to subtract money from wallet and hold before order will be done
        if wallet_subtract_money(order_query):
            return order_query
        else:
            print("Order is not ready, please repeat")


    elif operation_type== "Sell":
        print("Enter price for Sell operation:")
        sell_order_price = float(input(">>"))
        print("Enter amount in lot's:")
        amount = int(input(">>"))
        created_at = ts
        order_query = [operation_type, ticker, sell_order_price, amount, created_at]
        print("You create sell order query: ", order_query)
        return order_query

    else:
        print("You do something wrong")


def wallet_subtract_money(order_data):

    operation_type = order_data[0]
    current_user_id = order_data[1]
    ticker = order_data[2]
    buy_order_price = order_data[3]
    amount = order_data[4]
    currency = order_data[5]
    money_to_subtract = order_data[6]
    created_at = order_data[7]
    order_query = [operation_type, current_user_id, ticker, buy_order_price, amount, currency, money_to_subtract,
                   created_at]
    print("Money to subtract:", money_to_subtract)
    print(order_query)

    # ct stores current time
    ct = datetime.datetime.now()
    # ts store timestamp of current time
    ts = ct.timestamp()
    account_id = current_user_id
    # check if this file exist
    trader.is_wallet_history_exist(account_id)
    wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")

    if currency == "RUB" or currency == "USD":


        amount = money_to_subtract
        date_time = ts
        operation = "subtract"
        # random id generator
        operation_id = randint(10000, 99999)

        # second operation will calculate and write new data to current state of wallet
        with open("files/wallet_" + str(account_id) + ".txt", "r") as file:
            data = file.read()
        wallet_current_data = json.loads(data)

        if currency == "RUB":
            wallet_current_data["RUB"] -= amount
            if wallet_current_data["RUB"] >= 0.:
                with open("files/wallet_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))

                df = wallet_history_data.append({"currency": currency,
                                                 "amount": amount,
                                                 "date_time": date_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                return True
            elif wallet_current_data["RUB"] < 0.:
                print("You don't have enough money for this operation")
                return False
        elif currency == "USD":
            wallet_current_data["USD"] -= amount
            if wallet_current_data["USD"] >= 0.:
                with open("files/wallet_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                # write operation to history
                df = wallet_history_data.append({"currency": currency,
                                                 "amount": amount,
                                                 "date_time": date_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                return True
            elif wallet_current_data["USD"] < 0.:
                print("You don't have enough money for this operation")
                return False







def commission():
    pass

def trader_wallet_subtraction(currency, buy_order_price, amount):
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




def order_sell_limit(ticker="UWGN", currency="RUR", sell_order_price=110.3, amount=1, created_at=None):
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
    market_price = market.get_ticker_price(ticker)
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