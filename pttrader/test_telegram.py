
import login
import trader
import broker

import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)




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

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(get_my_token())

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("login", login_command))

    # on non command i.e message - echo the message on Telegram
    #dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # bot's text handlers
    text_update_handler = MessageHandler(Filters.text, filter_text_input)
    dispatcher.add_handler(text_update_handler)
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    # # starting program, waiting for  User input and user account_id return
    # print("Please type your login ")
    # input_user_login = input("Login >>")
    # print("Type your Account id: (use only integer numbers)")
    #
    # while True:
    #     try:
    #         input_account_id = int(input("Account id >>"))
    #     except ValueError:
    #         print("you type not integer number. Example: 123456")
    #         continue
    #     else:
    #         break
    # response_from_login_module = login.user_logging(input_user_login, input_account_id)
    #
    # # main cycle
    # market_manager(response_from_login_module)


if __name__ == "__main__":
    main()


