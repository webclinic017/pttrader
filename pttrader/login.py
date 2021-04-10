import json
from random import randint
import trader
from pathlib import Path
import os
import time


def wait_logging():
    wait = True

    print("Please log in")
    print("Type your Name:")
    login = input(">>")
    print("Type your Account ID:")
    account_id = int(input(">>"))
    while wait:

        account_data = Path("files/traders_accounts.txt")
        if account_data.is_file():

            if checking_traders_accounts_file(login, account_id) is None:

                print(login, "and", account_id, " does not exist.")
                print("Create new Account?")
                print("type: Yes or No or hit Enter to exit:")
                answer = input(">>")
                if answer == "Yes":

                    # print("Login",login,"Id", account_id)
                    new_account_id = create_new_account(login)
                    print("New login", login, "and", new_account_id, "created 2")

                    return checking_traders_accounts_file(login, new_account_id)
                    # cycle going again and ends after return ID
                elif answer == "No":
                    print("Please log in")
                    print("Type your Name:")
                    login = input(">>")
                    print("Type your Account ID:")
                    account_id = int(input(">>"))
                elif answer == "":
                    print("exit")
                    exit(code=1)
            else:
                return checking_traders_accounts_file(login, account_id)

        else:
            print("First time running")
            new_account_id = create_new_account(login)
            print("New login", login, "and", new_account_id, "created 1")
            return checking_traders_accounts_file(login, new_account_id)


def checking_traders_accounts_file(login, account_id):
    # check if user already exist
    with open('files/traders_accounts.txt') as file:
        data = file.read()  #
    data = json.loads(data)

    for account in data:
        if login == account["login"] and account_id == account["account_id"]:

            # if exist return user ID
            return account_id
        else:
            pass
    return


def create_new_account(new_login):
    """
    :param: new_login Name
    This function create new login and account_id in traders_accounts.txt and append it to the end
    :return: traders_accounts.txt
    """

    login = new_login
    account_id = randint(10000, 99999)  # random id generator
    new_account = trader.Account(login=login, account_id=account_id)
    if Path("files").is_dir():

        account_data = Path("files/traders_accounts.txt")
        if account_data.is_file():
            # file exists
            # add new account to local database
            with open('files/traders_accounts.txt', "r") as file:
                data = file.read()
            data = json.loads(data)

            data.append({"login": new_account.login, "account_id": new_account.account_id})
            with open('files/traders_accounts.txt', 'w') as file:
                file.write(json.dumps(data))
                print("Remember your account id: ", new_account.account_id)
            return new_account.account_id

        elif Path("files").is_dir():
            time.sleep(1)

            # add new account to local database

            first_data = [{"login": new_account.login, "account_id": new_account.account_id}]
            with open('files/traders_accounts.txt', 'w+') as file:
                file.write(json.dumps(first_data))
                print("Remember your account id: ", new_account.account_id)
            return new_account.account_id

    else:
        time.sleep(1)
        os.mkdir("files")
        time.sleep(1)

        # add new account to local database

        first_data = [{"login": new_account.login, "account_id": new_account.account_id}]
        with open('files/traders_accounts.txt', 'w+') as file:
            file.write(json.dumps(first_data))
            print("Remember your account id: ", new_account.account_id)
        return new_account.account_id
