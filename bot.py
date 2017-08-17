import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import credentials
import callbacks


logging.basicConfig(format='[%(asctime)s] %(name)s: %(message)s')


def error_callback(bot, update, error):
    logging.error(error)


updater = Updater(credentials.TOKEN)
updater.dispatcher.add_error_handler(error_callback)

for handler in [CommandHandler('start', callbacks.start),
                CommandHandler('aulas', callbacks.all_classes),
                CommandHandler('hoje', callbacks.classes_today),
                CommandHandler('amanha', callbacks.classes_tomorrow),
                CommandHandler('help', callbacks.show_help),
                MessageHandler(Filters.text, callbacks.handle_message)]:
    updater.dispatcher.add_handler(handler)

updater.start_polling()
updater.idle()
