#!/usr/bin/env python

import locale
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from . import config
from . import callbacks


locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
logging.basicConfig(format='[%(asctime)s] %(name)s: %(message)s')


def run():
    updater = Updater(config.TOKEN)
    updater.dispatcher.add_error_handler(callbacks.error_callback)

    for handler in [CommandHandler('start', callbacks.start),
                    CommandHandler('aulas', callbacks.all_classes),
                    CommandHandler('hoje', callbacks.classes_today),
                    CommandHandler('amanha', callbacks.classes_tomorrow),
                    CommandHandler('help', callbacks.show_help),
                    MessageHandler(Filters.text, callbacks.handle_message)]:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run()
