import json
from random import randint


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
                return account["ID"]
            else:
                pass
        print(login, "doe's not exist.")
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
    This function create new login and ID in traders_accounts.txt and append it to the end
    :return: traders_accounts.txt
    """

    with open('traders_accounts.txt') as file:
        data = file.read()
    data = json.loads(data)
    generate_new_id = randint(10000, 99999)  # random id generator
    data.append({"login": new_login, "ID": generate_new_id})
    with open('traders_accounts.txt', 'w') as file:
        file.write(json.dumps(data))