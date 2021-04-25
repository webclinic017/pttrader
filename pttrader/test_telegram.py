
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
            #show last 10 operations
            print(wallet_history_data.tail(10))
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
        # wallet add money
        elif user_input == "broker commission":
            # get input data from user

            print("Enter commission rate to add:")
            broker_commission = float(trader.get_user_input_data())

            data_query = [current_user_id, broker_commission]
            if trader.wallet_set_broker_commission(data_query):
                print(trader.wallet_show_current(current_user_id))
                user_input = ""
        # portfolio show history
        elif user_input == "portfolio current":

            print(trader.portfolio_show_current(current_user_id))
            user_input = ""
        # portfolio show history
        elif user_input == "portfolio history":
            # trader.portfolio_show_history(current_user_id)
            # show last 10 operations
            print((trader.portfolio_show_history(current_user_id)).tail(10))
            user_input = ""
        # check_user_input
        else:
            print("Waiting for user command, you in else branch")
            user_input = input(">>")

def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hi! Please type your login')


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def login_command(update: Update, _: CallbackContext) -> None:

    login = MessageHandler()

    print(login)


def get_my_token() -> str:

    with open('data_for_telegram.txt', "r") as file:
        token = file.read()
    return token

def main() -> None:
    # https://github.com/lytves/crypto-coins-info-bot-v2/blob/957293e1fca6086d00b0b2715f9ed8304aaff2cd/cryptocoinsinfo/utils.py#L41

    from telegram.ext import Updater
    from telegram.ext import CommandHandler, MessageHandler, Filters

    from bot_utils import module_logger
    from handlers_bot import filter_text_input, error, start, download_api_coinslists_handler

    module_logger.info("Start the @pttraderbot bot!")

    # create an object "bot"
    updater = Updater(token=get_my_token(), use_context=True)
    dispatcher = updater.dispatcher

    # bot's error handler
    dispatcher.add_error_handler(error)

    # bot's command handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # bot's text handlers
    text_update_handler = MessageHandler(Filters.text, filter_text_input)
    dispatcher.add_handler(text_update_handler)


    # bot's text handlers
    text_update_handler = MessageHandler(Filters.text, filter_text_input)
    dispatcher.add_handler(text_update_handler)


def user_logging(text_message):
    # starting program, waiting for  User input and user account_id return

    user_login = text_message
    print("Please type your login ")
    input_user_login = input("Login >>")
    print("Type your Account id: (use only integer numbers)")

    while True:
        try:
            input_account_id = int(input("Account id >>"))
        except ValueError:
            print("you type not integer number. Example: 123456")
            continue
        else:
            break
    response_from_login_module = login.user_logging(input_user_login, input_account_id)

    # main cycle
    market_manager(response_from_login_module)


if __name__ == "__main__":
    main()


