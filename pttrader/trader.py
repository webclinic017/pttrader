import pandas as pd
import csv
from pathlib import Path
import datetime


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


def create_new_portfolio(account_id):
    with open("portfolio_history_" + str(account_id) + ".csv", "w+", newline='') as csv_file:
        fieldnames = ["instrument", "ticker", "amount", "price", "date_time", "operation", "operation_id"]

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()


def create_new_wallet(account_id):
    df = pd.DataFrame(columns=["currency", "amount", "date_time", "operation", "operation_id"])
    df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
    # with open("files/wallet_history_" + str(account_id) + ".csv", "w+", newline='') as csv_file:
    #     fieldnames = ["currency", "amount", "date_time", "operation", "operation_id"]
    #
    #     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    #     writer.writeheader()


def wallet_add_money(account_id):
    """
    This function add money to current wallet
    """

    # ct stores current time
    ct = datetime.datetime.now()
    print("current time:-", ct)

    # ts store timestamp of current time
    ts = ct.timestamp()
    print("timestamp:-", ts)

    # df = pd.DataFrame(columns=["currency", "amount", "date_time", "operation", "operation_id"])
    is_wallet_exist(account_id)
    data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
    while True:

        print("Enter currency:")
        currency = str(input(">>"))
        if currency == "RUR" or currency == "USD":

            print("Enter amount:")
            amount = input(">>")
            date_time = ts
            operation = "add"
            operation_id = 10
            # add_data = list({currency, amount, date_time, operation, operation_id})
            # df.append(add_data)
            df = data.append({"currency": currency,
                              "amount": amount,
                              "date_time": date_time,
                              "operation": operation,
                              "operation_id": operation_id},
                             ignore_index=True)

            df.to_csv("files/wallet_history_" + str(account_id) + ".csv", index=False)
            break
        else:
            print("You type something wrong")


def wallet_show_history(account_id):
    if Path("files").is_dir():

        wallet_data = Path("files/wallet_history_" + str(account_id) + ".csv")
        if wallet_data.is_file():
            # file exists
            # add new account to local database

            data = pd.read_csv("files/wallet_history_" + str(account_id) + ".csv")
            return data

        # print(self.data)
        else:
            print("Wallet does not exist \n"
                  "To create new wallet \n"
                  "Type 'wallet' again"
                  )
            create_new_wallet(account_id)


class Wallet:
    """
    Class wallet that keep trader's money.
    Contain currency type: "USD", "EUR", "RUR" etc. and amount
    Variant 1: Wallet as two  unic .csv tables as database for Trader's account see:
     wallet_current_state_example.csv
     wallet_history_41447.csv
    """
    pass


def is_wallet_exist(account_id):
    if Path("files").is_dir():

        wallet_data = Path("files/wallet_history_" + str(account_id) + ".csv")
        if wallet_data.is_file():
            pass

        # print(self.data)
        else:
            print("Wallet does not exist \n"
                  "To create new wallet \n"
                  "Type 'wallet' again"
                  )
            create_new_wallet(account_id)


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
