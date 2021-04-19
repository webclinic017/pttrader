"""
This module used for user logging

"""

import json
import trader
from pathlib import Path
import os
import sys


def user_logging(login, account_id):

    while True:

        if trader_accounts_file_exist():
            if get_user_account_id(login, account_id)[0]:
                return account_id

            elif not get_user_account_id(login, account_id)[0]:
                # need to add new user or user made mistake in input data
                print(login, "and", account_id, "not found")
                print("Type new, to create new account or hit Enter to retype")
                user_input = trader.get_user_input_data()
                # user type "new"
                if user_input == "new":
                    print("New login is", login)
                    account_id = add_user_to_traders_account_file(login)
                    print("account id", account_id)
                    return account_id
                elif user_input == "":  # user hit Enter
                    print("retype your login and account id ")
                    login = trader.get_user_input_data()
                    account_id = trader.get_user_input_data()

                else:
                    print("you type:", user_input)

        # this is new login and account id
        elif not trader_accounts_file_exist():

            if create_traders_accounts_file():

                account_id = add_user_to_traders_account_file(login)
                return account_id


def trader_accounts_file_exist():
    account_data = Path("files/traders_accounts.txt")

    if account_data.is_file():

        return True
    else:
        # Traders accounts database doesn't exist

        return False


def create_traders_accounts_file():
    if not Path("files").is_dir():
        os.mkdir("files")

    # add empty data to local database
    empty_data = []
    with open('files/traders_accounts.txt', 'w+') as file:
        file.write(json.dumps(empty_data))
    # self checking
    if trader_accounts_file_exist():
        return True
    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return False


def add_user_to_traders_account_file(login):
    # add new account to local database

    with open('files/traders_accounts.txt', "r") as file:
        data = file.read()
    data = json.loads(data)
    account_id = trader.generate_random_id() # generate random unic id
    data.append({"login": login, "account_id": account_id})
    with open('files/traders_accounts.txt', 'w') as file:
        file.write(json.dumps(data))

    return account_id


def get_user_account_id(login, account_id):

    # check if user already exist
    with open('files/traders_accounts.txt') as file:
        data = file.read()  #
    data = json.loads(data)

    for account in data:
        if login == account["login"] and account_id == account["account_id"]:

            response = [True, account_id]
            return response
        else:
            pass

    response = [False, account_id]
    return response


