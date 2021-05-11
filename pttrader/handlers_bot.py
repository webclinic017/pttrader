from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.dispatcher import run_async

import bot_utils
import login
import trader
import broker
import market
import json
import urllib
from urllib.request import urlopen


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

    text_response = ('Привет, новый пользователь ' + usr_name + "!" +

                     "\n pttrader используется для автоматизации создания записей о ваших сделках.  "
                     "\n Учет сделок ведется в таблицах, которые пользователь может получить для анализа. "
                     "\n * Для начала работы нужно добавить виртуальных денег на ваш кошелек"
                     "\n * напишите или нажмите на команду /wadd чтобы увидеть пример"
                     "\n * После добавления денег бот вернет сообщение с балансом кошелька:"
                     "\n * Например {RUB: 1000.0, USD: 0.0, broker_commission: 0.3} "
                     "\n * команда /buy используется для содания ордера на покупку, нажмите на нее чтобы увидеть пример"
                     "\n * команда /check для проверки статуса созданного ордера"
                     "\n Напиши или нажми на /help чтобы увидеть все доступные команды ")

    text_response_2 = ('Привет, ' + usr_name + "!" +
                       "\n Напиши или нажми /help чтобы увидеть все доступные команды "
                       "\n * Сначала нужно добавить /wadd виртуальных денег на ваш кошелек /wcur  "
                       "\n * написать команду /ticker название тикера чтобы получить информацию о нём  "
                       "\n * команда /buy используется для содания ордера на покупку"
                       "\n * команда /check для проверки статуса созданного ордера")

    user_login = update.message.from_user.username
    # check if user exist, if not create new user database

    if login.user_logging(user_login, usr_chat_id):
        context.bot.send_message(usr_chat_id, text_response_2)

    # if user use bot first time, we need to create all new user files
    elif not login.user_logging(user_login, usr_chat_id):
        if login.trader_accounts_file_exist():
            login.add_user_to_traders_account_file(user_login, usr_chat_id)
            # create new wallet current file and new wallet history file
            trader.wallet_create_new(usr_chat_id)
            # create new portfolio current and new portfolio history files
            trader.portfolio_create_new(usr_chat_id)
            context.bot.send_message(usr_chat_id, text_response)
        else:
            login.create_traders_accounts_file()
            login.add_user_to_traders_account_file(user_login, usr_chat_id)
            # create new wallet current file and new wallet history file
            trader.wallet_create_new(usr_chat_id)
            # create new portfolio current and new portfolio history files
            trader.portfolio_create_new(usr_chat_id)
            context.bot.send_message(usr_chat_id, text_response)


@run_async
def help_user(update, context):
    usr_chat_id = update.message.chat_id
    text_response = ("Список доступных команд: \n\n"
                     " Нажмите на любую команду чтобы получить подсказку\n"
                     " /buy \n"
                     " /sell \n"
                     " /check (проверка статуса заявок на покупку и продажу)\n"
                     " /ticker (получить информацию о тикере) \n"
                     " /wcur (показывает текущий баланс на кошельке) \n"
                     " /wadd  (добавить денег на кошелек) \n"
                     " /brcom (установить размер брокерской коммиссии (0.3% по умолчанию))\n"
                     " /pcur (to show current portfolio) \n"
                     " /cancel (to cancel order in query)\n"
                     " /start чтобы увидеть начальный текст с примерами"
                     " Если есть вопросы, пишите автору @mikhashev\n"
                     )

    context.bot.send_message(usr_chat_id, text_response)


@run_async
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


@run_async
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
    # TODO add economy sector info

    try:
        ticker = str(context.args[0].upper())

        data_link = 'https://api-invest.tinkoff.ru/trading/stocks/get?ticker=' + ticker
        data = urllib.request.urlopen(data_link)
        data = data.read().decode("utf-8")
        data = json.loads(data)

        data_payload = data["payload"]

        if data_payload['exchangeStatus'] == "Open":

            current_ticker_price = market.get_ticker_price(ticker)

            if not current_ticker_price[0]:

                data_price = data_payload['price']

                current_ticker_price = data_price["value"]
                currency = data_price['currency']
                data_symbol = data_payload["symbol"]
                price_increment = data_symbol['minPriceIncrement']
                lot_size = data_symbol['lotSize']
                exchange_status = "открыта"
                text_response = (
                            "последняя цена: " + str(current_ticker_price) + " " + currency +
                            "\nинкремент цены: " + str(price_increment) +
                            "\nразмер лота: " + str(lot_size) +
                            "\nбиржа " + str(exchange_status))
                context.bot.send_message(usr_chat_id, text_response)

            elif current_ticker_price[0]:
                try:
                    currency = market.get_ticker_currency(ticker)
                    price_increment = market.get_ticker_min_price_increment(ticker)
                    lot_size = market.get_ticker_lot_size(ticker)
                    exchange_status = "открыта"

                    text_response = (
                                "средняя цена последней минуты: " + str(current_ticker_price[1]) + " " + currency +
                                "\nинкремент цены: " + str(price_increment) +
                                "\nразмер лота: " + str(lot_size) +
                                "\nбиржа " + str(exchange_status))
                    context.bot.send_message(usr_chat_id, text_response)
                except Exception as e:
                    print(e)

        elif data_payload['exchangeStatus'] == "Close":

            data_price = data_payload['price']

            current_ticker_price = data_price["value"]
            currency = data_price['currency']
            data_symbol = data_payload["symbol"]
            price_increment = data_symbol['minPriceIncrement']
            lot_size = data_symbol['lotSize']
            exchange_status = "закрыта"
            text_response = ("последняя цена: " + str(current_ticker_price) + " " + currency +
                             "\nинкремент цены: " + str(price_increment) +
                             "\nразмер лота: " + str(lot_size) +
                             "\nбиржа " + str(exchange_status))
            context.bot.send_message(usr_chat_id, text_response)



    except (IndexError, ValueError):

        update.message.reply_text("Применение: /ticker <тикер>"
                                  "\n Пример: /ticker sber")


@run_async
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
    # TODO  Can you create buy order when exchange is closed?
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

        response_data = broker.create_order_query(data_query)
        # respond data is nested list [bool,[list]]

        if response_data[0]:
            text_response = ("Ордер на покупку создан: " + str(response_data[1]))
            context.bot.send_message(usr_chat_id, text_response)

        elif not response_data[0]:
            text_response = response_data[1]
            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text("Применение: /buy <тикер> <цена покупки> <количество лотов> <текстовое описание>"
                                  "\nПример: /buy sber 220.01 10 Думаю что из за ипотечных кредитов через год "
                                  "вырастит до 400 рублей")


@run_async
def sell(update: Update, context: CallbackContext):
    """
    same as for buy
    """
    bot_utils.command_info(update)
    order_type = "Sell"
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id
    # TODO  Can you create buy order when exchange is closed?
    try:
        # use context args[n] n- number, to get user input data
        # /sell ticker order_price amount
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
            text_response = ("Ордер на продажу создан: " + str(response_data[1]))
            context.bot.send_message(usr_chat_id, text_response)

        elif not response_data[0]:
            text_response = response_data[1]
            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text("Использование: /sell <ticker> <price> <operation_id> <order_description>"
                                  "\n Пример: /sell sber 320.01 123456 Причина продажи"
                                  "\n Для продажи валюты:  /sell usdrub <price> <amount> <order_description> ")


@run_async
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


@run_async
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


@run_async
def wallet_add(update: Update, context: CallbackContext):
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    # check if user exist already

    user_login = update.message.from_user.username
    # check if user exist, if not create new user database

    if login.user_logging(user_login, usr_chat_id):
        pass

    # if user use bot first time, we need to create all new user files
    elif not login.user_logging(user_login, usr_chat_id):
        if login.create_traders_accounts_file():
            login.add_user_to_traders_account_file(user_login, usr_chat_id)
            # create new wallet current file and new wallet history file
            trader.wallet_create_new(usr_chat_id)
            # create new portfolio current and new portfolio history files
            trader.portfolio_create_new(usr_chat_id)
            pass

    try:
        # use context args[n] n- number, to get user input data
        amount = int(context.args[0])
        currency = str(context.args[1].upper())

        operation_id = trader.get_random_id()
        instrument = "currency"
        operation = "user add"

        data_query = [user_data.id, currency, amount, operation_id, instrument, operation]

        if trader.wallet_add_money(data_query):

            text_response = (trader.wallet_show_current(user_data.id))
            context.bot.send_message(usr_chat_id, text_response)

        elif not trader.wallet_add_money(data_query):
            text_response = "Что-то пошло не так, пожалуйста повторите операцию"
            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /wadd <количество> <валюта> \n'
                                  'Пример: /wadd 1000 rub')


@run_async
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


@run_async
def show_portfolio_current(update: Update, context: CallbackContext):
    """
    this function show current user portfolio
    """
    bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:
        portfolio_data = (trader.portfolio_show_current(user_data.id))
        if portfolio_data.empty:
            text_response = "В вашем портфолио пока ничего нет."
            context.bot.send_message(usr_chat_id, text_response)

        else:
            portfolio_orders = portfolio_data.to_json(orient="split", index=False).encode('utf8')

            data = json.loads(portfolio_orders)

            data_response = ""
            # parsed = json.dumps(data, indent=2).encode('utf8')
            for order in data['data']:
                data_response += str(order) + "\n\n\n"
            text_response = data_response
            context.bot.send_message(usr_chat_id, text_response)

    except (IndexError, ValueError):
        update.message.reply_text('Something wrong, type to @mikhashev ')


@run_async
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

# commands for tinkoff API ank private key
@run_async
def operations_sync(update: Update, context: CallbackContext):
    """
    /sync
    type command in telegram to syncronize your real trade operations witch current operations database
    :return: text
    """
    # when user sent /sync
    #bot_utils.command_info(update)
    user_data = update.effective_user
    usr_chat_id = update.message.chat_id

    try:
        # get operations data from real user brokers account
        # update data in local database
        # if database not exist, create new

        if user_data.username == "mikhashev":

            # update wallet data from broker account
            trader.update_wallet(usr_chat_id)
            # update portfolio from broker data (update to current date every time)
            trader.update_portfolio(usr_chat_id)
            # update operations history available to current date from broker data
            # if already exist history file, update from last to current date
            response = [trader.save_operations_to_history(usr_chat_id)]
            data = response[0]
            print(data)
            if data[0] :
                all_operations_num = data[1]
                from_date = data[2]
                to_date = data[3]
                text_response = "Обновлено: " + str(all_operations_num) + ", c " + str(from_date) + " по " +\
                                str(to_date)

                context.bot.send_message(usr_chat_id, text_response)
            else:
                all_operations_num = data[1]
                from_date = data[2]
                to_date = data[3]

                text_response = "Обновлено: " + str(all_operations_num) + ", c " + str(from_date) + " по " +\
                                str(to_date)

                context.bot.send_message(usr_chat_id, text_response)

        else:

            text_response = str(user_data.username) + ", у вас нет аккаунта Тинькофф Инвестиции для получения данных " \
                                                      "по операциям "

            context.bot.send_message(usr_chat_id, text_response)

    except Exception as e:
        print(e)
        update.message.reply_text("Использование: /sync")




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
