"""
This module used for user logging

"""

import json
import trader
from pathlib import Path
import os
import sys



def user_logging(user_login, account_id):
    """

    :return: bool
    """

    if trader_accounts_file_exist():
        if get_user_account_id(user_login, account_id)[0]:
            return True

        else:
            # need to add new user or user made mistake in input data
            print("new user")
            return False
            # if add_user_to_traders_account_file(user_login, account_id):
            #     return True


    # this is new login and account id
    elif not trader_accounts_file_exist():
        print("new user not trader_accounts_file_exist()")
        return False

def check_user_login(user_login, account_id):
    if trader_accounts_file_exist():
        if get_user_account_id(user_login, account_id)[0]:
            return True

    elif not trader_accounts_file_exist():

        return False



def trader_accounts_file_exist() -> bool:
    account_data = Path("files/traders_accounts.txt")

    if account_data.is_file():

        return True
    else:
        # Traders accounts database doesn't exist

        return False


def create_traders_accounts_file():
    if not Path("files").is_dir():
        os.mkdir("files")

    elif not trader_accounts_file_exist():

        # add empty data to local database
        empty_data = []
        with open('files/traders_accounts.txt', 'w+') as file:
            file.write(json.dumps(empty_data))
        return True


    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return False


def add_user_to_traders_account_file(user_login, account_id):
    # add new account to local database

    with open('files/traders_accounts.txt', "r") as file:
        data = file.read()
    data = json.loads(data)
    # get_id from tgm
    data.append({"login": user_login, "account_id": account_id})
    with open('files/traders_accounts.txt', 'w') as file:
        file.write(json.dumps(data))

    return True


def get_user_account_id(user_login, account_id):
    # check if user already exist
    with open('files/traders_accounts.txt') as file:
        data = file.read()  #
    data = json.loads(data)

    for account in data:
        if user_login == account["login"] and account_id == account["account_id"]:

            response = [True, account_id]
            return response
        else:
            pass



    response = [False, account_id]
    return response
