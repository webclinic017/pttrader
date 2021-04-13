import pandas as pd
import csv
from pathlib import Path
import datetime
from random import randint
import json


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


class Wallet:
    """
    Class wallet that keep trader's money.
    Contain currency type: "USD", "EUR", "RUR" etc. and amount
    Variant 1: Wallet as two  unic .csv tables as database for Trader's account see:
     wallet_current_state_example.csv
     wallet_history_41447.csv
    """
    pass


def wallet_create_new(account_id):
    """
    This function creates two .csv files:
    first for storing wallet operations history
    and second for current wallet state
    """
    wallet_history_df = pd.DataFrame(columns=["currency", "price", "amount", "date_time", "operation", "operation_id"])
    wallet_history_df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)

    first_data = {"RUB": 0., "USD": 0.}
    with open("files/wallet_" + str(account_id) + ".txt", 'w+') as file:
        file.write(json.dumps(first_data))


def wallet_add_money(account_id):
    """
    This function add money to current wallet .csv
    and write operation to wallet_history .csv
    fist operation will add data to wallet_history data
    second operation will calculate data and add to current wallet data
    """

    # ct stores current time
    ct = datetime.datetime.now()
    # ts store timestamp of current time
    ts = ct.timestamp()
    # check if this file exist
    is_wallet_history_exist(account_id)
    is_portfolio_history_exist(account_id)
    wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")

    while True:

        print("Enter currency:")
        currency = str(input(">>"))
        if currency == "RUB" or currency == "USD":

            print("Enter amount:")
            amount = float(input(">>"))
            price = 0.
            if currency == "RUB":

                price += amount
            elif currency == "USD":
                print("Please enter price in rubles when you bought a USD early:")
                price = float(input(">>"))
            date_time = ts
            operation = "add"
            operation_id = randint(10000, 99999)  # random id generator
            df = wallet_history_data.append({"currency": currency,
                                             "price": price,
                                             "amount": amount,
                                             "date_time": date_time,
                                             "operation": operation,
                                             "operation_id": operation_id},
                                            ignore_index=True)

            df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
            # second operation will calculate and write new data to current state of wallet
            with open("files/wallet_" + str(account_id) + ".txt", "r") as file:
                data = file.read()
            wallet_current_data = json.loads(data)

            if currency == "RUB":
                wallet_current_data["RUB"] += amount
            elif currency == "USD":
                wallet_current_data["USD"] += amount

            with open("files/wallet_" + str(account_id) + ".txt", 'w') as file:
                file.write(json.dumps(wallet_current_data))
            break
        else:
            print("You type something wrong")


def wallet_subtract_money(account_id):
    """
    This function subtract money from current wallet .csv
    and write operation to wallet_history .csv
    fist operation will add data to wallet_history data
    second operation will calculate data and add data to current wallet
    """

    pass


def wallet_show_current(account_id):
    """
    This function show current state of wallet, stored in .csv file
    """
    if Path("files").is_dir():

        current_wallet_data = Path("files/wallet_" + str(account_id) + ".txt")
        if current_wallet_data.is_file():
            # if file exists, return data
            with open("files/wallet_" + str(account_id) + ".txt", "r") as file:
                data = file.read()
            data = json.loads(data)
            return data

        # print(self.data)
        else:
            print("Wallet does not exist \n"
                  "New wallet will be created \n"
                  )
            wallet_create_new(account_id)
            portfolio_create_new(account_id)


def wallet_show_history(account_id):
    """
    This function show history of wallet, stored in .csv file
    """
    if Path("files").is_dir():

        wallet_data = Path("files/wallet_history_" + str(account_id) + ".csv")
        if wallet_data.is_file():
            # if file exists, return data
            data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
            return data

        # print(self.data)
        else:
            print("Wallet does not exist \n"
                  "To create new wallet \n"
                  "Type 'wallet' again"
                  )
            wallet_create_new(account_id)
            portfolio_create_new(account_id)


def is_wallet_history_exist(account_id):
    if Path("files").is_dir():

        wallet_data = Path("files/wallet_history_" + str(account_id) + ".csv")
        if wallet_data.is_file():
            pass

        # print(self.data)
        else:
            print("Wallet does not exist \n"
                  "New wallet will be created \n"
                  )

            wallet_create_new(account_id)  # create new empty wallet
            portfolio_create_new(account_id)  # create new empty portfolio


class Portfolio:
    """
    Class Portfolio contain info about Trader's assets
    Variant 1: Portfolio as two  unic .csv tables as database for Trader's account see:
     portfolio_current_state_example.csv Need to think about instrument price calculation if I bought 1 amount
      of A ticker at price 100 and than 1 amount of A ticker at price 200 than price now will be?
     
     portfolio_history_example.csv
    """

    def show_history(self, account_id):
        self.data = pd.read_csv("portfolio_history_" + str(account_id) + ".csv")
        print(self.data)


def portfolio_create_new(account_id):
    """
    This function creates two .csv files:
    first for storing portfolio operations history
    and second for current portfolio state
    """

    portfolio_history_df = pd.DataFrame(columns=["order_type", "ticker", "order_price", "amount", "currency",
                                                 "order_price_total", "order_created_at", "operation_id", "instrument",
                                                 "order_done_at"])
    portfolio_history_df.to_csv("files/portfolio_history_" + str(account_id) + ".csv", index=False)

    portfolio_current_df = pd.DataFrame(columns=["instrument", "ticker", "order_price", "amount", "currency",
                                                 "order_price_total", "order_created_at", "order_id"])
    portfolio_current_df.to_csv("files/portfolio_current_" + str(account_id) + ".csv", index=False)


def is_portfolio_history_exist(account_id):
    if Path("files").is_dir():

        portfolio_data = Path("files/portfolio_history_" + str(account_id) + ".csv")
        if portfolio_data.is_file():
            pass

        # print(self.data)
        else:
            print("Portfolio does not exist \n"
                  "New Portfolio will be created \n"
                  )

            portfolio_create_new(account_id)  # create new empty portfolio


def portfolio_history_add(data):
    """
    {'order_type': 'Buy', 'user_id': 39460, 'ticker': 'NMTP', 'order_price': 7.8, 'amount': 10, 'currency': 'RUB',
     'order_price_total': 7800.0, 'created_at': 1618331390.686862, 'operation_id': 73483, 'instrument': 'stocks',
     'order_status': False, 'order_done_at': 1618246800.0}
    """

    account_id = data["user_id"]
    is_portfolio_history_exist(account_id)
    portfolio_history_data = pd.read_csv("files/portfolio_history_" + str(account_id) + ".csv")
    df = portfolio_history_data.append({"order_type": data["order_type"],
                                        "ticker": data["ticker"],
                                        "order_price": data["order_price"],
                                        "amount": data["amount"],
                                        "currency": data["currency"],
                                        "order_price_total": data["order_price_total"],
                                        "order_created_at": data["created_at"],
                                        "operation_id": data["operation_id"],
                                        "instrument": data["instrument"],
                                        "order_done_at": data["order_done_at"],
                                        },
                                       ignore_index=True)

    df.to_csv("files/portfolio_history_" + str(account_id) + ".csv", index=False)

