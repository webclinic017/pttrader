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
    # waiting for user commands and checking orders status
    while user_logged_in:

        # there list of available user's commands:
        if user_input == "Help" or user_input == "help":
            print("List of commands: \n\n"
                  "buy \n"
                  "sell \n"
                  "wallet current \n"
                  "wallet history \n"
                  "wallet add \n"
                  "portfolio current \n"
                  "portfolio history\n"
                  )
            # wait for user new input:
            print("Waiting for user command")
            user_input = input(">>")

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
        elif user_input == "wallet current":
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
            # get input data from user

            currency = "RUB"

            print("Enter amount to add:")
            amount = float(trader.get_user_input_data())
            operation_id = trader.generate_random_id()
            instrument = "currency"
            operation = "user add"
            data_query = [current_user_id, currency, amount, operation_id, instrument, operation]
            trader.wallet_add_money(data_query)

            print(trader.wallet_show_current(current_user_id))
            user_input = ""
        # portfolio show history
        elif user_input == "portfolio current":

            print(trader.portfolio_show_current(current_user_id))
            user_input = ""
        # portfolio show history
        elif user_input == "portfolio history":
            # trader.portfolio_show_history(current_user_id)

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
    # starting program, waiting for  User input and user account_id return
    print("Please type your login ")
    input_user_login = str(input("Login >>"))
    print("Type your Account id: (use only integer numbers)")
    input_account_id = int(input("Account id >>"))
    response_from_login_module = login.user_logging(input_user_login, input_account_id)

    # main cycle
    market_manager(response_from_login_module)


if __name__ == "__main__":
    main()

# TODO change save to portfolio_curent and done orders moves tp portfolio_history
