import pandas as pd
import csv

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

    def create_new_wallet(self, account_id):

        with open("wallet_history_"+str(account_id)+".csv", "w+", newline='') as csv_file:
            fieldnames = ["currency", "amount", "date_time", "operation", "operation_id"]

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()


    def create_new_portfolio(self, account_id):

        with open("portfolio_history_"+str(account_id)+".csv", "w+", newline='') as csv_file:
            fieldnames = ["instrument", "ticker", "amount", "price", "date_time", "operation", "operation_id"]

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()



class Wallet:
    """
    Class wallet that keep trader's money.
    Contain currency type: "USD", "EUR", "RUR" etc. and amount
    Variant 1: Wallet as two  unic .csv tables as database for Trader's account see:
     wallet_current_state_example.csv
     wallet_history_example.csv
    """
    def show_history(self, account_id):
        self.data = pd.read_csv("wallet_history_"+str(account_id)+".csv")
        print(self.data)


class Portfolio:
    """
    Class Portfolio contain info about Trader's assets
    Variant 1: Portfolio as two  unic .csv tables as database for Trader's account see:
     portfolio_current_state_example.csv Need to think about instrument price calculation if I bought 1 amount
      of A ticker at price 100 and than 1 amount of A ticker at price 200 than price now will be?
     
     portfolio_history_example.csv
    """
    def show_history(self, account_id):
        self.data = pd.read_csv("portfolio_history_"+str(account_id)+".csv")
        print(self.data)
