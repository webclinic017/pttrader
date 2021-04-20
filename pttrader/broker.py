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
from dateutil import tz


def get_current_time():
    Moscow_tz = tz.gettz("Europe/Moscow")
    time_to_moscow = datetime.datetime.now(tz=Moscow_tz)
    current_time = pd.to_datetime(time_to_moscow)
    return current_time


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
    # TODO change all dates to one standard as below

    order_type = order_query[0]
    print("Enter ticker name:")
    ticker = trader.get_user_input_data()
    if ticker == "USDRUB":
        instrument = "currency"
    else:
        instrument = "stocks"
    order_data = [instrument, ticker]
    currency = market.get_ticker_currency(order_data)
    if currency == "TickerNotFound":
        print(ticker, currency, "return False")
        return False
    current_ticker_price = market.get_ticker_price(order_data)
    print("Current price:", current_ticker_price, "currency:",currency)
    print("price increment is:", market.get_ticker_min_price_increment(order_data))
    if current_ticker_price == "TickerNotFound":
        print(ticker, current_ticker_price, "return False")
        return False

    if order_type == "Buy" and currency == "RUB":

        print("Enter price for Buy operation:")

        order_price = float(input(">>"))
        lot_size = market.get_ticker_lot_size(order_data)
        print("1 lot size:", lot_size)
        print("Enter amount in lot's:")
        amount = int(input(">>"))

        order_price_total = order_price * lot_size * amount
        created_at = get_current_time()
        user_id = order_query[1]
        operation_id = trader.generate_random_id()
        # TODO need to describe order_status for different situation: hold, done, query, wait  ... etc.
        order_status = False
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status]
        print("You create buy order: ", order_query)
        # need to subtract HOLD  USD from portfolio and hold before order will be done
        # need to subtract money from wallet and hold before order will be done
        if wallet_subtract_money_for_buy(order_query):
            create_orders_query(order_query)
            return True
        else:
            print("Order is not ready, please repeat")
            return False

    elif order_type == "Buy" and currency == "USD":


        print("Enter price for Buy operation:")
        # TODO change all input() to one function trader.get_user_input_data()
        order_price = float(input(">>"))
        lot_size = market.get_ticker_lot_size(order_data)
        print("1 lot size:", lot_size)
        print("Enter amount in lot's:")
        amount = int(input(">>"))

        order_price_total = order_price * lot_size * amount
        created_at = get_current_time()
        user_id = order_query[1]
        operation_id = trader.generate_random_id()
        # TODO need to describe order_status for different situation: hold, done, query, wait  ... etc.
        order_status = False
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status]
        print("You create buy order: ", order_query)
        # need to subtract HOLD  USD from portfolio and hold before order will be done
        # need to subtract money from wallet and hold before order will be done
        portfolio_all_data = trader.portfolio_show_current(user_id)
        portfolio_usdrub_data = (portfolio_all_data[portfolio_all_data["ticker"] == "USDRUB"])
        if not portfolio_usdrub_data.empty:

            # need to calculate amount of USD to hold
            # get current USD amount from wallet balance
            wallet_balance_data = trader.wallet_show_current(user_id)
            usd_at_wallet = wallet_balance_data["USD"]
            print("usd_at_wallet: ", usd_at_wallet)
            if usd_at_wallet >= order_price_total:
                print("You have enough money for this buy order")
                # hold usd from wallet_current for this operation
                if wallet_subtract_money_for_buy(order_query):
                    create_orders_query(order_query)
                    return True

            elif usd_at_wallet < order_price_total:
                print("You don't have enough money for this buy order")
                print("You need:", order_price_total - usd_at_wallet)
                return False
            # if first order have enough amount do hold operation
            # else add second buy order if exist and do hold operation
            # if amount not enough for buy operation - user need to buy more USDRUB

            # need to calculate amount of USD to hold



        elif portfolio_usdrub_data.empty:
            print("You need to buy USDRUB")

            return False

    elif order_type == "Sell" :

        print("Enter operation id to sell ")
        buy_operation_id = int(input(">>"))
        user_id = order_query[1]
        portfolio_all_data = trader.portfolio_show_current(user_id)
        portfolio_data = (portfolio_all_data[portfolio_all_data["operation_id"] == buy_operation_id])
        if not portfolio_data.empty:
            # check if order have one operation_id for buy and sell order early

            if len(portfolio_data) == 2 and len(portfolio_data["order_type"].unique()) == 2:
                print("Order: ", buy_operation_id, "closed completely")
                return False
            else:
                portfolio_order_data = portfolio_data[portfolio_data["operation_id"] == buy_operation_id]
                current_ticker_price = market.get_ticker_price(order_data)
                print("Current price:", current_ticker_price)
                if current_ticker_price == "TickerNotFound":
                    print(ticker, current_ticker_price, "return False")
                    return False
                else:
                    print("price increment is:", market.get_ticker_min_price_increment(order_data))
                    print("Enter price for Sell operation:")
                    order_price = float(input(">>"))
                    lot_size = market.get_ticker_lot_size(order_data)
                    print("1 lot size:", lot_size)
                    print("Enter amount in lot's:")

                    amount = int(portfolio_order_data["amount"].values)
                    print("amount:", amount)
                    currency = market.get_ticker_currency(order_data)
                    order_price_total = order_price * lot_size * amount
                    created_at = get_current_time()

                    # use historical id to easy close this orders in future
                    operation_id = buy_operation_id
                    order_status = False
                    order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                                   created_at, operation_id, instrument, order_status]
                    print("You create sell order: ", order_query)
                    # need to add money to wallet after order will be done
                    # check if trader portfolio have data for sell
                    create_orders_query(order_query)
                    return True
        elif portfolio_data.empty:
            print(buy_operation_id, "Order not found")
            return False
    else:
        print("Order is not ready, please repeat")
        return False


def wallet_subtract_money_for_buy(order_data):
    """
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                   created_at, operation_id, instrument, order_status]
    """
    order_type = order_data[0]
    account_id = order_data[1]
    ticker = order_data[2]
    order_price = order_data[3]
    amount = order_data[4]
    currency = order_data[5]
    order_price_total = order_data[6]
    created_at = order_data[7]
    operation_id = order_data[8]
    instrument = order_data[9]
    order_status = order_data[10]

    print("Money to hold from wallet:", order_price_total, currency)
    current_time = get_current_time()

    wallet_history_data = trader.wallet_show_history(account_id)

    operation = "buy"
    # second operation will calculate and write new data to current state of wallet
    wallet_current_data = trader.wallet_show_current(account_id)

    if instrument == "currency":
        wallet_current_data["RUB"] -= order_price_total
        if wallet_current_data["RUB"] >= 0.:
            with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                file.write(json.dumps(wallet_current_data))
            # pay attention that 0-order_price_total for result as -xxx
            df = wallet_history_data.append({"currency": currency,
                                             "amount": 0 - order_price_total,
                                             "date_time": current_time,
                                             "operation": operation,
                                             "operation_id": operation_id},
                                            ignore_index=True)

            df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
            # add money to wallet after order complete

            return True

        elif wallet_current_data["RUB"] < 0.:
            print("You don't have enough money for this operation")
            print(trader.wallet_show_current(account_id))
            return False

    elif instrument == "stocks":

        if currency == "RUB":
            wallet_current_data["RUB"] -= order_price_total
            if wallet_current_data["RUB"] >= 0.:
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                # pay attention that 0-amount for result as -xxx
                df = wallet_history_data.append({"currency": currency,
                                                 "amount": 0 - order_price_total,
                                                 "date_time": current_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                return True
            elif wallet_current_data["RUB"] < 0.:
                print("You don't have enough money for this operation")
                print(trader.wallet_show_current(account_id))
                return False

        elif currency == "USD":
            wallet_current_data["USD"] -= order_price_total
            if wallet_current_data["RUB"] >= 0.:
                # write new data to wallet_current
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))

                df = wallet_history_data.append({"currency": currency,
                                                 "amount": 0 - order_price_total,
                                                 "date_time": current_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                return True

            elif wallet_current_data["USD"] < 0.:
                print("You don't have enough money for this operation")
                print(trader.wallet_show_current(account_id))
                return False


def wallet_add_money_for_sell(order_data):
    """
    Add money to user wallet after sell operation will done
    Used portfolio data
    """
    print(order_data)
    order_type = order_data["order_type"]
    user_id = order_data["user_id"]
    ticker = order_data["ticker"]
    order_price = order_data["order_price"]
    amount = order_data["amount"]
    currency = order_data["currency"]
    order_price_total = order_data["order_price_total"]
    created_at = order_data["created_at"]
    operation_id = order_data["operation_id"]
    instrument = order_data["instrument"]
    order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                   created_at, operation_id]
    print("Money to add:", order_price_total)
    print(order_query)

    current_time = get_current_time()
    account_id = user_id
    # check if this file exist
    trader.is_wallet_history_exist(account_id)
    wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")

    if currency == "RUB" or currency == "USD":

        amount = order_price_total

        operation = "sell"
        # second operation will calculate and write new data to current state of wallet
        with open("files/wallet_current_" + str(account_id) + ".txt", "r") as file:
            data = file.read()
        wallet_current_data = json.loads(data)

        if currency == "RUB":
            wallet_current_data["RUB"] += amount
            if wallet_current_data["RUB"] >= 0.:
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))

                df = wallet_history_data.append({"currency": currency,
                                                 "amount": amount,
                                                 "date_time": current_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                return True
            elif wallet_current_data["RUB"] < 0.:
                print("You don't have enough money for this operation")
                print(trader.wallet_show_current(account_id))
                return False
        elif currency == "USD":
            wallet_current_data["USD"] += amount
            if wallet_current_data["USD"] >= 0.:
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                # write operation to history
                df = wallet_history_data.append({"currency": currency,
                                                 "amount": amount,
                                                 "date_time": current_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                return True
            elif wallet_current_data["USD"] < 0.:
                print("You don't have enough money for this operation")
                print(trader.wallet_show_current(account_id))
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
                file.write(json.dumps(data, default=str))

            return True

        elif Path("files").is_dir():
            time.sleep(1)

            # add new order to local database

            first_data = [{"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                           "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                           "order_price_total": order_query[6], "created_at": order_query[7],
                           "operation_id": order_query[8], "instrument": order_query[9],
                           "order_status": order_query[10]}]
            with open('files/orders_query.txt', 'w+') as file:
                file.write(json.dumps(first_data, default=str))

            return True

    else:
        # create folder if not exist
        os.mkdir("files")

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
    # all not done orders
    while new_order_list and order_status:
        for order_data in new_order_list:

            print("Checking order id:", order_data["operation_id"])
            print("Order created_at", order_data["created_at"])
            # check orders in orders list only for current user
            if order_data["user_id"] == account_id:
                print("Order data:", order_data)
                # order_status_response = check_order_status(order_data)
                order_status_response = market.get_ticker_historical_data(order_data)
                print("Order status from market response:", order_status_response)
                if order_status_response[0]:
                    print("Order ", order_data["operation_id"], "status is:", order_status_response[0])
                    order_data.update({"order_done_at": order_status_response[1]})
                    # remove done order from order_query
                    new_order_list.remove(order_data)
                    with open('files/orders_query.txt', 'w+') as file:
                        file.write(json.dumps(new_order_list))
                        print("New orders_query changed ")

                    if order_data['order_type'] == "Buy" and order_data['instrument'] == "stocks":

                        # add data about done order to potrfolio_current
                        trader.portfolio_current_add_order(order_data)

                    elif order_data['order_type'] == "Buy" and order_data['instrument'] == "currency":
                        data_query = [order_data["user_id"], "USD", order_data["amount"], order_data["operation_id"]]
                        trader.wallet_add_money(data_query)
                        # add data about done order to potrfolio_current
                        trader.portfolio_current_add_order(order_data)

                    elif order_data['order_type'] == "Sell" and order_data['instrument'] == "stocks":
                        # add money to user_id wallet
                        wallet_add_money_for_sell(order_data)
                        # add data about Sell order to portfolio history file
                        trader.portfolio_history_add_order(order_data)
                        #delete data about orders from portfolio current and write to portfolio history
                        trader.portfolio_move_from_current(order_data)
                    elif order_data['order_type'] == "Sell" and order_data['instrument'] == "currency":
                        print("You sell USDRUB , need to add money to wallet RUB ")
                        # add data to wallet history
                        # also need to move data about Buy operation id to portfolio history

                elif not order_status_response[0]:
                    print("Order status = False")
                    order_status = False

                else:
                    print("Checking order: ", order_data["operation_id"])
        print("Iteration done")

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
    operation_id = order_data_next["operation_id"]
    current_time = get_current_time()
    # need to check all prices from order created_at to now or min max daily
    order_status = market.get_ticker_historical_data(order_data_next)

    return order_status
