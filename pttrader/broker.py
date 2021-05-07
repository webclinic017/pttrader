import market
import trader
import json
import pandas as pd
from pathlib import Path
import os

from dateutil import tz
from openapi_client import openapi
from datetime import datetime, timedelta


def get_current_time():
    # Moscow_tz = tz.gettz("Europe/Moscow")
    # time_to_moscow = datetime.datetime.now(tz=Moscow_tz)
    # current_time = pd.to_datetime(time_to_moscow)

    # for tinkoff_api only
    d = datetime.utcnow()
    current_time = d.isoformat("T", timespec="seconds") + "+00:00"

    return current_time


# input data may be primary from trader: buy request, sell request
def create_order_query(order_query):
    """
    Get input parameters from trader:
    data_query = [order_type, user_data.id, ticker,order_price,  amount, order_description]

    :return: list [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission,
                        order_description]

    """
    order_type = order_query[0]
    user_id = order_query[1]
    ticker = order_query[2]
    order_price = order_query[3]
    order_description = order_query[5]

    current_wallet_data = trader.wallet_show_current(user_id)
    broker_commission = current_wallet_data["broker_commission"]

    if ticker == "USDRUB":
        instrument = "currency"
    else:
        instrument = "stocks"
    order_data = [instrument, ticker]

    # TODO if market is closed. use last date data
    currency = market.get_ticker_currency(order_data)

    if currency == "TickerNotFound":
        response = [False, order_query]
        return response

    current_ticker_price = market.get_ticker_price(order_data)

    if current_ticker_price == "TickerNotFound":
        response = [False, order_query]
        return response

    if order_type == "Buy" and currency == "RUB":
        amount = order_query[4]
        # get lot size for ticker at market
        lot_size = market.get_ticker_lot_size(order_data)
        # calculate commission for current order
        commission_raw = order_price * lot_size * amount / 100 * broker_commission
        order_price_total_raw = (order_price * lot_size * amount)
        commission = round(commission_raw, 2)
        order_price_total = round(order_price_total_raw, 2)
        # get current time to fix when order created, may be transported to handlers_bot to get time from there
        created_at = get_current_time()
        # get generated random id for operation tracking
        operation_id = trader.get_random_id()
        # TODO need to describe order_status for different situation: hold, done, query, wait  ... etc.
        order_status = False
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission,
                       order_description
                       ]
        wallet_balance_data = trader.wallet_show_current(user_id)
        rub_at_wallet = wallet_balance_data["RUB"]
        # subtract money from wallet
        if rub_at_wallet >= order_price_total:
            wallet_subtract_money_for_buy(order_query)
            # add order data to  order query
            create_orders_query(order_query)
            # response goes to handlers_bot module
            response = [True, order_query]
            return response
        elif rub_at_wallet < order_price_total:

            order_query = "You need more RUB /wcur " \
                          + "\nRUB at wallet: " + str(rub_at_wallet) \
                          + "\norder price total: " + str(order_price_total)
            response = [False, order_query]
            return response
    # TODO refactor for other order types
    # if you want to buy stock in USD currency, first you need USD at your wallet
    # 1) you need to buy USDRUB before buy stock in USD
    elif order_type == "Buy" and currency == "USD":
        amount = order_query[4]
        lot_size = market.get_ticker_lot_size(order_data)
        commission_raw = order_price * lot_size * amount / 100 * broker_commission
        order_price_total_raw = order_price * lot_size * amount
        commission = round(commission_raw, 2)
        order_price_total = round(order_price_total_raw, 2)
        created_at = get_current_time()
        operation_id = trader.get_random_id()
        # TODO need to describe order_status for different situation: hold, done, query, wait  ... etc.
        order_status = False
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission,
                       order_description
                       ]

        # check if in portfolio current has data about USDRUB
        portfolio_all_data = trader.portfolio_show_current(user_id)
        portfolio_usdrub_data = (portfolio_all_data[portfolio_all_data["ticker"] == "USDRUB"])
        if not portfolio_usdrub_data.empty:
            # need to calculate amount of USD to hold
            # get current USD amount from wallet balance
            wallet_balance_data = trader.wallet_show_current(user_id)
            usd_at_wallet = wallet_balance_data["USD"]
            # check if you have enough money

            if usd_at_wallet >= order_price_total:
                # hold usd from wallet_current for this operation
                if wallet_subtract_money_for_buy(order_query):
                    create_orders_query(order_query)
                    # response goes to handlers_bot module
                    response = [True, order_query]
                    return response

            elif usd_at_wallet < order_price_total:
                order_query = ["You need to buy USDRUB /wcur /buy" + "*" \
                               + "\nUSD at wallet: *" + str(usd_at_wallet) \
                               + "\norder price total: *" + str(order_price_total)]
                response = [False, order_query]
                return response
            # if first order have enough amount do hold operation
            # else add second buy order if exist and do hold operation
            # if amount not enough for buy operation - user need to buy more USDRUB

            # need to calculate amount of USD to hold

        elif portfolio_usdrub_data.empty:

            order_query = ["elif portfolio_usdrub_data.empty: You need to buy USDRUB /wcur /buy"]
            response = [False, order_query]
            return response

    elif order_type == "Buy" and instrument == "currency":
        amount = order_query[4]
        lot_size = market.get_ticker_lot_size(order_data)
        print("1 lot size:", lot_size)

        commission_raw = order_price * lot_size * amount / 100 * broker_commission
        order_price_total_raw = (order_price * lot_size * amount)
        commission = round(commission_raw, 2)
        order_price_total = round(order_price_total_raw, 2)

        created_at = get_current_time()
        operation_id = trader.get_random_id()

        # TODO need to describe order_status for different situation: hold, done, query, wait  ... etc.
        order_status = False  # TODO сheck where it used
        order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission,
                       order_description
                       ]

        # need to subtract money from wallet and hold before order will be done
        if wallet_subtract_money_for_buy(order_query):
            # create_orders_query(order_query)
            create_orders_query(order_query)
            response = [True, order_query]
            return response
        else:

            response = [False, order_query]
            return response

    elif order_type == "Sell" and instrument == "currency":
        amount = order_query[4]
        if current_wallet_data["USD"] > 0.:

            if current_ticker_price == "TickerNotFound":
                order_query = [ticker + str(current_ticker_price) + " return False"]
                response = [False, order_query]
                return response
            else:
                # check market size  (for limit orders it is 1000 lot , for current price is 1 lot)
                lot_size = market.get_ticker_lot_size(order_data)

                # available amount at wallet

                currency = market.get_ticker_currency(order_data)
                commission_raw = order_price * lot_size * amount / 100 * broker_commission
                order_price_total_raw = order_price * lot_size * amount
                commission = round(commission_raw, 2)
                order_price_total = round(order_price_total_raw, 2)
                created_at = get_current_time()

                # use new id or use from history?
                operation_id = trader.get_random_id()
                order_status = False
                order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                               created_at, operation_id, instrument, order_status, commission,
                               broker_commission, order_description
                               ]
                print("You create sell order: ", order_query)
                # need to hold money  USD currency from wallet
                if hold_money_for_currency_sell(order_query):
                    create_orders_query(order_query)
                    response = [True, order_query]
                    return response

                else:
                    order_query = "Order is not ready, please repeat"
                    response = [False, order_query]
                    return response
        else:
            order_query = "Order is not ready, please check wallet /wcur"
            response = [False, order_query]
            return response

    elif order_type == "Sell" and instrument == "stocks":

        buy_operation_id = order_query[4]

        # check if order to sell already in order query

        with open("files/orders_query_" + str(user_id) + ".txt", "r") as file:
            data = file.read()
        new_order_list = json.loads(data)
        for order in new_order_list:

            if buy_operation_id == order['operation_id']:
                text_response = "Ордер на продажу уже в очереди. Ждите его исполнения или отмените /cancel "+\
                                str(buy_operation_id)
                response = [False, text_response]

                return response

        portfolio_all_data = trader.portfolio_show_current(user_id)
        portfolio_data = (portfolio_all_data[portfolio_all_data["operation_id"] == buy_operation_id])
        if not portfolio_data.empty:
            # check if order have one operation_id for buy and sell order early

            if len(portfolio_data) == 2 and len(portfolio_data["order_type"].unique()) == 2:
                order_query = ("Order: " + str(buy_operation_id) + "closed completely")
                response = [False, order_query]
                return response
            else:
                portfolio_order_data = portfolio_data[portfolio_data["operation_id"] == buy_operation_id]
                current_ticker_price = market.get_ticker_price(order_data)

                if current_ticker_price == "TickerNotFound":
                    order_query = [ticker + str(current_ticker_price) + " return False"]
                    response = [False, order_query]
                    return response
                else:

                    lot_size = market.get_ticker_lot_size(order_data)

                    amount = int(portfolio_order_data["amount"].values)

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
                                   broker_commission, order_description
                                   ]

                    # need to add money to wallet after order will be done
                    # check if trader portfolio have data for sell
                    create_orders_query(order_query)
                    response = [True, order_query]
                    return response
        elif portfolio_data.empty:
            order_query = (str(buy_operation_id) + "Order not found")
            response = [False, order_query]
            return response
    else:
        order_query = "Order is not ready, please repeat"
        response = [False, order_query]
        return response


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
    order_description = order_data[13]

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
    order_description = order_data[13]

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
    order_description = order_data["order_description"]
    order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                   created_at, operation_id, order_description]
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
    this function add new order data to local txt file

            order_query = [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission]
    """
    user_id = order_query[1]
    if Path("files").is_dir():
        # TODO add used)id to the end o
        orders_query_data = Path("files/orders_query_" + str(user_id) + ".txt")
        if orders_query_data.is_file():
            # file exists
            # add new order to local database
            with open("files/orders_query_" + str(user_id) + ".txt", "r") as file:
                data = file.read()
            data = json.loads(data)

            data.append({"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                         "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                         "order_price_total": order_query[6], "created_at": order_query[7],
                         "operation_id": order_query[8], "instrument": order_query[9], "order_status": order_query[10],
                         "commission": order_query[11], "broker_commission": order_query[12],
                         "order_description": order_query[13],
                         })
            with open("files/orders_query_" + str(user_id) + ".txt", "w") as file:
                file.write(json.dumps(data, default=str))

            return True

        elif not orders_query_data.is_file():
            # create new db and add new order to local database

            first_data = [{"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                           "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                           "order_price_total": order_query[6], "created_at": order_query[7],
                           "operation_id": order_query[8], "instrument": order_query[9],
                           "order_status": order_query[10],
                           "commission": order_query[11], "broker_commission": order_query[12],
                           "order_description": order_query[13],
                           }]
            with open("files/orders_query_" + str(user_id) + ".txt", "w+") as file:
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
                       "order_description": order_query[13],
                       }]
        with open("files/orders_query_" + str(user_id) + ".txt", 'w+') as file:
            file.write(json.dumps(first_data))

        return True


def cancel_order_in_query(data):
    """
    delete order from orders_query.txt
    delete data from wallet history
    add money to wallet if was hold


    [{"order_type": "Sell", "user_id": 486927694, "ticker": "FLOT", "order_price": 92.0, "amount": 3000,
     "currency": "RUB", "order_price_total": 2760000.0, "created_at": "2021-04-29T10:28:01+00:00",
      "operation_id": 925880, "instrument": "stocks", "order_status": false, "commission": 1932.0,
      "broker_commission": 0.07, "order_description": ""},

    """
    operation_id = data[0]
    user_id = data[1]

    with open("files/orders_query_" + str(user_id) + ".txt", "r") as file:
        data = file.read()
    orders_query = json.loads(data)

    wallet_current_data = trader.wallet_show_current(user_id)
    wallet_history_data = trader.wallet_show_history(user_id)

    for order in orders_query:
        if order["operation_id"] == operation_id and order["order_type"] == "Buy":
            print("order[operation_id] == operation_id and order[order_type] == Buy")
            if order["currency"] == "RUB":
                print("order[currency] == RUB", order)

                wallet_current_data["RUB"] += (order["order_price_total"] + order["commission"])
                wallet_current_data["RUB"] = round(wallet_current_data["RUB"], 2)
                # save wallet data

                with open("files/wallet_current_" + str(user_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))

                # delete data from wallet history
                portfolio_cur = wallet_history_data.set_index("operation_id")
                wallet_history_dropped = portfolio_cur.drop(operation_id)

                wallet_history_dropped.to_csv("files/wallet_history_" + str(user_id) + ".csv", index=True)
                # delete from order query
                orders_query.remove(order)
                with open("files/orders_query_" + str(user_id) + ".txt", 'w+') as file:
                    file.write(json.dumps(orders_query))



                return True

            elif order["currency"] == "USD":
                wallet_current_data["USD"] += (order["order_price_total"] + order["commission"])
                wallet_current_data["USD"] = round(wallet_current_data["USD"], 2)
                # save wallet data
                with open("files/wallet_current_" + str(user_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                # delete data from wallet history
                portfolio_cur = wallet_history_data.set_index("operation_id")
                wallet_history_dropped = portfolio_cur.drop(operation_id)

                wallet_history_dropped.to_csv("files/wallet_history_" + str(user_id) + ".csv", index=True)
                # delete from order query
                orders_query.remove(order)

                with open("files/orders_query_" + str(user_id) + ".txt", 'w+') as file:
                    file.write(json.dumps(orders_query))

                return True

        # TODO for sell cancel if order was create before
        elif order["operation_id"] == operation_id and order["order_type"] == "Sell":
            orders_query.remove(order)
            with open("files/orders_query_" + str(user_id) + ".txt", 'w+') as file:
                file.write(json.dumps(orders_query))
            return True

    return False



def check_new_orders(account_id):
    """
    Check orders status from orders_query for current user id

    """
    # check if not this location
    orders_query_data = Path("files/orders_query_" + str(account_id) + ".txt")
    if not orders_query_data.is_file():
        # add new order to local database
        first_data = []
        with open("files/orders_query_" + str(account_id) + ".txt", "w+") as file:
            file.write(json.dumps(first_data, default=str))

    # read local user db
    with open("files/orders_query_" + str(account_id) + ".txt", "r") as file:
        data = file.read()
    new_order_list = json.loads(data)
    not_done_orders = []
    done_orders = []
    # check all orders in order query
    for order_data in new_order_list:

        print("Checking order id:", order_data["operation_id"])
        # order_status_response = market.get_ticker_historical_data(order_data)
        order_status_response = market.get_ticker_historical_data_from_tinkoff_api(order_data)

        if order_status_response[0]:
            print("Order ", order_data["operation_id"], "status is:", order_status_response[0])
            order_done_at = (order_status_response[1]).isoformat("T")
            order_data.update({"order_done_at": order_done_at})
            order_data.update({"order_status": True})
            # remove done order from order_query
            new_order_list.remove(order_data)
            with open("files/orders_query_" + str(account_id) + ".txt", 'w+') as file:
                file.write(json.dumps(new_order_list))
            if order_data['order_type'] == "Buy" and order_data['instrument'] == "stocks":

                # add data about done order to potrfolio_current
                trader.portfolio_current_add_order(order_data)
                done_orders.append(str(order_data["operation_id"]) + " " + str(order_data["order_type"] +
                                                                               " " + str(order_data["ticker"])))

            elif order_data['order_type'] == "Sell" and order_data['instrument'] == "stocks":
                # TODO make calcs for USD stocs and current USDRUB in portfolio (need to update data)
                # add money to user_id wallet
                wallet_add_money_for_sell(order_data)
                # add data about Sell order to portfolio history file
                trader.portfolio_history_add_order(order_data)
                # delete data about orders from portfolio current and write to portfolio history
                trader.portfolio_move_from_current(order_data)

                done_orders.append(order_data["operation_id"])

            elif order_data['order_type'] == "Buy" and order_data['instrument'] == "currency":
                data_query = [order_data["user_id"], "USD", order_data["amount"], order_data["operation_id"],
                              order_data["instrument"], order_data["order_type"]]
                # add money to trader wallet
                trader.wallet_add_money(data_query)

                # add data about done order to portfolio_current TODO keep as one operation_id
                # 1 check if there any USDRUB in portfolio current
                portfolio_all_data = trader.portfolio_show_current(order_data["user_id"])
                portfolio_data = (portfolio_all_data[portfolio_all_data["ticker"] == order_data["ticker"]])
                if not portfolio_data.empty:

                    # get data about USDRUB from current portfolio

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

                    done_orders.append(str(order_data["operation_id"]) + " " + str(order_data["order_type"] +
                                                                                   " " + str(order_data["ticker"])))

                # there is no orders in current portfolio add one
                elif portfolio_data.empty:

                    trader.portfolio_current_add_order(order_data)
                    done_orders.append(str(order_data["operation_id"]) + " " + str(order_data["order_type"] +
                                                                                   " " + str(order_data["ticker"])))

            elif order_data['order_type'] == "Sell" and order_data['instrument'] == "currency":

                # add data to wallet history and add money to user_id wallet
                wallet_add_money_for_sell(order_data)

                # 1) subtract order amount from amount in portfolio_current
                # 2) subtract order total price from Number in portfolio_current
                # recalculate average price
                # 3) add order commission to Number in portfolio_current and rewrite portfolio_current file
                portfolio_all_data = trader.portfolio_show_current(order_data["user_id"])
                portfolio_data = (portfolio_all_data[portfolio_all_data["ticker"] == order_data["ticker"]])
                if not portfolio_data.empty:
                    # if 0 $ amount at current wallet
                    # order_amount == portfolio_amount
                    current_wallet_data = trader.wallet_show_current(account_id)
                    # get data about USDRUB from current portfolio
                    # calculate average price for new order: sum of orders order_price_total / sum of amounts
                    order_total_price = order_data["order_price_total"]
                    order_amount = order_data["amount"]
                    order_commission = order_data["commission"]
                    portfolio_total_price = (portfolio_data["order_price_total"]).values[0]
                    portfolio_amount = portfolio_data["amount"].values[0]
                    portfolio_commission = portfolio_data["commission"].values[0]
                    if current_wallet_data["USD"] == 0 and order_amount == portfolio_amount:

                        # this is last order, remove from portfolio
                        get_index_number = portfolio_data["commission"].index.values[0]

                        without_dropped_data = portfolio_all_data.drop([get_index_number])
                        # save to csv
                        without_dropped_data.to_csv("files/portfolio_current_" + str(account_id) + ".csv",
                                                    index=False)
                        # order done sent response to handlers
                        done_orders.append(str(order_data["operation_id"]) + " " + str(order_data["order_type"] +
                                                                                       " " + str(order_data["ticker"])))

                    else:

                        dif_of_amounts = round(portfolio_amount - order_amount, 2)

                        dif_of_price_totals = round(portfolio_total_price - order_total_price, 2)

                        average_price = round(dif_of_price_totals / dif_of_amounts, 2)

                        sum_of_commissions = round(order_commission + portfolio_commission, 2)

                        # next step: delete from portfolio old data and save new
                        get_index_number = portfolio_data["commission"].index.values[0]

                        without_dropped_data = portfolio_all_data.drop([get_index_number])

                        df = without_dropped_data.append({"order_type": order_data["order_type"],
                                                          "ticker": order_data["ticker"],
                                                          "order_price": average_price,
                                                          "amount": dif_of_amounts,
                                                          "currency": order_data["currency"],
                                                          "order_price_total": dif_of_price_totals,
                                                          "commission": sum_of_commissions,
                                                          "order_created_at": order_data["created_at"],
                                                          "operation_id": order_data["operation_id"],
                                                          "instrument": order_data["instrument"],
                                                          "order_done_at": order_data["order_done_at"],
                                                          },
                                                         ignore_index=True)
                        # save to csv
                        df.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=False)

                        # order done sent response to handlers

                        done_orders.append(str(order_data["operation_id"]) + " " + str(order_data["order_type"] +
                                                                                       " " + str(order_data["ticker"])))

                # delete data about order if amount in order = amount from portfolio current


        elif not order_status_response[0]:
            not_done_orders.append(str(order_data["operation_id"]) + " " + str(order_data["order_type"] \
                                                                               + " " + str(
                order_data["ticker"] + " " + str(order_data["order_price"]
                                                 ))))

    # sent changes in response
    order_data = "Неисполненные заявки: " + str(not_done_orders) + "\n\nВыполненые заявки: " + str(done_orders)

    response = [False, order_data]
    return response
