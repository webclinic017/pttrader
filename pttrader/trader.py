import pandas as pd
from pathlib import Path
from random import randint
import json
import sys
import broker
import market
from time import sleep

from pytz import timezone
from openapi_client import openapi
from datetime import datetime, timedelta

pd.set_option('display.max_columns', None)
import pickle


def get_random_id():
    """
    random id generator foo for store same condition at one place
    :return: int()
    """
    random_id = randint(100000, 999999)
    return random_id


def wallet_create_new(account_id):
    """
    This function creates two files:
    first for storing wallet operations history
    and second for current wallet balance

    """

    main_currency = "RUB"
    broker_commission = 0.3
    if main_currency == "RUB":

        wallet_current_data = {main_currency: 0., "USD": 0., "broker_commission": broker_commission}
        with open("files/wallet_current_" + str(account_id) + ".txt", 'w+') as file:
            file.write(json.dumps(wallet_current_data))

        wallet_history_df = pd.DataFrame(columns=["operation_id", "currency", "amount", "operation",
                                                  "instrument", "date_time",
                                                  ])
        wallet_history_df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)

        # check if files are created
        if is_wallet_history_exist(account_id) and is_wallet_current_exist(account_id):
            return True
        else:
            print("Something goes wrong, check function", sys._getframe().f_code.co_name)
            return False
    elif main_currency == "USD":
        # for future dev, to choose main currency
        print("Sorry, only RUB supported now.")
        return False
    else:
        # for future dev, to choose main currency
        print("Sorry, only RUB supported now. You type:", main_currency)
        return False


def wallet_set_broker_commission(data_query):
    """
    This function used to set broker's commission rate, which was set by default when wallet has created
    """
    account_id = data_query[0]
    broker_commission = data_query[1]
    # check if this file exist
    if is_wallet_current_exist(account_id) and is_wallet_history_exist(account_id):

        wallet_current_data = wallet_show_current(account_id)
        wallet_current_data["broker_commission"] = broker_commission
        # write new data to wallet_current
        with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
            file.write(json.dumps(wallet_current_data))

        return True

    elif not is_wallet_current_exist(account_id) and is_wallet_history_exist(account_id):
        if wallet_create_new(account_id):
            wallet_current_data = wallet_show_current(account_id)
            wallet_current_data["broker_commission"] = broker_commission
            # write new data to wallet_current
            with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                file.write(json.dumps(wallet_current_data))
                return True

    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return False


def wallet_add_money(data_query):
    """
    This function used to add money to current wallet file
    and write operation to wallet_history file
    fist operation will add data to wallet_history data
    second operation will calculate data and add to current wallet data

     data_query = [current_user_id, currency, amount, operation_id]

    """
    account_id = data_query[0]
    currency = data_query[1]
    amount = data_query[2]
    operation_id = data_query[3]
    instrument = data_query[4]
    operation = data_query[5]

    current_time = broker.get_current_time()

    # check if this file exist
    if is_wallet_current_exist(account_id) and is_wallet_history_exist(account_id):
        wallet_history_data = wallet_show_history(account_id)
        wallet_current_data = wallet_show_current(account_id)

        # second operation will calculate and write new data to current state of wallet
        if currency == "RUB":
            wallet_current_data["RUB"] += amount
            # do round function for same numbers data in all files
            wallet_current_data["RUB"] = round(wallet_current_data["RUB"], 2)
            df = wallet_history_data.append({"currency": currency,
                                             "amount": amount,
                                             "date_time": current_time,
                                             "operation": operation,
                                             "operation_id": operation_id,
                                             "instrument": instrument},
                                            ignore_index=True)
            # write new data to wallet_history
            df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
            # write new data to wallet_current
            with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                file.write(json.dumps(wallet_current_data))

            return True

        elif currency == "USD":
            wallet_current_data["USD"] += amount
            wallet_current_data["USD"] = round(wallet_current_data["USD"], 2)
            df = wallet_history_data.append({"currency": currency,
                                             "amount": amount,
                                             "date_time": current_time,
                                             "operation": operation,
                                             "operation_id": operation_id,
                                             "instrument": instrument},
                                            ignore_index=True)
            # write new data to wallet_history
            df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
            # write new data to wallet_current
            with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                file.write(json.dumps(wallet_current_data))

            return True
    # may be delete this, because it is reserved if wallet not created at /start
    elif not is_wallet_current_exist(account_id) and not is_wallet_history_exist(account_id):
        if wallet_create_new(account_id):
            wallet_history_data = wallet_show_history(account_id)
            wallet_current_data = wallet_show_current(account_id)

            currency = str()
            for key in wallet_current_data.keys():
                currency = key

            operation = "add"
            instrument = "currency"
            # random id generator foo
            operation_id = get_random_id()

            # second operation will calculate and write new data to current state of wallet

            if currency == "RUB":
                wallet_current_data["RUB"] += amount
                df = wallet_history_data.append({"currency": currency,
                                                 "amount": amount,
                                                 "date_time": current_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                return True
            elif currency == "USD":
                wallet_current_data["USD"] += amount
                df = wallet_history_data.append({"currency": currency,
                                                 "amount": amount,
                                                 "date_time": current_time,
                                                 "operation": operation,
                                                 "operation_id": operation_id,
                                                 "instrument": instrument},
                                                ignore_index=True)

                df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
                with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                    file.write(json.dumps(wallet_current_data))
                return True

    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return False


def wallet_show_current(account_id):
    """
    This function return current data of user wallet, stored in local file
    """

    if is_wallet_current_exist(account_id):
        with open("files/wallet_current_" + str(account_id) + ".txt", "r") as file:
            data = file.read()
        wallet_current_data = json.loads(data)
        return wallet_current_data
    elif not is_wallet_current_exist(account_id):
        if wallet_create_new(account_id):
            with open("files/wallet_current_" + str(account_id) + ".txt", "r") as file:
                data = file.read()
            wallet_current_data = json.loads(data)
            return wallet_current_data
    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return


def wallet_show_history(account_id):
    """
    This function return user wallet history data , stored in local file
    """
    if is_wallet_history_exist(account_id):
        wallet_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
        return wallet_data

    elif not is_wallet_history_exist(account_id):
        if wallet_create_new(account_id):
            wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
            return wallet_history_data

    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return


def is_wallet_current_exist(account_id):
    wallet_data = Path("files/wallet_current_" + str(account_id) + ".txt")
    if Path("files").is_dir() and wallet_data.is_file():
        return True
    else:

        return False


def is_wallet_history_exist(account_id):
    wallet_data = Path("files/wallet_history_" + str(account_id) + ".csv")
    if Path("files").is_dir() and wallet_data.is_file():
        return True
    else:

        return False


# this functions for portfolio
def portfolio_create_new(account_id):
    """
    This function creates two .csv files:
    first for storing portfolio operations history
    and second for current portfolio state
    """

    portfolio_current_df = pd.DataFrame(columns=["operation_id", "order_type", "ticker", "order_price", "amount",
                                                 "currency", "order_price_total", "commission", "instrument",
                                                 "order_description",
                                                 "order_created_at", "order_done_at",
                                                 ])

    portfolio_current_df.to_csv("files/portfolio_history_" + str(account_id) + ".csv", index=False)

    portfolio_history_df = pd.DataFrame(columns=["operation_id", "order_type", "ticker", "order_price", "amount",
                                                 "currency", "order_price_total", "commission", "instrument",
                                                 "order_description",
                                                 "order_created_at", "order_done_at",
                                                 ])

    portfolio_history_df.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=False)

    if is_portfolio_current_exist(account_id) and is_portfolio_history_exist(account_id):
        return True
    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return False


def is_portfolio_current_exist(account_id):
    portfolio_data = Path("files/portfolio_current_" + str(account_id) + ".csv")
    if Path("files").is_dir() and portfolio_data.is_file():
        return True
    else:
        return False


def is_portfolio_history_exist(account_id):
    portfolio_data = Path("files/portfolio_history_" + str(account_id) + ".csv")
    if Path("files").is_dir() and portfolio_data.is_file():
        return True
    else:
        return False


def portfolio_current_add_order(data):
    """
     data:
     {'order_type': 'Buy', 'user_id': 39460, 'ticker': 'NMTP', 'order_price': 7.8, 'amount': 10, 'currency': 'RUB',
      'order_price_total': 7800.0, 'commission' : 0.3,'created_at': 1618331390.686862, 'operation_id': 73483, 'instrument': 'stocks',
      'order_status': False, 'order_done_at': 1618246800.0}
     """

    account_id = data["user_id"]
    operation_id = data['operation_id']
    if is_portfolio_current_exist(account_id):
        portfolio_current_data = pd.read_csv("files/portfolio_current_" + str(account_id) + ".csv")
        df = portfolio_current_data.append({"order_type": data["order_type"],
                                            "ticker": data["ticker"],
                                            "order_price": data["order_price"],
                                            "amount": data["amount"],
                                            "currency": data["currency"],
                                            "order_price_total": data["order_price_total"],
                                            "commission": data["commission"],
                                            "order_created_at": data["created_at"],
                                            "operation_id": data["operation_id"],
                                            "instrument": data["instrument"],
                                            "order_done_at": data["order_done_at"],
                                            "order_description": data["order_description"],
                                            },
                                           ignore_index=True)

        df.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=False)
        return True

    elif not is_portfolio_current_exist(account_id):
        if portfolio_create_new(account_id):
            portfolio_current_data = pd.read_csv("files/portfolio_current_" + str(account_id) + ".csv")
            df = portfolio_current_data.append({"order_type": data["order_type"],
                                                "ticker": data["ticker"],
                                                "order_price": data["order_price"],
                                                "amount": data["amount"],
                                                "currency": data["currency"],
                                                "order_price_total": data["order_price_total"],
                                                "commission": data["commission"],
                                                "order_created_at": data["created_at"],
                                                "operation_id": data["operation_id"],
                                                "instrument": data["instrument"],
                                                "order_done_at": data["order_done_at"],
                                                "order_description": data["order_description"],
                                                },
                                               ignore_index=True)

            df.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=False)
            # check if order is write to the file
            data = portfolio_show_current(account_id)

            check_portfolio_data = (data[data["operation_id"] == operation_id])

            if not check_portfolio_data.empty:
                return True
    else:
        print("Something wrong, check: portfolio_current_add_order ")
        return False


def portfolio_history_add_order(data):
    """
     data:
     {'order_type': 'Buy', 'user_id': 39460, 'ticker': 'NMTP', 'order_price': 7.8, 'amount': 10, 'currency': 'RUB',
      'order_price_total': 7800.0, 'created_at': 1618331390.686862, 'operation_id': 73483, 'instrument': 'stocks',
      'order_status': False, 'order_done_at': 1618246800.0}
     """

    account_id = data["user_id"]
    operation_id = data['operation_id']
    if is_portfolio_history_exist(account_id):
        portfolio_history_data = pd.read_csv("files/portfolio_history_" + str(account_id) + ".csv")
        df = portfolio_history_data.append({"order_type": data["order_type"],
                                            "ticker": data["ticker"],
                                            "order_price": data["order_price"],
                                            "amount": data["amount"],
                                            "currency": data["currency"],
                                            "order_price_total": data["order_price_total"],
                                            "commission": data["commission"],
                                            "order_created_at": data["created_at"],
                                            "operation_id": data["operation_id"],
                                            "instrument": data["instrument"],
                                            "order_done_at": data["order_done_at"],
                                            "order_description": data["order_description"],
                                            },
                                           ignore_index=True)

        df.to_csv("files/portfolio_history_" + str(account_id) + ".csv", index=False)
        return True

    elif not is_portfolio_history_exist(account_id):
        if portfolio_create_new(account_id):
            portfolio_history_data = pd.read_csv("files/portfolio_history_" + str(account_id) + ".csv")
            df = portfolio_history_data.append({"order_type": data["order_type"],
                                                "ticker": data["ticker"],
                                                "order_price": data["order_price"],
                                                "amount": data["amount"],
                                                "currency": data["currency"],
                                                "order_price_total": data["order_price_total"],
                                                "commission": data["commission"],
                                                "order_created_at": data["created_at"],
                                                "operation_id": data["operation_id"],
                                                "instrument": data["instrument"],
                                                "order_done_at": data["order_done_at"],
                                                "order_description": data["order_description"],
                                                },
                                               ignore_index=True)

            df.to_csv("files/portfolio_history_" + str(account_id) + ".csv", index=False)
            # check if order is write to the file
            data = portfolio_show_history(account_id)

            check_portfolio_data = (data[data["operation_id"] == operation_id])

            if not check_portfolio_data.empty:
                return True
    else:
        print("Something wrong, check: portfolio_current_add_order ")
        return False


def portfolio_show_current(account_id):
    """
    This function show current data of portfolio, stored in .csv file
    """
    if is_portfolio_current_exist(account_id):
        current_data = pd.read_csv("files/portfolio_current_" + str(account_id) + ".csv")
        return current_data
    elif not is_portfolio_current_exist(account_id):
        if portfolio_create_new(account_id):
            current_data = pd.read_csv("files/portfolio_current_" + str(account_id) + ".csv")
            return current_data
    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return


def portfolio_show_history(account_id):
    """
    This function show history data of portfolio, stored in .csv file
    """
    if is_portfolio_history_exist(account_id):
        data = pd.read_csv("files/portfolio_history_" + str(account_id) + ".csv")
        return data
    elif not is_portfolio_history_exist(account_id):
        if portfolio_create_new(account_id):
            data = pd.read_csv("files/portfolio_history_" + str(account_id) + ".csv")
            return data

    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return


def portfolio_move_from_current(order_data):
    """
    open file portfolio_current
    find operation_id (same as in order_data["operation id"] and order_type == "Buy"
    write this data to portfolio_history csv
    delete this data from dataframe and save it to portfolio_current csv
    :return: True or False
    """
    account_id = order_data["user_id"]
    operation_id = order_data["operation_id"]

    order_type = "Buy"

    portfolio_all_data = portfolio_show_current(account_id)
    portfolio_filtered_data = (portfolio_all_data[portfolio_all_data["operation_id"] == operation_id])
    if not portfolio_filtered_data.empty:
        portfolio_hist = portfolio_show_history(account_id)
        portfolio_history = portfolio_hist.append(portfolio_filtered_data)
        # print("portfolio_history \n", portfolio_history)
        # save data to portfolio history csv
        portfolio_history.to_csv("files/portfolio_history_" + str(account_id) + ".csv", index=False)

        portfolio_cur = portfolio_all_data.set_index("operation_id")
        portfolio_cur_dropped = portfolio_cur.drop(operation_id)

        # save data to portfolio current csv
        portfolio_cur_dropped.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=True)

        return True

    elif portfolio_filtered_data.empty:
        print(" data not found")
        return False


def is_all_operations_history_exist(account_id):
    operations_data = Path("files/all_operations_history_" + str(account_id) + ".csv")
    if Path("files").is_dir() and operations_data.is_file():
        return True
    else:
        return False


def create_operations_history_file(account_id):
    # this functions for portfolio
    """
    This function creates  .csv file:
    for storing all operations history

    """

    all_operations_history_df = pd.DataFrame(
        columns=["operation_id", "operation_type", "instrument_type", "ticker", "currency", "price",
                 "quantity", "payment", "commission", "created_at", "done_at"
                 ])

    all_operations_history_df.to_csv("files/all_operations_history_" + str(account_id) + ".csv", index=False)
    # check is file created
    if is_all_operations_history_exist(account_id):
        return True
    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return False


def get_operations_data_from_broker(account_id):
    """
    return list
    """
    # todo choose period
    history_period = 10
    now = datetime.now(tz=timezone('Europe/Moscow'))
    yesterday = now - timedelta(days=history_period)
    client = market.tinkof_api_auth()
    ops = client.operations.operations_get(_from=yesterday.isoformat(), to=now.isoformat())
    operations_data = ops.payload

    with open("files/operations_data_" + str(account_id) + ".data", 'wb') as file:
        # file.write(operations_data.operations)
        pickle.dump(operations_data.operations, file)


def check_last_date_in_operations_data(account_id):
    now = datetime.now(tz=timezone('Europe/Moscow'))

    current_data = pd.read_csv("files/all_operations_history_" + str(account_id) + ".csv")

    return True


def save_operations_to_history(account_id):
    client = market.tinkof_api_auth()
    # all_operations_history_df = pd.DataFrame(
    #     columns=["operation_id", "operation_type", "instrument_type", "ticker", "currency", "price",
    #              "quantity", "payment", "commission", "created_at", "done_at"
    #              ])
    # if already exist history - > rewrite

    if is_all_operations_history_exist(account_id):
        print("History exist")
        all_operations_history_df = pd.read_csv("files/all_operations_history_" + str(account_id) + ".csv")

        # file exist, check last date and update

        # update
        get_operations_data_from_broker(account_id)
        with open("files/operations_data_" + str(account_id) + ".data", "rb") as file:
            list_of_operations = pickle.load(file)

        print(type(list_of_operations))
        print(len(list_of_operations))
        count = 0
        for operation in list_of_operations:
            sleep(.5)
            count += 1
            print("Counter: ", count)
            operation_id = []
            operation_type = []  # Buy, Sell
            instrument_type = []  # Stock,
            figi = []  # need to convert to ticker name
            ticker = []  # store as ticker
            currency = []  # RUB, USD
            price = []
            quantity = []  # like amount
            payment = []  # like order price total
            commission = []
            created_at = []
            done_at = []
            if operation.operation_type == 'Buy' and operation.status == "Done":
                print(operation.operation_type)

                operation_id.append(operation.id)
                operation_type.append(operation.operation_type)
                instrument_type.append(operation.instrument_type)  # Stock,
                figi = operation.figi  # need to convert to ticker name
                figi_data = client.market.market_search_by_figi_get(figi)  # get ticker by figi
                ticker.append(figi_data.payload.ticker)  # store as ticker
                currency.append(operation.currency)  # RUB, USD
                price.append(operation.price)
                quantity.append(operation.quantity)  # like amount
                payment.append(operation.payment)  # like order price total
                commission_data = operation.commission
                if commission_data is not None:
                    commission.append(commission_data.value)
                else:
                    commission.append("None")

                # TODO keep same timeformat as usual
                done_at_data = operation.trades

                if done_at_data is not None:
                    done_at.append((done_at_data[0].date).isoformat('T'))

                elif done_at_data is None:
                    done_at.append((operation.date).isoformat('T'))

                created_at.append(operation.date.isoformat('T'))
                # print("Counter:", count)
                # print(operation_id)
                # print(operation_type)  # Buy, Sell
                # print(instrument_type)  # Stock,
                #
                # print(ticker) # store as ticker
                # print(currency)  # RUB, USD
                # print(price)
                # print(quantity)  # like amount
                # print(payment)  # like order price total
                # print(commission)
                # print(created_at)
                # print(done_at)

                all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                              "operation_type": operation_type[0],
                                                                              "instrument_type": instrument_type[0],
                                                                              "ticker": ticker[0],
                                                                              "currency": currency[0],
                                                                              "price": price[0],
                                                                              "quantity": quantity[0],
                                                                              "payment": payment[0],
                                                                              "commission": commission[0],
                                                                              "created_at": created_at[0],
                                                                              "done_at": done_at[0]
                                                                              }, ignore_index=True)

            elif operation.operation_type == 'Sell' and operation.status == "Done":
                print(operation.operation_type)

                operation_id.append(operation.id)
                operation_type.append(operation.operation_type)
                instrument_type.append(operation.instrument_type)  # Stock,
                figi = operation.figi  # need to convert to ticker name
                figi_data = client.market.market_search_by_figi_get(figi)  # get ticker by figi
                ticker.append(figi_data.payload.ticker)  # store as ticker
                currency.append(operation.currency)  # RUB, USD
                price.append(operation.price)
                quantity.append(operation.quantity)  # like amount
                payment.append(operation.payment)  # like order price total
                commission_data = operation.commission
                if commission_data is not None:
                    commission.append(commission_data.value)

                # TODO keep same timeformat as usual
                done_at_data = operation.trades

                if done_at_data is not None:
                    done_at.append((done_at_data[0].date).isoformat('T'))

                elif done_at_data is None:
                    done_at.append((operation.date).isoformat('T'))

                created_at.append(operation.date.isoformat('T'))

                all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                              "operation_type": operation_type[0],
                                                                              "instrument_type": instrument_type[0],
                                                                              "ticker": ticker[0],
                                                                              "currency": currency[0],
                                                                              "price": price[0],
                                                                              "quantity": quantity[0],
                                                                              "payment": payment[0],
                                                                              "commission": commission[0],
                                                                              "created_at": created_at[0],
                                                                              "done_at": done_at[0]
                                                                              }, ignore_index=True)
            # dict_keys(['Sell', 'BrokerCommission', 'Buy', 'PayOut', 'PayIn', 'MarginCommission', 'Dividend', 'ServiceCommission'])
            elif operation.operation_type == 'Dividend':
                print(operation.operation_type)
                operation_id.append(operation.id)
                figi = operation.figi  # need to convert to ticker name
                figi_data = client.market.market_search_by_figi_get(figi)
                ticker.append(figi_data.payload.ticker)
                currency.append(operation.currency)
                operation_type.append(operation.operation_type)
                payment.append(operation.payment)  # like order price total
                done_at.append(operation.date.isoformat('T'))

                all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                              "operation_type": operation_type[0],

                                                                              "ticker": ticker[0],
                                                                              "currency": currency[0],

                                                                              "payment": payment[0],

                                                                              "done_at": done_at[0]
                                                                              }, ignore_index=True)
            #
            #
            elif operation.operation_type == 'ServiceCommission':
                print(operation.operation_type)
                operation_id.append(operation.id)
                currency.append(operation.currency)
                operation_type.append(operation.operation_type)
                payment.append(operation.payment)  # like order price total
                done_at.append(operation.date.isoformat('T'))

                all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                              "operation_type": operation_type[0],

                                                                              "currency": currency[0],

                                                                              "payment": payment[0],

                                                                              "done_at": done_at[0]
                                                                              }, ignore_index=True)
            #
            #
            elif operation.operation_type == 'MarginCommission':
                print(operation.operation_type)
                operation_id.append(operation.id)
                currency.append(operation.currency)
                operation_type.append(operation.operation_type)
                payment.append(operation.payment)  # like order price total
                done_at.append(operation.date.isoformat('T'))

                all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                              "operation_type": operation_type[0],

                                                                              "currency": currency[0],

                                                                              "payment": payment[0],

                                                                              "done_at": done_at[0]
                                                                              }, ignore_index=True)
            #
            elif operation.operation_type == 'PayIn':
                print(operation.operation_type)
                operation_id.append(operation.id)
                currency.append(operation.currency)
                operation_type.append(operation.operation_type)
                payment.append(operation.payment)  # like order price total
                done_at.append(operation.date.isoformat('T'))

                all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                              "operation_type": operation_type[0],

                                                                              "currency": currency[0],

                                                                              "payment": payment[0],

                                                                              "done_at": done_at[0]
                                                                              }, ignore_index=True)
            #
            elif operation.operation_type == 'PayOut':
                print(operation.operation_type)
                operation_id.append(operation.id)
                currency.append(operation.currency)
                operation_type.append(operation.operation_type)
                payment.append(operation.payment)  # like order price total
                done_at.append(operation.date.isoformat('T'))

                all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                              "operation_type": operation_type[0],

                                                                              "currency": currency[0],

                                                                              "payment": payment[0],

                                                                              "done_at": done_at[0]
                                                                              }, ignore_index=True)
            #
            elif operation.operation_type == 'BrokerCommission':
                print(operation.operation_type)
                operation_id.append(operation.id)
                figi = operation.figi  # need to convert to ticker name
                figi_data = client.market.market_search_by_figi_get(figi)
                ticker.append(figi_data.payload.ticker)
                currency.append(operation.currency)
                operation_type.append(operation.operation_type)
                payment.append(operation.payment)  # like order price total
                done_at.append(operation.date.isoformat('T'))

                all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                              "operation_type": operation_type[0],

                                                                              "ticker": ticker[0],
                                                                              "currency": currency[0],

                                                                              "payment": payment[0],

                                                                              "done_at": done_at[0]
                                                                              }, ignore_index=True)

        # print(all_operations_history_df.head)
        print("Save to csv with id: ", account_id)
        all_operations_history_df.to_csv("files/all_operations_history_" + str(account_id) + ".csv", index=False)

        all_operations_history_updated = pd.read_csv("files/all_operations_history_" + str(account_id) + ".csv")

        from_index = (len(all_operations_history_updated) - 1)
        data = all_operations_history_updated.tail(1)
        from_date = (data["done_at"][from_index])

        data = all_operations_history_updated.head(1)
        to_date = (data["done_at"][0])
        all_operations = len(list_of_operations)

        response = [True, all_operations, from_date, to_date]

        return response

    elif not is_all_operations_history_exist(account_id):
        print("new acc")
        if create_operations_history_file(account_id):

            all_operations_history_df = pd.read_csv("files/all_operations_history_" + str(account_id) + ".csv")

            # list_of_operations.append(get_operations_data_from_broker(account_id))
            get_operations_data_from_broker(account_id)
            with open("files/operations_data_" + str(account_id) + ".data", "rb") as file:
                list_of_operations = pickle.load(file)

            print(type(list_of_operations))
            print(len(list_of_operations))
            count = 0
            for operation in list_of_operations:
                sleep(.5)
                count += 1
                print("Counter: ", count)

                operation_id = []
                operation_type = []  # Buy, Sell
                instrument_type = []  # Stock,
                figi = []  # need to convert to ticker name
                ticker = []  # store as ticker
                currency = []  # RUB, USD
                price = []
                quantity = []  # like amount
                payment = []  # like order price total
                commission = []
                created_at = []
                done_at = []
                if operation.operation_type == 'Buy' and operation.status == "Done":
                    print(operation.operation_type)

                    operation_id.append(operation.id)
                    operation_type.append(operation.operation_type)
                    instrument_type.append(operation.instrument_type)  # Stock,
                    figi = operation.figi  # need to convert to ticker name
                    figi_data = client.market.market_search_by_figi_get(figi)  # get ticker by figi
                    ticker.append(figi_data.payload.ticker)  # store as ticker
                    currency.append(operation.currency)  # RUB, USD
                    price.append(operation.price)
                    quantity.append(operation.quantity)  # like amount
                    payment.append(operation.payment)  # like order price total
                    commission_data = operation.commission
                    if commission_data is not None:
                        commission.append(commission_data.value)
                    else:
                        commission.append("None")

                    # TODO keep same timeformat as usual
                    done_at_data = operation.trades

                    if done_at_data is not None:
                        done_at.append((done_at_data[0].date).isoformat('T'))

                    elif done_at_data is None:
                        done_at.append((operation.date).isoformat('T'))

                    created_at.append(operation.date.isoformat('T'))
                    # print("Counter:", count)
                    # print(operation_id)
                    # print(operation_type)  # Buy, Sell
                    # print(instrument_type)  # Stock,
                    #
                    # print(ticker) # store as ticker
                    # print(currency)  # RUB, USD
                    # print(price)
                    # print(quantity)  # like amount
                    # print(payment)  # like order price total
                    # print(commission)
                    # print(created_at)
                    # print(done_at)

                    all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                                  "operation_type": operation_type[0],
                                                                                  "instrument_type": instrument_type[0],
                                                                                  "ticker": ticker[0],
                                                                                  "currency": currency[0],
                                                                                  "price": price[0],
                                                                                  "quantity": quantity[0],
                                                                                  "payment": payment[0],
                                                                                  "commission": commission[0],
                                                                                  "created_at": created_at[0],
                                                                                  "done_at": done_at[0]
                                                                                  }, ignore_index=True)

                elif operation.operation_type == 'Sell' and operation.status == "Done":
                    print(operation.operation_type)

                    operation_id.append(operation.id)
                    operation_type.append(operation.operation_type)
                    instrument_type.append(operation.instrument_type)  # Stock,
                    figi = operation.figi  # need to convert to ticker name
                    figi_data = client.market.market_search_by_figi_get(figi)  # get ticker by figi
                    ticker.append(figi_data.payload.ticker)  # store as ticker
                    currency.append(operation.currency)  # RUB, USD
                    price.append(operation.price)
                    quantity.append(operation.quantity)  # like amount
                    payment.append(operation.payment)  # like order price total
                    commission_data = operation.commission
                    if commission_data is not None:
                        commission.append(commission_data.value)

                    # TODO keep same timeformat as usual
                    done_at_data = operation.trades

                    if done_at_data is not None:
                        done_at.append((done_at_data[0].date).isoformat('T'))

                    elif done_at_data is None:
                        done_at.append((operation.date).isoformat('T'))

                    created_at.append(operation.date.isoformat('T'))

                    all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                                  "operation_type": operation_type[0],
                                                                                  "instrument_type": instrument_type[0],
                                                                                  "ticker": ticker[0],
                                                                                  "currency": currency[0],
                                                                                  "price": price[0],
                                                                                  "quantity": quantity[0],
                                                                                  "payment": payment[0],
                                                                                  "commission": commission[0],
                                                                                  "created_at": created_at[0],
                                                                                  "done_at": done_at[0]
                                                                                  }, ignore_index=True)
                # dict_keys(['Sell', 'BrokerCommission', 'Buy', 'PayOut', 'PayIn', 'MarginCommission', 'Dividend', 'ServiceCommission'])
                elif operation.operation_type == 'Dividend':
                    print(operation.operation_type)
                    operation_id.append(operation.id)
                    figi = operation.figi  # need to convert to ticker name
                    figi_data = client.market.market_search_by_figi_get(figi)
                    ticker.append(figi_data.payload.ticker)
                    currency.append(operation.currency)
                    operation_type.append(operation.operation_type)
                    payment.append(operation.payment)  # like order price total
                    done_at.append(operation.date.isoformat('T'))

                    all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                                  "operation_type": operation_type[0],

                                                                                  "ticker": ticker[0],
                                                                                  "currency": currency[0],

                                                                                  "payment": payment[0],

                                                                                  "done_at": done_at[0]
                                                                                  }, ignore_index=True)

                elif operation.operation_type == 'ServiceCommission':
                    print(operation.operation_type)
                    operation_id.append(operation.id)
                    currency.append(operation.currency)
                    operation_type.append(operation.operation_type)
                    payment.append(operation.payment)  # like order price total
                    done_at.append(operation.date.isoformat('T'))

                    all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                                  "operation_type": operation_type[0],

                                                                                  "currency": currency[0],

                                                                                  "payment": payment[0],

                                                                                  "done_at": done_at[0]
                                                                                  }, ignore_index=True)


                elif operation.operation_type == 'MarginCommission':
                    print(operation.operation_type)
                    operation_id.append(operation.id)
                    currency.append(operation.currency)
                    operation_type.append(operation.operation_type)
                    payment.append(operation.payment)  # like order price total
                    done_at.append(operation.date.isoformat('T'))

                    all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                                  "operation_type": operation_type[0],

                                                                                  "currency": currency[0],

                                                                                  "payment": payment[0],

                                                                                  "done_at": done_at[0]
                                                                                  }, ignore_index=True)
                #
                elif operation.operation_type == 'PayIn':
                    print(operation.operation_type)
                    operation_id.append(operation.id)
                    currency.append(operation.currency)
                    operation_type.append(operation.operation_type)
                    payment.append(operation.payment)  # like order price total
                    done_at.append(operation.date.isoformat('T'))

                    all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                                  "operation_type": operation_type[0],

                                                                                  "currency": currency[0],

                                                                                  "payment": payment[0],

                                                                                  "done_at": done_at[0]
                                                                                  }, ignore_index=True)
                #
                elif operation.operation_type == 'PayOut':
                    print(operation.operation_type)
                    operation_id.append(operation.id)
                    currency.append(operation.currency)
                    operation_type.append(operation.operation_type)
                    payment.append(operation.payment)  # like order price total
                    done_at.append(operation.date.isoformat('T'))

                    all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                                  "operation_type": operation_type[0],

                                                                                  "currency": currency[0],

                                                                                  "payment": payment[0],

                                                                                  "done_at": done_at[0]
                                                                                  }, ignore_index=True)
                #
                elif operation.operation_type == 'BrokerCommission':
                    print(operation.operation_type)
                    operation_id.append(operation.id)
                    figi = operation.figi  # need to convert to ticker name
                    figi_data = client.market.market_search_by_figi_get(figi)
                    ticker.append(figi_data.payload.ticker)
                    currency.append(operation.currency)
                    operation_type.append(operation.operation_type)
                    payment.append(operation.payment)  # like order price total
                    done_at.append(operation.date.isoformat('T'))

                    all_operations_history_df = all_operations_history_df.append({"operation_id": operation_id[0],
                                                                                  "operation_type": operation_type[0],

                                                                                  "ticker": ticker[0],
                                                                                  "currency": currency[0],

                                                                                  "payment": payment[0],

                                                                                  "done_at": done_at[0]
                                                                                  }, ignore_index=True)

            # print(all_operations_history_df.head)
            print("Account id:", account_id)
            all_operations_history_df.to_csv("files/all_operations_history_" + str(account_id) + ".csv", index=False)

            all_operations_history_updated = pd.read_csv("files/all_operations_history_" + str(account_id) + ".csv")

            from_index = (len(all_operations_history_updated) - 1)
            data = all_operations_history_updated.tail(1)
            from_date = (data["done_at"][from_index])

            data = all_operations_history_updated.head(1)
            to_date = (data["done_at"][0])
            all_operations = len(list_of_operations)

            response = [True, all_operations, from_date, to_date]
            return response  # dates from xxx to xxx
    else:
        print("Something wrong, check: portfolio_current_add_order ")
        return False


def get_portfolio_data_from_broker(account_id) -> list:
    client = market.tinkof_api_auth()
    portfolio = client.portfolio.portfolio_get()
    positions = portfolio.payload

    return positions.positions


def update_portfolio(account_id):
    """
        This function creates two .csv files:
        first for storing portfolio operations history
        and second for current portfolio state
        """
    portfolio_current_df = pd.DataFrame(columns=["sector", "instrument_type", "ticker", "balance", "lots",
                                                 "average_position_price",
                                                 "currency",
                                                 ])
    portfolio_current_df.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=False)

    # sector = []
    # instrument_type = []
    # ticker = []
    # balance = []
    # lots = []
    # average_position_price = []
    # currency = []

    # get current portfolio data from real broker
    portfolio = get_portfolio_data_from_broker(account_id)
    portfolio_current_df = pd.read_csv("files/portfolio_current_" + str(account_id) + ".csv")

    for open_position in portfolio:
        figi = open_position.figi
        # figi_to_ticker
        ticker = market.get_ticker_by(figi)
        # after obtain ticker by figi we try to get sector
        sector = market.get_sector_by_ticker(ticker)
        instrument_type = open_position.instrument_type
        lots = open_position.lots
        average_position_price = open_position.average_position_price.value
        currency = open_position.average_position_price.currency
        balance = open_position.balance
        # blocked
        # expected_yield

        portfolio_current_df = portfolio_current_df.append({"sector": sector,
                                                            "instrument_type": instrument_type,
                                                            "ticker": ticker,
                                                            "balance": balance,
                                                            "lots": lots,
                                                            "average_position_price": average_position_price,
                                                            "currency": currency,

                                                            }, ignore_index=True)

    portfolio_current_df.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=False)
    print("Portfolio updated")
    if is_portfolio_current_exist(account_id):
        return True
    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return False


class Account:
    """
    Class Account contain personal information about Traider:
    Login
    Password
    ID
    """

    def __init__(self, login, account_id):
        self.user_login = login
        self.user_account_id = account_id

    def login(self, login):
        self.user_login = login
        return login

    def account_id(self, account_id):
        self.user_account_id = account_id
        return account_id
