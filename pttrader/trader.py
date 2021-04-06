import pandas as pd

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
     wallet_history_example.csv
    """
    pass


class Portfolio:
    """
    Class Portfolio contain info about Trader's assets
    Variant 1: Portfolio as two  unic .csv tables as database for Trader's account see:
     portfolio_current_state_example.csv Need to think about instrument price calculation if I bought 1 amount
      of A ticker at price 100 and than 1 amount of A ticker at price 200 than price now will be?
     
     portfolio_history_example.csv
    """
    def __init__(self):
        pass

    def show():
        data = pd.read_csv("portfolio_history_example.csv")
        print(data)
