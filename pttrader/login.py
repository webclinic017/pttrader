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
    login = str(input(">>"))
    while wait:
        account_data = Path("files/traders_accounts.txt")
        if account_data.is_file():
            # check if user already exist
            with open('files/traders_accounts.txt') as file:
                data = file.read()  #
            data = json.loads(data)

            for account in data:
                if login == account["login"]:
                    print("Hello, ", account["login"] + "!")
                    # wait = False
                    # if exist return user ID
                    return account["account_id"]
                else:
                    pass
            print(login, "does not exist.")
            print("Create new Login?")
            print("type: Yes or No")
            answer = str(input(">>"))
            if answer == "Yes":

                create_new_account(login)
                print("New login created 2")

                # cycle going again and ends after return ID
            else:
                print(login, ",type your login again or exit:")
                login = str(input(">>"))
                if login == "":
                    print("exit")
                else:
                    print("You type: ", login)
        else:
            print("First time running")
            create_new_account(login)
            print("New login created 1")


def create_new_account(new_login):
    """
    :param: new_login Name
    This function create new login and account_id in traders_accounts.txt and append it to the end
    :return: traders_accounts.txt
    """

    generate_new_id = randint(10000, 99999)  # random id generator
    new_account = trader.Account(login=new_login, account_id=generate_new_id)
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
    else:
        time.sleep(1)
        os.mkdir("files")
        time.sleep(1)

        # add new account to local database

        first_data = [{"login": new_account.login, "account_id": new_account.account_id}]
        with open('files/traders_accounts.txt', 'w+') as file:
            file.write(json.dumps(first_data))
