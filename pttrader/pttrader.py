
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters

from bot_utils import module_logger
from handlers_bot import (filter_text_input,
                          error,
                          start,
                          wallet_add,
                          help_user,
                          buy,
                          sell,
                          check_orders,
                          wallet_current,
                          set_broker_commission,
                          wallet_history,
                          ticker_data,
                          show_portfolio_current,
                          cancel_order

                          )


def get_my_token() -> str:

    with open('data_for_telegram.txt', "r") as file:
        token = file.read()
    return token


def main() -> None:

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

    sell_handler = CommandHandler('sell', sell)
    dispatcher.add_handler(sell_handler)

    wallet_show_current = CommandHandler('wcur', wallet_current)
    dispatcher.add_handler(wallet_show_current)

    wallet_show_history = CommandHandler('whist', wallet_history)
    dispatcher.add_handler(wallet_show_history)

    wallet_add_money = CommandHandler('wadd', wallet_add)
    dispatcher.add_handler(wallet_add_money)

    change_broker_commission = CommandHandler('brcom', set_broker_commission)
    dispatcher.add_handler(change_broker_commission)

    portfolio_current = CommandHandler('pcur', show_portfolio_current)
    dispatcher.add_handler(portfolio_current)

    cancel_order_in_query = CommandHandler('cancel', cancel_order)
    dispatcher.add_handler(cancel_order_in_query)

    # bot's text handlers
    text_update_handler = MessageHandler(Filters.text, filter_text_input)
    dispatcher.add_handler(text_update_handler)

    # Start the Bot start_polling() method
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
