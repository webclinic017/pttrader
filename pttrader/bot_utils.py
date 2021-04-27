import logging
from logging.handlers import TimedRotatingFileHandler
import os
import reply_markups as rm
import handlers_bot

# start logging to the file of current directory or º it to console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
module_logger = logging.getLogger(__name__)


# # start logging to the file with log rotation at midnight of each day
# formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
# handler = TimedRotatingFileHandler(os.path.dirname(os.path.realpath(__file__)) + '/../pttraderbot.log',
#                                    when='midnight',
#                                    backupCount=10)
# handler.setFormatter(formatter)
# module_logger = logging.getLogger(__name__)
# module_logger.addHandler(handler)
# module_logger.setLevel(logging.INFO)
# end of log section


# the functions for logging handlers
def command_info(update):
    if update:
        us_message = str(update.effective_message.text) if update.effective_message.text else 'None'

        usr_name = update.message.from_user.first_name
        if update.message.from_user.last_name:
            usr_name += ' ' + update.message.from_user.last_name
        if update.message.from_user.username:
            usr_name += ' (@' + update.message.from_user.username + ')'

        us_chat_id = str(update.message.from_user.id) if update.message.from_user.id else 'None'

        module_logger.info("Has received a command \"{}\" from user {}, with id {}".format(us_message, usr_name,
                                                                                           us_chat_id))


def message_info(update):
    if update:
        us_message = str(update.message.text) if update.message.text else 'None'

        usr_name = update.message.from_user.first_name
        if update.message.from_user.last_name:
            usr_name += ' ' + update.message.from_user.last_name
        if update.message.from_user.username:
            usr_name += ' (@' + update.message.from_user.username + ')'

        # old use of this user_name, bcz of an error in logs
        # us_first_name = str(update.message.from_user.first_name) if update.message.from_user.first_name else 'None'

        us_chat_id = str(update.message.from_user.id) if update.message.from_user.id else 'None'

        module_logger.info("Has received a message"
                           " \"{}\" from user {}, with id {}".format(us_message, usr_name, us_chat_id))


# work with a user's message from update
def text_simple(usr_msg_text):
    # always working with an uppercased text
    user_login = usr_msg_text[0]
    user_id = usr_msg_text[1]
    usr_msg_text = usr_msg_text[2].upper()
    print("User message upper:", usr_msg_text)
    menu_text_response = ''
    api_response1 = ''
    api_response2 = ''
    reply_markup_response = ''

    if "⬅ page 1".upper() == usr_msg_text:
        menu_text_response = 'page 1'
        reply_markup_response = rm.reply_markup_p1

    elif "page 2 ➡".upper() == usr_msg_text or '⬅ page 2'.upper() in usr_msg_text:
        menu_text_response = 'page 2'
        reply_markup_response = rm.reply_markup_p2

    elif "page 3 ➡".upper() == usr_msg_text:
        menu_text_response = 'page 3'
        reply_markup_response = rm.reply_markup_p3

    elif "buyew".upper() == usr_msg_text:
        import broker

        request_query = ["Buy", user_id]
        print("Order, in orders query: ", broker.create_order_query(request_query))
        api_response1 = broker.create_order_query(request_query)
        print(api_response1)
        reply_markup_response = rm.reply_markup_p1

    elif "sell".upper() == usr_msg_text:
        pass


    elif "wallet add".upper() == usr_msg_text:
        # get input data from user
        import trader
        currency = "RUB"

        print("Enter amount to add:")
        amount = float(trader.get_user_input_data())
        operation_id = trader.get_random_id()
        instrument = "currency"
        operation = "user add"
        data_query = [user_id, currency, amount, operation_id, instrument, operation]
        trader.wallet_add_money(data_query)

        print(trader.wallet_show_current(user_id))



        reply_markup_response = rm.reply_markup_p1
    """
    elif "EOS".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('EOS')
        api_response2 = parse_api_cryptocomparejson('EOS')
        reply_markup_response = reply_markup_p3

    elif "Ripple".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('XRP')
        api_response2 = parse_api_cryptocomparejson('XRP')
        reply_markup_response = reply_markup_p1

    elif "Litecoin".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('LTC')
        api_response2 = parse_api_cryptocomparejson('LTC')
        reply_markup_response = reply_markup_p2

    elif "Cardano".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('ADA')
        api_response2 = parse_api_cryptocomparejson('ADA')
        reply_markup_response = reply_markup_p1

    elif "IOTA".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('MIOTA')
        api_response2 = parse_api_cryptocomparejson('IOT')
        reply_markup_response = reply_markup_p2

    elif "Dash".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('DASH')
        api_response2 = parse_api_cryptocomparejson('DASH')
        reply_markup_response = reply_markup_p2

    elif "NEM".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('XEM')
        api_response2 = parse_api_cryptocomparejson('XEM')
        reply_markup_response = reply_markup_p2

    elif "Monero".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('XMR')
        api_response2 = parse_api_cryptocomparejson('XMR')
        reply_markup_response = reply_markup_p3

    elif "NEO".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('NEO')
        api_response2 = parse_api_cryptocomparejson('NEO')
        reply_markup_response = reply_markup_p3

    elif "Stellar".upper() == usr_msg_text:
        api_response1 = parse_api_coinmarketcapjson('XLM')
        api_response2 = parse_api_cryptocomparejson('XLM')
        reply_markup_response = reply_markup_p3
    else:
        api_response1 = parse_api_coinmarketcapjson(usr_msg_text)
        api_response2 = parse_api_cryptocomparejson(usr_msg_text)
    """

    return {'apiresponse1': api_response1, 'apiresponse2': api_response2,
            'menutextresponse': menu_text_response, 'replymarkupresponse': reply_markup_response}
