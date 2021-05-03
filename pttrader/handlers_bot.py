from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.dispatcher import run_async

import bot_utils
import login
import trader
import broker
import market
import json


# send a start message, command handler
@run_async
def start(update: Update, context: CallbackContext):
    """
    this start function and command. Used for first time run and after clearing chat by user
    if need you can add custom command /login <user_login> <user_id> for multiple accounts creation
    """
    bot_utils.command_info(update)

    usr_name = update.message.from_user.first_name
    if update.message.from_user.last_name:
        usr_name += ' ' + update.message.from_user.last_name
    usr_chat_id = update.message.chat_id

    text_response = ('Hi, new user ' + usr_name + "!" +
                     "\n Type /help to see all available commands "
                     "\n * first add money /wadd to your current wallet /wcur  "
                     "\n * use /ticker to check data about stock "
                     "\n * use /buy to create buy order"
                     "\n * use /check to check order status")

    text_response_2 = ('Hi, again ' + usr_name + "!" +
                       "\n Type /help to see all available commands "
                       "\n * first add money to your current wallet /wadd "
                       "\n * use /ticker to check data about stock "
                       "\n * use /buy to create buy order"
                       "\n * use /check to check order status")

    user_login = update.message.from_user.username
    # check if user exist, if not create new user database
    if login.user_logging(user_login, usr_chat_id):
        context.bot.send_message(usr_chat_id, text_response_2)

    # if user use bot first time, we need to create all new user files
    elif not login.user_logging(user_login, usr_chat_id):
        if login.create_traders_accounts_file():
            login.add_user_to_traders_account_file(user_login, usr_chat_id)
            # create new wallet current file and new wallet history file
            trader.wallet_create_new(usr_chat_id)
            # create new portfolio current and new portfolio history files
            trader.portfolio_create_new(usr_chat_id)
            context.bot.send_message(usr_chat_id, text_response)


def help_user(update, context):
    usr_chat_id = update.message.chat_id
    text_response = ("List of commands: \n\n"
                     " /buy \n"
                     " /sell \n"
                     " /check (to check order status in query)\n"
                     " /ticker (to get info about ticker) \n"
                     " /wcur (to show current wallet balance) \n"
                     " /wadd  (add money to wallet) \n"
                     " /brcom (to change default 0.3% broker's commission rate)\n"
                     " /pcur (to show current portfolio) \n"
                     " /cancel (to cancel order in query)\n"
                     )

    context.bot.send_message(usr_chat_id, text_response)


def check_orders(update: Update, context: CallbackContext):
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id
    try:
        order_status_response = (broker.check_new_orders(user_data.id))

        # can delete first element in future
        if order_status_response[0]:
            text_response = ("Order done: " + str(order_status_response[1]))

            context.bot.send_message(usr_chat_id, text_response)
        elif not order_status_response[0]:
            text_response = order_status_response[1]

            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /check")


def ticker_data(update: Update, context: CallbackContext):
    """
    return data about ticker:
    Current price: 10.08
    currency: USD
    price increment is: 0.01
    lot size
    """
    bot_utils.command_info(update)
    usr_chat_id = update.message.chat_id

    try:
        ticker = str(context.args[0].upper())

        current_ticker_price = market.get_ticker_price(ticker)
        currency = market.get_ticker_currency(ticker)
        price_increment = market.get_ticker_min_price_increment(ticker)
        lot_size = market.get_ticker_lot_size(ticker)

        text_response = ("current price: " + str(current_ticker_price) + " " + currency +
                         "\n price increment: " + str(price_increment) +
                         "\n lot size: " + str(lot_size))
        context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /ticker <ticker>"
                                  "\n Example: /ticker sber")


def buy(update: Update, context: CallbackContext):
    """
    user message: /buy <ticker> <price> <amount> <order_description>
    Example: /buy sber 220.01 10 reason to buy

    function creates order list with parameters:
    [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission, order_description]
    """
    bot_utils.command_info(update)
    order_type = "Buy"
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id
    # TODO  test add order_description parameter Why do you buy?. /buy <ticker> <price> <amount> <text>
    try:
        # use context args[n] n- number, to get user input data
        # /buy ticker order_price amount
        ticker = str(context.args[0].upper())
        order_price = float(context.args[1])
        amount = int(context.args[2])
        order_description = ""
        for arg in context.args[3:]:
            order_description += arg + " "

        # make list to create order query
        data_query = [order_type, user_data.id, ticker, order_price, amount, order_description]
        print(data_query)
        response_data = broker.create_order_query(data_query)
        # respond data is nested list [bool,[list]]
        print('response data in buy handler', response_data)
        if response_data[0]:
            text_response = ("Order, created " + str(response_data[1]))
            context.bot.send_message(usr_chat_id, text_response)

        elif not response_data[0]:
            text_response = response_data[1]
            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /buy <ticker> <price> <amount> <order_description>"
                                  "\nExample: /buy sber 220.01 10 I buy because of COVID 2019 and"
                                  " think that price will grow up to 300")


def sell(update: Update, context: CallbackContext):
    """
    same as for buy
    """
    bot_utils.command_info(update)
    order_type = "Sell"
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:
        # use context args[n] n- number, to get user input data
        # /buy ticker order_price amount
        ticker = str(context.args[0].upper())
        order_price = float(context.args[1])
        if ticker == "USDRUB":
            amount = float(context.args[2])
            order_description = ""
            for arg in context.args[3:]:
                order_description += arg + " "

            data_query = [order_type, user_data.id, ticker, order_price, amount, order_description]
            print(data_query)
            response_data = broker.create_order_query(data_query)
        else:
            operation_id = int(context.args[2])
            order_description = ""
            for arg in context.args[3:]:
                order_description += arg + " "
            # make list to create order query
            data_query = [order_type, user_data.id, ticker, order_price, operation_id, order_description]
            print(data_query)
            response_data = broker.create_order_query(data_query)
            # respond data is nested list [bool,[list]]
        if response_data[0]:
            text_response = ("Order, created " + str(response_data[1]))
            context.bot.send_message(usr_chat_id, text_response)
        elif not response_data[0] and len(response_data[1]) > 2:
            total_money = response_data[1][6]
            currency = response_data[1][5]
            text_response = ("Order not created, check wallet balance /wcur " +
                             "\n Order total: " + str(total_money) + currency)
            context.bot.send_message(usr_chat_id, text_response)
        elif not response_data[0]:
            text_response = response_data[1]
            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /sell <ticker> <price> <operation_id> <order_description>"
                                  "\n Example: /sell sber 320.01 123456 reason to sell"
                                  "\n For currency /sell usdrub <price> <amount> <order_description> ")


def wallet_current(update: Update, context: CallbackContext):
    """
    this function show current user wallet balance
    """
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:
        text_response = (trader.wallet_show_current(user_data.id))
        context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text('Something wrong with your wallet. check it ')


def wallet_history(update: Update, context: CallbackContext):
    """
    this function show current user wallet history
    """
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:
        text_response = (trader.wallet_show_history(user_data.id))
        context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text('Something wrong with your wallet. check it ')


def wallet_add(update: Update, context: CallbackContext):
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:
        # use context args[n] n- number, to get user input data
        amount = int(context.args[0])
        currency = str(context.args[1].upper())

        operation_id = trader.get_random_id()
        instrument = "currency"
        operation = "user add"

        data_query = [user_data.id, currency, amount, operation_id, instrument, operation]

        trader.wallet_add_money(data_query)

        text_response = (trader.wallet_show_current(user_data.id))
        context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /wadd <amount> <currency> \n'
                                  'Example: /wadd 1000 rub')


def set_broker_commission(update: Update, context: CallbackContext):
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:
        # use context args[n] n- number, to get user input data
        broker_commission = float(context.args[0])
        if broker_commission < 0:
            update.message.reply_text("Sorry, you can't set commission less than 0")
            return

        data_query = [user_data.id, broker_commission]
        if trader.wallet_set_broker_commission(data_query):
            text_response = 'Commission was set to ' + str(broker_commission)
            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /brcom <rate>'
                                  '\n Example: /brcom 0.05')


def show_portfolio_current(update: Update, context: CallbackContext):
    """
    this function show current user portfolio
    """
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:
        portfolio_data = (trader.portfolio_show_current(user_data.id))

        portfolio_orders = portfolio_data.to_json(orient="split", index=False).encode('utf8')

        data = json.loads(portfolio_orders)

        data_response = ""
        #parsed = json.dumps(data, indent=2).encode('utf8')
        for order in data['data']:

            data_response += str(order)+"\n\n\n"
        text_response = data_response
        context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text('Something wrong, type to @mikhashev ')

def cancel_order(update: Update, context: CallbackContext):
    """
    /cancel <operation_id>

    """
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:

        operation_id = int(context.args[0])
        data = [operation_id, usr_chat_id]
        if broker.cancel_order_in_query(data):
            text_response = (str(operation_id) + ", order canceled")
            context.bot.send_message(usr_chat_id, text_response)
        if not broker.cancel_order_in_query(data):
            text_response = (str(operation_id) + ", order not found")
            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /cancel <operation_id>'
                                  '\n Example: /cancel 123456')




# bot's update error handler
@run_async
def error(update, context):
    bot_utils.module_logger.warning('Update caused error "%s"', context.error)

    # TODO send a message for the admin with error from here


# not used now
# text messages handler for send user keyboard for all users
@run_async
def filter_text_input(update, context):
    bot_utils.message_info(update)
    usr_msg_text = update.message.text
    user_data = update.effective_user

    user_response = [user_data.username, user_data.id, usr_msg_text]

    usr_chat_id = update.effective_chat.id

    # string for response
    text_response = ''
    print("usr_msg_text", usr_msg_text)
    # to work with a text request
    dict_to_request = bot_utils.text_simple(user_response)

    # if there is a reply_markup keyboard in a response from function - it's a menu request
    if dict_to_request['menutextresponse']:
        text_response = str(dict_to_request['menutextresponse'])

    # a simple request for a bot (coin name o coin ticket)
    elif dict_to_request['apiresponse1'] or dict_to_request['apiresponse2']:
        text_response = dict_to_request['apiresponse1'] + dict_to_request['apiresponse2']

    """
    if text_response is not empty, bot send a response to user
    """
    if text_response:
        context.bot.send_message(usr_chat_id, text_response,
                                 parse_mode="Markdown", reply_markup=dict_to_request['replymarkupresponse'])
        bot_utils.module_logger.info("Had send a message to a channel %s", usr_chat_id)

    else:
        bot_utils.module_logger.info("Don't send a message for had receive the message %s", usr_msg_text)
