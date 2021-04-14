import datetime
import market
import trader
import json
from random import randint
import pandas as pd
from pathlib import Path
import os
import time
import datetime


# input data may be primary from trader: buy request, sell request
def create_order_query(order_query):
    """
    Get input parameters from trader:
    operation type: Buy or Sell from main cycle
    ticker
    order_price
    order_price
    amount
    created_at
    :return: order query
    """
    # ct stores current time
    ct = datetime.datetime.now()
    # ts store timestamp of current time
    ts = ct.timestamp()
    order_type = order_query[0]
    print("Enter ticker name:")
    ticker = str(input(">>"))
    if ticker == "USDRUB":
        instrument = "currency"
    else:
        instrument = "stocks"
    order_data = [instrument, ticker]
    print("Current price:", market.get_ticker_price(order_data))
    print("price increment is:", market.get_ticker_min_price_increment(order_data))

    if order_type == "Buy":

        print("Enter price for Buy operation:")
        order_price = float(input(">>"))
        lot_size = market.get_ticker_lot_size(order_data)
        print("1 lot size:", lot_size)
        print("Enter amount in lot's:")
        amount = int(input())
        currency = market.get_ticker_currency(order_data)
        order_price_total = order_price * lot_size * amount
        created_at = ts
        user_id = order_query[1]
        # random id generator
        operation_id = randint(10000, 99999)
        order_status = False
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status]
        print("You create buy order: ", order_query)
        # need to subtract money from wallet and hold before order will be done
        if wallet_subtract_money_for_buy(order_query):
            create_orders_query(order_query)
            return order_query
        else:
            print("Order is not ready, please repeat")

    elif order_type == "Sell":

        print("Enter price for Sell operation:")
        order_price = float(input(">>"))
        lot_size = market.get_ticker_lot_size(order_data)
        print("1 lot size:", lot_size)
        print("Enter amount in lot's:")
        amount = int(input())
        currency = market.get_ticker_currency(order_data)
        order_price_total = order_price * lot_size * amount
        created_at = ts
        user_id = order_query[1]
        # random id generator
        operation_id = randint(10000, 99999)
        order_status = False
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status]
        print("You create sell order: ", order_query)
        # need to subtract money from wallet and hold before order will be done
        if wallet_subtract_money_for_buy(order_query):
            create_orders_query(order_query)
            return True
        else:
            print("Order is not ready, please repeat")
            return False


def wallet_subtract_money_for_buy(order_data):
    order_type = order_data[0]
    user_id = order_data[1]
    ticker = order_data[2]
    order_price = order_data[3]
    amount = order_data[4]
    currency = order_data[5]
    order_price_total = order_data[6]
    created_at = order_data[7]
    operation_id = order_data[8]
    instrument = order_data[9]
    order_status = order_data[10]
    order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                   created_at, operation_id, instrument, order_status]
    print("Money to subtract:", order_price_total)
    print(order_query)

    # ct stores current time
    ct = datetime.datetime.now()
    # ts store timestamp of current time
    ts = ct.timestamp()
    account_id = user_id
    # check if this file exist
    trader.is_wallet_history_exist(account_id)
    wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
    price = order_price
    if currency == "RUB" or currency == "USD":
        amount = order_price_total
        date_time = ts
        operation = "subtract"
        # second operation will calculate and write new data to current state of wallet
        with open("files/wallet_" + str(account_id) + ".txt", "r") as file:
            data = file.read()
        wallet_current_data = json.loads(data)

        if instrument == "USDRUB":
            wallet_current_data["RUB"] -= amount
            if wallet_current_data["RUB"] >= 0.:
                with open("files/wallet_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))

                df = wallet_history_data.append({"currency": currency,
                                                 "price": price,
                                                 "amount": amount,
                                                 "date_time": date_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                # add money to wallet after order complete

                return True

            elif wallet_current_data["RUB"] < 0.:
                print("You don't have enough money for this operation")
                return False

        if currency == "RUB":
            wallet_current_data["RUB"] -= amount
            if wallet_current_data["RUB"] >= 0.:
                with open("files/wallet_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                price += amount
                df = wallet_history_data.append({"currency": currency,
                                                 "price": price,
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
                # TODO think about USDRUB price where to get it to store here
                # write operation to history
                df = wallet_history_data.append({"currency": currency,
                                                 "price": price,
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


def wallet_add_money_for_sell(order_data):
    """
    Add money to user wallet after sell operation will done
    Used portfolio data
    """
    order_type = order_data[0]
    user_id = order_data[1]
    ticker = order_data[2]
    order_price = order_data[3]
    amount = order_data[4]
    currency = order_data[5]
    order_price_total = order_data[6]
    created_at = order_data[7]
    operation_id = order_data[8]
    order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                   created_at, operation_id]
    print("Money to subtract:", order_price_total)
    print(order_query)

    # ct stores current time
    ct = datetime.datetime.now()
    # ts store timestamp of current time
    ts = ct.timestamp()
    account_id = user_id
    # check if this file exist
    trader.is_wallet_history_exist(account_id)
    wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")

    if currency == "RUB" or currency == "USD":

        amount = order_price_total
        date_time = ts
        operation = "subtract"
        # second operation will calculate and write new data to current state of wallet
        with open("files/wallet_" + str(account_id) + ".txt", "r") as file:
            data = file.read()
        wallet_current_data = json.loads(data)

        if currency == "RUB":
            wallet_current_data["RUB"] += amount
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
            wallet_current_data["USD"] += amount
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


def create_orders_query(order_query):
    if Path("files").is_dir():

        orders_query_data = Path("files/orders_query.txt")
        if orders_query_data.is_file():
            # file exists
            # add new order to local database
            with open('files/orders_query.txt', "r") as file:
                data = file.read()
            data = json.loads(data)

            data.append({"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                         "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                         "order_price_total": order_query[6], "created_at": order_query[7],
                         "operation_id": order_query[8], "instrument": order_query[9], "order_status": order_query[10]})
            with open('files/orders_query.txt', 'w') as file:
                file.write(json.dumps(data))

            return

        elif Path("files").is_dir():
            time.sleep(1)

            # add new order to local database

            first_data = [{"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                           "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                           "order_price_total": order_query[6], "created_at": order_query[7],
                           "operation_id": order_query[8], "instrument": order_query[9],
                           "order_status": order_query[10]}]
            with open('files/orders_query.txt', 'w+') as file:
                file.write(json.dumps(first_data))
                print("New order_query_created")
            return

    else:
        time.sleep(1)
        os.mkdir("files")
        time.sleep(1)

        # add new order to local database

        first_data = [{"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                       "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                       "order_price_total": order_query[6], "created_at": order_query[7],
                       "operation_id": order_query[8], "instrument": order_query[9], "order_status": order_query[10]}]
        with open('files/orders_query.txt', 'w+') as file:
            file.write(json.dumps(first_data))
            print("New order_query_created")
        return


def commission():
    pass


def check_new_orders(account_id):
    """
    Check orders status from orders_query for current user id

    """
    with open('files/orders_query.txt', "r") as file:
        data = file.read()
    data = json.loads(data)
    new_order_list = data
    order_status = True
    while new_order_list and order_status:
        for order_data in new_order_list:
            # check orders in orders list only for current user
            if order_data["user_id"] == account_id:
                order_status = check_order_status(order_data)

                if order_status[0]:
                    print("Order ", order_data["operation_id"], "status is Done\n")

                    # remove done order from order_query
                    new_order_list.remove(order_data)
                    with open('files/orders_query.txt', 'w+') as file:
                        file.write(json.dumps(new_order_list))
                        print("New orders_query changed ")

                    # add data about done order to potrtfolio_history
                    order_data.update({"order_done_at": order_status[1]})
                    trader.portfolio_history_add(order_data)
                elif not order_status[0]:
                    print("Order status = False")
                    order_status = False
                    break

                else:
                    print("Checking order: ", order_data["operation_id"])

    print("There are no Done orders ", len(new_order_list))


def check_order_status(order_data_next):
    """
    Checking ticker market price and order_price is will be meet conditions to buy:
    market_price is less or equal than order_price
    condition to to sell:
    market_price is greater or equal than order_price
    first_data = [{"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                   "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                   "order_price_total": order_query[6], "created_at": order_query[7],
                   "operation_id": order_query[8], "instrument": order_query[9], "order_status": order_query[10]}]
    ['Buy', 41388, 'NMTP', 7.5, 100, 'RUB', 75000.0, 1618309777.660006, 85103, 'stocks', False]
    :param order:
    :return: True or False
    """

    order_type = order_data_next["order_type"]
    ticker = order_data_next["ticker"]
    order_price = order_data_next["order_price"]
    created_at = order_data_next["created_at"]
    instrument = order_data_next["instrument"]

    # need to check all prices from order created_at to now or min max daily

    df = market.get_ticker_historical_data(order_data_next)

    for items in df:
        hist_price = (round(items, ndigits=3))

        flag = False
        # condition for buy order

        if order_type == "Buy" and order_price >= hist_price:

            date_of_done = df.index[0]
            # convert to timestamp
            order_done_at = datetime.datetime.timestamp(date_of_done)
            flag = True
            order_status = [flag, order_done_at]

            return order_status
        # condition for sell order
        elif order_type == "Sell" and order_price <= hist_price:

            date_of_done = df.index[0]

            order_done_at = datetime.datetime.timestamp(date_of_done)
            flag = True
            order_status = [flag, order_done_at]
            return order_status
        else:
            print("Wrong condition or not Done yet")
            # need to store in another list for check iteration
            order_done_at = created_at
            flag = False
            order_status = [flag, order_done_at]
            return order_status
