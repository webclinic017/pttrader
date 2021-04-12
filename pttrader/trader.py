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
    wallet_history_df = pd.DataFrame(columns=["currency", "amount", "date_time", "operation", "operation_id"])
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
    wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
    while True:

        print("Enter currency:")
        currency = str(input(">>"))
        if currency == "RUB" or currency == "USD":

            print("Enter amount:")
            amount = float(input(">>"))
            date_time = ts
            operation = "add"
            operation_id = randint(10000, 99999)  # random id generator
            df = wallet_history_data.append({"currency": currency,
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
            print(wallet_current_data)
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

    # ct stores current time
    ct = datetime.datetime.now()
    # ts store timestamp of current time
    ts = ct.timestamp()

    # check if this file exist
    is_wallet_history_exist(account_id)
    wallet_history_data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
    while True:

        print("Enter currency:")
        currency = str(input(">>"))
        if currency == "RUB" or currency == "USD":

            print("Enter amount:")
            amount = float(input(">>"))
            date_time = ts
            operation = "subtract"
            # random id generator
            operation_id = randint(10000, 99999)
            df = wallet_history_data.append({"currency": currency,
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
                wallet_current_data["RUB"] -= amount
            elif currency == "USD":
                wallet_current_data["USD"] -= amount
            print(wallet_current_data)
            with open("files/wallet_" + str(account_id) + ".txt", 'w') as file:
                file.write(json.dumps(wallet_current_data))
            break
        else:
            print("You type something wrong")


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

            wallet_create_new(account_id)  # create new wallet


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


def create_new_portfolio(account_id):
    with open("portfolio_history_" + str(account_id) + ".csv", "w+", newline='') as csv_file:
        fieldnames = ["instrument", "ticker", "amount", "price", "date_time", "operation", "operation_id"]

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
