import pandas as pd
from pathlib import Path
import datetime
from random import randint
import json
import sys
import broker
pd.set_option('display.max_columns', None)


def get_user_input_data():
    user_input = input(">>")
    return user_input


def generate_random_id():
    """
    random id generator foo for store same condition at one place
    :return: int()
    """
    random_id = randint(100000, 999999)
    return random_id


def wallet_create_new(account_id):
    """
    This function creates two .csv files:
    first for storing wallet operations history
    and second for current wallet state
    """

    # get input data from user

    print("Only RUB supported now as main currency.")
    main_currency = "RUB"
    broker_commission = 0.3
    if main_currency == "RUB":

        wallet_current_data = {main_currency: 0., "USD": 0., "broker_commission": broker_commission}
        with open("files/wallet_current_" + str(account_id) + ".txt", 'w+') as file:
            file.write(json.dumps(wallet_current_data))

        wallet_history_df = pd.DataFrame(columns=[ "operation_id", "currency", "amount", "operation",
                                                   "instrument",  "date_time",
                                                   ])
        wallet_history_df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)

        # check if files are created
        if is_wallet_history_exist(account_id) and is_wallet_current_exist(account_id):
            return True
        else:
            print("Something goes wrong, check function", sys._getframe().f_code.co_name)
            return False
    elif main_currency == "USD":
        print("Sorry, only RUB supported now.")
        return False
    else:
        print("Sorry, only RUB supported now. You type:", main_currency)
        return False


def wallet_set_broker_commission(data_query):
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
    This function add money to current wallet .csv
    and write operation to wallet_history .csv
    fist operation will add data to wallet_history data
    second operation will calculate data and add to current wallet data

     data_query = [current_user_id, currency, amount, operation_id]

    """
    account_id = data_query[0]
    currency = data_query[1]
    amount = data_query[2]
    operation_id = data_query[3]
    instrument = data_query[4]
    operation = data_query [5]

    current_time = broker.get_current_time()

    # check if this file exist
    if is_wallet_current_exist(account_id) and is_wallet_history_exist(account_id):
        wallet_history_data = wallet_show_history(account_id)
        wallet_current_data = wallet_show_current(account_id)



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
            # write new data to wallet_current
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
            # write new data to wallet_current
            with open("files/wallet_current_" + str(account_id) + ".txt", 'w') as file:
                file.write(json.dumps(wallet_current_data))
    elif not is_wallet_current_exist(account_id) and is_wallet_history_exist(account_id):
        if wallet_create_new(account_id):
            wallet_history_data = wallet_show_history(account_id)
            wallet_current_data = wallet_show_current(account_id)

            currency = str()
            for key in wallet_current_data.keys():
                currency = key
            # can change to foo input user data
            print("Enter amount to add:")
            amount = get_user_input_data()
            operation = "add"
            instrument = "currency"
            # random id generator foo
            operation_id = generate_random_id()

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
        return


def wallet_show_current(account_id):
    """
    This function show current state of wallet, stored in .csv file
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
    This function show history of wallet, stored in .csv file
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
        print("Wallet current does not exist")

        return False


def is_wallet_history_exist(account_id):
    wallet_data = Path("files/wallet_history_" + str(account_id) + ".csv")
    if Path("files").is_dir() and wallet_data.is_file():
        return True
    else:
        print("Wallet history does not exist \n"
              "New wallet history will be created \n"
              )
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
                                                 "order_created_at", "order_done_at",
                                                 ])

    portfolio_current_df.to_csv("files/portfolio_history_" + str(account_id) + ".csv", index=False)

    portfolio_history_df = pd.DataFrame(columns=["operation_id", "order_type", "ticker", "order_price", "amount",
                                                 "currency", "order_price_total", "commission", "instrument",
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
        print("Portfolio does not exist \n"
              "New Portfolio will be created \n"
              )
        return False


def is_portfolio_history_exist(account_id):
    portfolio_data = Path("files/portfolio_history_" + str(account_id) + ".csv")
    if Path("files").is_dir() and portfolio_data.is_file():
        return True
    else:
        print("Portfolio does not exist \n"
              "New Portfolio will be created \n"
              )
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
    print("Add data to portfolio_history\n", data)

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
        #print("portfolio_history \n", portfolio_history)
        # save data to portfolio history csv
        portfolio_history.to_csv("files/portfolio_history_" + str(account_id) + ".csv", index=False)

        portfolio_cur = portfolio_all_data.set_index("operation_id")
        portfolio_cur_dropped = portfolio_cur.drop(operation_id)

        #print("portfolio_cur_dropped\n", portfolio_cur_dropped)
        # save data to portfolio current csv
        portfolio_cur_dropped.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=True)

        return True

    elif portfolio_filtered_data.empty:
        print(" data not found")
        return False

class Account:
    """
    Class Account contain personal information about Traider:
    Login
    Password
    ID
    """

    def __init__(self, login, account_id):
        self.login = login
        self.account_id = account_id
