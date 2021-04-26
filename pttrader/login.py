"""
This module used for user logging

"""

import json
import trader
from pathlib import Path
import os
import sys

# TODO delete all useless print functions

def user_logging(user_login, account_id):
    """

    :return: int account_id
    """

    while True:

        if trader_accounts_file_exist():
            if get_user_account_id(user_login, account_id)[0]:
                return True

            elif not get_user_account_id(user_login, account_id)[0]:
                # need to add new user or user made mistake in input data
                print(user_login, "and", account_id, "not found")
                if add_user_to_traders_account_file(user_login, account_id):

                    return True


        # this is new login and account id
        elif not trader_accounts_file_exist():

            if create_traders_accounts_file():

                account_id = add_user_to_traders_account_file(user_login,account_id)
                print("New account created!"
                      "\nRemember your Login:", user_login,
                      "\nAccount id:", account_id
                      )
                return True


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


