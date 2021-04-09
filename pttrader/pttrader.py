import time
import login
import trader
import broker


def market_manager(user_account_id):
    """
    This is main cycle

    """

    current_user_id = user_account_id
    user_logged_in = True
    print("Type: Help, to see available commands or hit Enter to pass")
    user_input = input(">>")
    if user_input == "":
        print("Passed")
    else:
        print("You type: ", user_input)

    while user_logged_in:  # waiting for user commands and checking orders status

        # there list of available user's commands:
        if user_input == "Help":
            print("List of commands: \n\n"
                  "buy \n"
                  "sell \n"
                  "wallet \n"
                  )
            # wait for user new input:
            print("Waiting for user command")
            user_input = input(">>")
            if user_input == "":
                print("Waiting for user command")
                user_input = input(">>")
            else:
                print("You type: ", user_input)

        elif user_input == "":
            print("Waiting for user command")
            user_input = input(">>")
        # buy command
        elif user_input == "buy":
            broker.create_order_query("Buy")
            print("Try to buy")
            user_input = ""
        # sell command
        elif user_input == "sell":
            broker.create_order_query("Sell")
            print("Try to sell")
            user_input = ""
        # wallet command
        elif user_input == "wallet":
            trader_wallet = trader.Wallet(current_user_id)

            print("Your wallet: ", trader_wallet.show_history())
            user_input = ""
        # check_user_input()
        else:

            print("Waiting for user command, you in else branch")
            user_input = input(">>")
            # check_new_orders()
            time.sleep(1)  # make pause for 5 sec for checking price changes
            # print("Sleep 5 sec")


def main():
    # starting program, waiting for User log in
    account_id = login.wait_logging()
    print("Hello,", account_id)
    # main cycle
    market_manager(account_id)


if __name__ == "__main__":
    main()
