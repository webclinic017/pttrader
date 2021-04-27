
import trader
import broker

from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters

from bot_utils import module_logger
from handlers_bot import (filter_text_input, error, start, wallet_add, help_user, buy, check_orders, wallet_current,
                          set_broker_commission, wallet_history, ticker_data)


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
                  "check"
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
            # show last 10 operations
            print(wallet_history_data.tail(10))
            user_input = ""
        # wallet add money
        elif user_input == "wallet add":
            # get input data from user

            currency = "RUB"

            print("Enter amount to add:")
            amount = float(trader.get_user_input_data())
            operation_id = trader.get_random_id()
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


def get_my_token() -> str:
    with open('data_for_telegram.txt', "r") as file:
        token = file.read()
    return token


def main() -> None:
    # https://github.com/lytves/crypto-coins-info-bot-v2/blob/957293e1fca6086d00b0b2715f9ed8304aaff2cd/cryptocoinsinfo/utils.py#L41

    module_logger.info("Start the @pttraderbot bot!")

    # create an object "bot"
    updater = Updater(token=get_my_token(), use_context=True)
    dispatcher = updater.dispatcher

    # bot's error handler
    dispatcher.add_error_handler(error)

    # bot's command handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', help_user)
    dispatcher.add_handler(help_handler)

    get_ticker_data = CommandHandler('ticker', ticker_data)
    dispatcher.add_handler(get_ticker_data)

    check_order_handler = CommandHandler('check', check_orders)
    dispatcher.add_handler(check_order_handler)

    buy_handler = CommandHandler('buy', buy)
    dispatcher.add_handler(buy_handler)

    wallet_show_current = CommandHandler('wcur', wallet_current)
    dispatcher.add_handler(wallet_show_current)

    wallet_show_history = CommandHandler('whist', wallet_history)
    dispatcher.add_handler(wallet_show_history)

    wallet_add_money = CommandHandler('wadd', wallet_add)
    dispatcher.add_handler(wallet_add_money)

    change_broker_commission = CommandHandler('brcom', set_broker_commission)
    dispatcher.add_handler(change_broker_commission)

    # bot's text handlers
    text_update_handler = MessageHandler(Filters.text, filter_text_input)
    dispatcher.add_handler(text_update_handler)

    # *** here put the job for the bot ***
    #
    # add tasks to parse APIs from sites-aggregators to local JSON-files, is used time interval, coz
    # APIs (CMC) have pricing plans with limits
    # job_queue = updater.job_queue
    # job_queue.run_repeating(download_api_coinslists_handler, TIME_INTERVAL, 5, context='coinmarketcap')
    # job_queue.run_repeating(download_api_coinslists_handler, TIME_INTERVAL, 10, context='cryptocompare')

    # Start the Bot start_polling() method
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
