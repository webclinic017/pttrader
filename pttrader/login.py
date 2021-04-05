import json
from random import randint
import trader

def wait_logging():
    wait = True

    print("Please log in")
    print("Type your Name:")
    login = str(input())
    while wait:

        # check if user already exist
        with open('traders_accounts.txt') as file:
            data = file.read()  #
        data = json.loads(data)

        for account in data:
            if login == account["login"]:
                print("Hello, ", account["login"]+"!")
                #wait = False
                # if exist return user ID
                return account["account_id"]
            else:
                pass
        print(login, "does not exist.")
        print("Create new Login?")
        print("type: Yes or No")
        answer = str(input())
        if answer == "Yes":

            create_new_login(login)
            print("New login created")
            # cycle going again and ends after return ID
        else:
            print(login, ",type your login again or exit:")
            login = str(input())


def create_new_login(new_login):
    """
    :param: new_login Name
    This function create new login and account_id in traders_accounts.txt and append it to the end
    :return: traders_accounts.txt
    """
    generate_new_id = randint(10000, 99999)  # random id generator
    new_account = trader.Account(login=new_login,account_id=generate_new_id)
    print(new_account.login)
    with open('traders_accounts.txt') as file:
        data = file.read()
    data = json.loads(data)

    data.append({"login": new_account.login, "account_id": new_account.account_id})
    with open('traders_accounts.txt', 'w') as file:
        file.write(json.dumps(data))