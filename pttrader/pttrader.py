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
    while user_logged_in:  # waiting for user commands and checking orders status

        # there list of available user's commands:
        if user_input == "Help" or user_input == "help":
            print("List of commands: \n\n"
                  "buy \n"
                  "sell \n"
                  "wallet balance \n"
                  "wallet history \n"
                  "wallet add \n"
                  "portfolio history\n"
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
            print("Waiting for user command, elif branch")
            user_input = input(">>")
        # check order status
        elif user_input == "check":
            print("Checking user orders status from orders_query_doc")
            broker.check_new_orders(current_user_id)
            user_input = ""
        # buy command
        elif user_input == "buy":
            print("Try to buy")
            request_query = ["Buy", current_user_id]
            print("Order, in orders query: ", broker.create_order_query(request_query))
            user_input = ""
        # sell command
        elif user_input == "sell":
            print("Try to sell")
            request_query = ["Sell", current_user_id]
            print("Order, in orders query: ", broker.create_order_query(request_query))

            user_input = ""
        # wallet command to show current state of wallet
        elif user_input == "wallet balance":
            print("User ID: ", str(current_user_id))
            wallet_data = trader.wallet_show_current(current_user_id)

            print("balance: ", wallet_data)
            user_input = ""
        # wallet show history
        elif user_input == "wallet history":
            print("User ID: ", str(current_user_id))
            wallet_history_data = trader.wallet_show_history(current_user_id)

            print(wallet_history_data)
            user_input = ""
        # wallet add money
        elif user_input == "wallet add":
            trader.wallet_add_money(current_user_id)

            print(trader.wallet_show_current(current_user_id))
            user_input = ""
        # portfolio show history
        elif user_input == "portfolio history":
            #trader.portfolio_show_history(current_user_id)

            print(trader.portfolio_show_history(current_user_id))
            user_input = ""
        # check_user_input
        else:
            print("Waiting for user command, you in else branch")
            user_input = input(">>")
            # check_new_orders()
            time.sleep(1)  # make pause for 5 sec for checking price changes
            # print("Sleep 5 sec")


def main():
    # starting program, waiting for  User log in and user_id return
    account_id = login.wait_logging()
    print("Hello,", account_id)
    # main cycle
    market_manager(account_id)


if __name__ == "__main__":
    main()
