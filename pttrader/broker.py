import market
import trader
import json
import pandas as pd
from pathlib import Path
import os
import time
import datetime
from dateutil import tz


def get_current_time():
    # Moscow_tz = tz.gettz("Europe/Moscow")
    # time_to_moscow = datetime.datetime.now(tz=Moscow_tz)
    # current_time = pd.to_datetime(time_to_moscow)

    # for tinkoff_api only
    d = datetime.datetime.utcnow()
    current_time = d.isoformat("T", timespec="seconds") + "+00:00"

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
    user_id = order_query[1]
    # Your broker commission 0.3%
    current_wallet_data = trader.wallet_show_current(user_id)
    broker_commission = current_wallet_data["broker_commission"]
    # tinkoff_tarif_treyder = 0.05

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
    print("Current price:", current_ticker_price, "currency:", currency)
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
        commission_raw = order_price * lot_size * amount / 100 * broker_commission
        order_price_total_raw = (order_price * lot_size * amount)
        commission = round(commission_raw, 2)
        order_price_total = round(order_price_total_raw, 2)

        created_at = get_current_time()

        operation_id = trader.generate_random_id()
        # TODO need to describe order_status for different situation: hold, done, query, wait  ... etc.
        order_status = False
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission]
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
        commission_raw = order_price * lot_size * amount / 100 * broker_commission
        order_price_total_raw = order_price * lot_size * amount
        commission = round(commission_raw, 2)
        order_price_total = round(order_price_total_raw, 2)
        created_at = get_current_time()
        user_id = order_query[1]
        operation_id = trader.generate_random_id()
        # TODO need to describe order_status for different situation: hold, done, query, wait  ... etc.
        order_status = False
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission]
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

    elif order_type == "Buy" and instrument == "currency":

        print("Enter price for Buy operation:")
        order_price = float(input(">>"))

        lot_size = market.get_ticker_lot_size(order_data)
        print("1 lot size:", lot_size)
        print("Enter amount in lot's:")
        amount = int(input(">>"))

        commission_raw = order_price * lot_size * amount / 100 * broker_commission
        order_price_total_raw = (order_price * lot_size * amount)
        commission = round(commission_raw, 2)
        order_price_total = round(order_price_total_raw, 2)
        created_at = get_current_time()
        operation_id = trader.generate_random_id()
        # TODO need to describe order_status for different situation: hold, done, query, wait  ... etc.
        order_status = False  # TODO сheck where it used
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission]

        # need to subtract money from wallet and hold before order will be done
        if wallet_subtract_money_for_buy(order_query):
            create_orders_query(order_query)
            return True
        else:
            print("Order is not ready, please repeat")
            return False

    elif order_type == "Sell" and instrument == "currency":

        if current_wallet_data["USD"] > 0.:

            print("Available amount for sell:", current_wallet_data["USD"])

            if current_ticker_price == "TickerNotFound":
                print(ticker, current_ticker_price, "return False")
                return False
            else:

                print("Enter price for Sell operation:")
                order_price = float(input(">>"))
                lot_size = market.get_ticker_lot_size(order_data)
                print("1 lot size:", lot_size)
                print("Enter amount in lot's for sell:")
                # available amount at wallet
                amount = int(input(">>"))
                currency = market.get_ticker_currency(order_data)
                commission_raw = order_price * lot_size * amount / 100 * broker_commission
                order_price_total_raw = order_price * lot_size * amount
                commission = round(commission_raw, 2)
                order_price_total = round(order_price_total_raw, 2)
                created_at = get_current_time()

                # use new id or use from history?
                operation_id = trader.generate_random_id()
                order_status = False
                order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                               created_at, operation_id, instrument, order_status, commission,
                               broker_commission]
                print("You create sell order: ", order_query)
                # need to hold money  USD currency from wallet
                if hold_money_for_currency_sell(order_query):
                    create_orders_query(order_query)
                return True

    elif order_type == "Sell" and instrument == "stocks":

        print("Enter operation id to sell ")
        buy_operation_id = int(input(">>"))

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
                    commission_raw = order_price * lot_size * amount / 100 * broker_commission
                    order_price_total_raw = order_price * lot_size * amount
                    commission = round(commission_raw, 2)
                    order_price_total = round(order_price_total_raw, 2)
                    created_at = get_current_time()

                    # use historical id to easy close this orders in future
                    operation_id = buy_operation_id
                    order_status = False
                    order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                                   created_at, operation_id, instrument, order_status, commission,
                                   broker_commission]
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


def hold_money_for_currency_sell(order_data):
    order_type = order_data[0]
    account_id = order_data[1]
    ticker = order_data[2]
    order_price = order_data[3]
    amount = order_data[4]
    currency = "USD"
    order_price_total = order_data[6]
    created_at = order_data[7]
    operation_id = order_data[8]
    instrument = order_data[9]
    order_status = order_data[10]
    commission = order_data[11]
    broker_commission = order_data[12]

    print("Money to hold for sell from wallet:", amount, currency)
    wallet_current_data = trader.wallet_show_current(account_id)
    wallet_current_data["USD"] -= amount

    wallet_current_data["USD"] = round(wallet_current_data["USD"], 2)
    if wallet_current_data["USD"] >= 0.:

        with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
            file.write(json.dumps(wallet_current_data))

        wallet_history_data = trader.wallet_show_history(account_id)

        df = wallet_history_data.append({"currency": currency,
                                         "amount": 0 - amount,
                                         "date_time": created_at,
                                         "operation": order_type,
                                         "operation_id": operation_id,
                                         "instrument": instrument},
                                        ignore_index=True)

        df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)

        return True
    elif wallet_current_data["USD"] < 0.:
        print("You don't have enough money for this operation")
        print(trader.wallet_show_current(account_id))
        return False


def wallet_subtract_money_for_buy(order_data):
    """
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                   created_at, operation_id, instrument, order_status, commission]
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
    commission = order_data[11]
    broker_commission = order_data[12]

    print("Money to hold from wallet:", order_price_total, currency)
    print(broker_commission, "% commission is:", commission, currency)

    wallet_history_data = trader.wallet_show_history(account_id)

    wallet_current_data = trader.wallet_show_current(account_id)

    if instrument == "currency":

        wallet_current_data["RUB"] -= commission
        wallet_current_data["RUB"] -= order_price_total

        wallet_current_data["RUB"] = (round(wallet_current_data["RUB"], 2))

        if wallet_current_data["RUB"] >= 0.:
            # save changed data
            with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                file.write(json.dumps(wallet_current_data))
            # pay attention that 0-order_price_total for result as -xxx
            df = wallet_history_data.append({"currency": currency,
                                             "amount": 0 - order_price_total,
                                             "date_time": created_at,
                                             "operation": order_type,
                                             "operation_id": operation_id,
                                             "instrument": instrument},
                                            ignore_index=True)
            # commission
            df = df.append({"currency": currency,
                            "amount": 0 - commission,
                            "date_time": created_at,
                            "operation": broker_commission,
                            "operation_id": operation_id,
                            "instrument": instrument},
                           ignore_index=True)

            df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)

            return True

        elif wallet_current_data["RUB"] < 0.:
            print("You don't have enough money for this operation")
            print(trader.wallet_show_current(account_id))
            return False

    elif instrument == "stocks":

        if currency == "RUB":

            wallet_current_data["RUB"] -= commission
            wallet_current_data["RUB"] -= order_price_total
            wallet_current_data["RUB"] = round(wallet_current_data["RUB"], 2)

            if wallet_current_data["RUB"] > 0.:
                # save changed data
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                # pay attention that 0-amount for result as -xxx
                df = wallet_history_data.append({"currency": currency,
                                                 "amount": 0 - order_price_total,
                                                 "date_time": created_at,
                                                 "operation": order_type,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)
                # commission
                df = df.append({"currency": currency,
                                "amount": 0 - commission,
                                "date_time": created_at,
                                "operation": broker_commission,
                                "operation_id": operation_id,
                                "instrument": instrument},
                               ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                return True

            elif wallet_current_data["RUB"] < 0.:
                print("You don't have enough money for this operation")
                print(trader.wallet_show_current(account_id))
                return False

        elif currency == "USD":

            wallet_current_data["USD"] -= commission
            wallet_current_data["USD"] -= order_price_total
            wallet_current_data["USD"] = round(wallet_current_data["USD"], 2)

            if wallet_current_data["USD"] > 0.:
                # write new data to wallet_current
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))

                df = wallet_history_data.append({"currency": currency,
                                                 "amount": 0 - order_price_total,
                                                 "date_time": created_at,
                                                 "operation": order_type,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)
                # commission
                df = df.append({"currency": currency,
                                "amount": 0 - commission,
                                "date_time": created_at,
                                "operation": broker_commission,
                                "operation_id": operation_id,
                                "instrument": instrument},
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
    commission = order_data["commission"]
    broker_commission = order_data["broker_commission"]
    order_done_at = order_data["order_done_at"]
    order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                   created_at, operation_id]
    print("Money to add:", order_price_total)
    print(order_query)

    account_id = user_id
    # check if this file exist
    trader.is_wallet_history_exist(account_id)
    wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")

    if currency == "RUB" or currency == "USD":

        wallet_current_data = trader.wallet_show_current(account_id)

        if currency == "RUB" and instrument == "stocks":
            # minus commission
            wallet_current_data["RUB"] -= commission
            wallet_current_data["RUB"] += order_price_total
            wallet_current_data["RUB"] = round(wallet_current_data["RUB"], 2)
            if wallet_current_data["RUB"] >= 0.:

                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))

                df = wallet_history_data.append({"currency": currency,
                                                 "amount": order_price_total,
                                                 "date_time": order_done_at,
                                                 "operation": order_type,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                # minus commission
                wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")

                df = wallet_history_data.append({"currency": currency,
                                                 "amount": 0 - commission,
                                                 "date_time": order_done_at,
                                                 "operation": broker_commission,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)

                return True

            elif wallet_current_data["RUB"] < 0.:
                print("You don't have enough money for this operation")
                print(trader.wallet_show_current(account_id))
                return False

        if currency == "RUB" and instrument == "currency":
            # minus commission
            wallet_current_data["RUB"] -= commission
            wallet_current_data["RUB"] += order_price_total

            wallet_current_data["RUB"] = round(wallet_current_data["RUB"], 2)

            if wallet_current_data["RUB"] >= 0.:

                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))

                df = wallet_history_data.append({"currency": currency,
                                                 "amount": order_price_total,
                                                 "date_time": order_done_at,
                                                 "operation": order_type,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                # minus commission
                wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")

                df = wallet_history_data.append({"currency": currency,
                                                 "amount": 0 - commission,
                                                 "date_time": order_done_at,
                                                 "operation": broker_commission,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)

                return True

            elif wallet_current_data["RUB"] < 0.:
                print("You don't have enough money for this operation")
                print(trader.wallet_show_current(account_id))
                return False

        elif currency == "USD":
            wallet_current_data["USD"] -= commission
            wallet_current_data["USD"] += order_price_total
            wallet_current_data["USD"] = round(wallet_current_data["USD"], 2)
            if wallet_current_data["USD"] >= 0.:
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                # write operation to history
                df = wallet_history_data.append({"currency": currency,
                                                 "amount": order_price_total,
                                                 "date_time": order_done_at,
                                                 "operation": order_type,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                # minus commission
                wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
                df = wallet_history_data.append({"currency": currency,
                                                 "amount": 0 - commission,
                                                 "date_time": order_done_at,
                                                 "operation": broker_commission,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                return True
            elif wallet_current_data["USD"] < 0.:
                print("You don't have enough money for this operation")
                print(trader.wallet_show_current(account_id))
                return False


def create_orders_query(order_query):
    """
            order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission]
    """

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
                         "operation_id": order_query[8], "instrument": order_query[9], "order_status": order_query[10],
                         "commission": order_query[11], "broker_commission": order_query[12],
                         })
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
                           "order_status": order_query[10],
                           "commission": order_query[11], "broker_commission": order_query[12],
                           }]
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
                       "operation_id": order_query[8], "instrument": order_query[9],
                       "order_status": order_query[10],
                       "commission": order_query[11], "broker_commission": order_query[12],
                       }]
        with open('files/orders_query.txt', 'w+') as file:
            file.write(json.dumps(first_data))

        return True


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

                # order_status_response = market.get_ticker_historical_data(order_data)
                order_status_response = market.get_ticker_historical_data_from_tinkoff_api(order_data)
                print("Order status from market response:", order_status_response)
                if order_status_response[0]:
                    print("Order ", order_data["operation_id"], "status is:", order_status_response[0])
                    order_done_at = (order_status_response[1]).isoformat("T")
                    order_data.update({"order_done_at": order_done_at})
                    # remove done order from order_query
                    new_order_list.remove(order_data)
                    with open('files/orders_query.txt', 'w+') as file:
                        file.write(json.dumps(new_order_list))
                        print("New orders_query changed ")

                    if order_data['order_type'] == "Buy" and order_data['instrument'] == "stocks":

                        # add data about done order to potrfolio_current
                        trader.portfolio_current_add_order(order_data)



                    elif order_data['order_type'] == "Sell" and order_data['instrument'] == "stocks":
                        # add money to user_id wallet
                        wallet_add_money_for_sell(order_data)
                        # add data about Sell order to portfolio history file
                        trader.portfolio_history_add_order(order_data)
                        # delete data about orders from portfolio current and write to portfolio history
                        trader.portfolio_move_from_current(order_data)

                    elif order_data['order_type'] == "Buy" and order_data['instrument'] == "currency":
                        data_query = [order_data["user_id"], "USD", order_data["amount"], order_data["operation_id"],
                                      order_data["instrument"], order_data["order_type"]
                                      ]
                        trader.wallet_add_money(data_query)
                        # add data about done order to portfolio_current TODO keep as one operation_id
                        # 1 check if there any USDRUB in portfolio current
                        portfolio_all_data = trader.portfolio_show_current(order_data["user_id"])
                        portfolio_data = (portfolio_all_data[portfolio_all_data["ticker"] == order_data["ticker"]])
                        if not portfolio_data.empty:
                            # get data about USDRUB from current portfolio
                            print("portfolio data:\n", portfolio_data)
                            # calculate average price for new order: sum of orders order_price_total / sum of amounts
                            order_total_price = order_data["order_price_total"]
                            order_amount = order_data["amount"]
                            order_commission = order_data["commission"]
                            portfolio_total_price = (portfolio_data["order_price_total"]).values[0]
                            portfolio_amount = portfolio_data["amount"].values[0]
                            portfolio_commission = portfolio_data["commission"].values[0]

                            sum_of_amounts = round(order_amount + portfolio_amount, 2)
                            sum_of_price_totals = round(order_total_price + portfolio_total_price, 2)
                            average_price = round(sum_of_price_totals / sum_of_amounts, 2)

                            sum_of_commissions = round(order_commission + portfolio_commission, 2)

                            # next step: delete from portfolio old data and save new
                            get_index_number = portfolio_data["commission"].index.values[0]
                            print("index num:", get_index_number)
                            without_dropped_data = portfolio_all_data.drop([get_index_number])

                            df = without_dropped_data.append({"order_type": order_data["order_type"],
                                                              "ticker": order_data["ticker"],
                                                              "order_price": average_price,
                                                              "amount": sum_of_amounts,
                                                              "currency": order_data["currency"],
                                                              "order_price_total": sum_of_price_totals,
                                                              "commission": sum_of_commissions,
                                                              "order_created_at": order_data["created_at"],
                                                              "operation_id": order_data["operation_id"],
                                                              "instrument": order_data["instrument"],
                                                              "order_done_at": order_data["order_done_at"],
                                                              },
                                                             ignore_index=True)
                            # save to csv
                            df.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=False)



                        # there is no orders in current portfolio add one
                        elif portfolio_data.empty:

                            trader.portfolio_current_add_order(order_data)

                    elif order_data['order_type'] == "Sell" and order_data['instrument'] == "currency":
                        print("You sell USDRUB , need to add money to wallet RUB ")
                        # add data to wallet history
                        # also need to move data about Buy operation id to portfolio history
                        # add money to user_id wallet
                        wallet_add_money_for_sell(order_data)
                        # add data about Sell order to portfolio history file
                        trader.portfolio_history_add_order(order_data)
                        # delete data about orders from portfolio current and write to portfolio history
                        trader.portfolio_move_from_current(order_data)

                elif not order_status_response[0]:
                    print("Order status = False")
                    order_status = False

                else:
                    print("Checking order: ", order_data["operation_id"])
        print("Iteration done")

    print("There are no Done orders ", len(new_order_list))
