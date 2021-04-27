from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.dispatcher import run_async

import bot_utils
import login
import trader
import broker
import market


# send a start message, command handler
@run_async
def start(update: Update, context: CallbackContext):
    """
    this start function and command. Used for first time run and after clearing chat by user
    """
    bot_utils.command_info(update)

    usr_name = update.message.from_user.first_name
    if update.message.from_user.last_name:
        usr_name += ' ' + update.message.from_user.last_name
    usr_chat_id = update.message.chat_id

    text_response = ('Hi, new user ' + usr_name + "!" +
                     "\n Type /help to see all available commands "
                     "\n * first add money to your current wallet /wadd "
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
                     "sell \n"
                     " /check \n"
                     " /ticker (to get info about ticker) \n"
                     " /wcur (to show current wallet balance) \n"
                     "whist (to show wallet history) \n"
                     " /wadd  (add money to wallet) \n"
                     " /brcom (to change default 0.3% broker's commission rate"
                     "portfolio current \n"
                     "portfolio history \n"
                     )

    context.bot.send_message(usr_chat_id, text_response)


# TODO need to show  which orders done
def check_orders(update: Update, context: CallbackContext):
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id
    try:
        order_status_response = (broker.check_new_orders(user_data.id))
        print('response data in check orders handler', order_status_response)

        if order_status_response[0]:
            text_response = ("Order done: " + str(order_status_response[1]))

            context.bot.send_message(usr_chat_id, text_response)
        elif not order_status_response[0]:
            text_response =  str(order_status_response[1])

            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /buy <ticker> <price> <amount>"
                                  "\n Example: /buy sber 220.01 10")


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
    user message: /buy <ticker> <price> <amount>
    Example: /buy sber 220.01 10

    function creates order list with parameters:
    [order_type, user_id, ticker, order_price, amount, currency, order_price_total,
                       created_at, operation_id, instrument, order_status, commission, broker_commission]
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
        # make list to create order query
        data_query = [order_type, user_data.id, ticker, order_price, amount]

        response_data = broker.create_order_query(data_query)
        # respond data is nested list [bool,[list]]
        print('response data in buy handler', response_data)
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
        update.message.reply_text("Usage: /buy <ticker> <price> <amount>"
                                  "\n Example: /buy sber 220.01 10")


# TODO sell function
def sell(update: Update, context: CallbackContext):
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
            data_query = [order_type, user_data.id, ticker, order_price, amount]
            response_data = broker.create_order_query(data_query)
        else:
            operation_id = int(context.args[2])
            # make list to create order query
            data_query = [order_type, user_data.id, ticker, order_price, operation_id]
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
        update.message.reply_text("Usage: /sell <ticker> <price> <operation_id>"
                                  "\n Example: /sell sber 320.01 123456")


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

        args_all = context.args

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


# bot's update error handler
@run_async
def error(update, context):
    bot_utils.module_logger.warning('Update caused error "%s"', context.error)

    # TODO send a message for the admin with error from here


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


# a handler for download the lists of coins from API agregators by job_queue of telegram.ext
"""
@run_async
def download_api_coinslists_handler(context):


    job = context.job

    module_logger.info('Start a request to %s API', job.context)

    url = ''

    if job.context == 'coinmarketcap':
        url = COINMARKET_API_URL_COINLIST.format(CMC_API_KEY)
        fileoutputname = FILE_JSON_COINMARKET

    elif job.context == 'cryptocompare':
        url = CRYPTOCOMPARE_API_URL_COINLIST
        fileoutputname = FILE_JSON_CRYPTOCOMPARE

    response = requests.get(url)

    # extract a json from response to a class 'dict' or 'list'
    response_dict_list = response.json()

    if response.status_code == requests.codes.ok:

        # check if one of the APIs response is an error
        if (('status' in response_dict_list and response_dict_list['status']['error_code'] != 0) or
                (('Response' in response_dict_list) and response_dict_list['Response'] is 'Error')):

            error_msg = ''
            if job.context == 'coinmarketcap':
                error_msg = response_dict_list['status']['error_message']

            elif job.context == 'cryptocompare':
                error_msg = response_dict_list['Message']

            module_logger.error('%s error message: %s' % (job.context, error_msg))

        else:
            module_logger.info('Success download the coinslist from %s', job.context)

            with open(fileoutputname, 'w') as outfile:
                json.dump(response_dict_list, outfile)
                module_logger.info('Success save it to %s', fileoutputname)

            # save a json to variable
            if job.context == 'coinmarketcap':
                jsonfiles.update_cmc_json(response_dict_list)

            elif job.context == 'cryptocompare':
                jsonfiles.update_cc_json(response_dict_list)

    else:
        module_logger.error('%s not successfully response', job.context)

"""
