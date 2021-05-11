import logging
from logging.handlers import TimedRotatingFileHandler
import os



# # start logging to the file of current directory or º it to console
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# module_logger = logging.getLogger(__name__)


# # start logging to the file with log rotation at midnight of each day
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = TimedRotatingFileHandler(os.path.dirname(os.path.realpath(__file__)) + '/pttraderbot.log',
                                   when='midnight',
                                   backupCount=10)
handler.setFormatter(formatter)
module_logger = logging.getLogger(__name__)
module_logger.addHandler(handler)
module_logger.setLevel(logging.INFO)
# # end of log section


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


# work with a user's message from update. Now work only with commands
def text_simple(usr_msg_text):
    # always working with an uppercased text
    usr_msg_text = usr_msg_text[2].upper()
    print("User message upper:", usr_msg_text)
    menu_text_response = ''
    api_response1 = ''
    api_response2 = ''
    reply_markup_response = ''

    if "⬅ page 1".upper() == usr_msg_text:
        menu_text_response = 'page 1'


    elif "buyew".upper() == usr_msg_text:
        pass


    elif "sell".upper() == usr_msg_text:
        pass


    elif "wallet add".upper() == usr_msg_text:
        pass

    return {'apiresponse1': api_response1, 'apiresponse2': api_response2,
            'menutextresponse': menu_text_response, 'replymarkupresponse': reply_markup_response}
