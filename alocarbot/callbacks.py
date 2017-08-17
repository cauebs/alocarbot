import calendar
from datetime import datetime

import dataset
from telegram import ReplyKeyboardMarkup, KeyboardButton

import .cagr
import .credentials
import .strings


def error_callback(bot, update, error):
    logging.error(error)


def start(bot, update):
    update.message.reply_text(strings.START, parse_mode='Markdown')


def handle_message(bot, update):
    text = update.message.text.strip()
    command = strings.COMMANDS.get(text)

    if command == 'all_classes':
        show_classes(bot, update, period='week')

    elif command == 'today':
        show_classes(bot, update, period='today')

    elif command == 'tomorrow':
        show_classes(bot, update, period='tomorrow')

    elif command == 'help':
        show_help(bot, update)

    elif text.isdigit() and len(text) in (7, 8):
        db = dataset.connect('sqlite:///users.db')
        table = db.get_table('users', primary_id='telegram_id')
        table.upsert({'telegram_id': update.message.from_user.id,
                      'cagr_id': text}, ['telegram_id'])

        keyboard = ReplyKeyboardMarkup([[KeyboardButton(c)]
                                        for c in strings.COMMANDS.keys()])

        update.message.reply_text(strings.UPDATED,
                                  reply_markup=keyboard,
                                  parse_mode='Markdown')


def show_classes(bot, update, period='week'):
    db = dataset.connect('sqlite:///users.db')
    table = db.get_table('users', primary_id='telegram_id')
    user = table.find_one(telegram_id=update.message.from_user.id)

    if not user:
        return update.message.reply_text(strings.NOT_FOUND)

    classes = cagr.fetch_user_classes(user['cagr_id'],
                                      credentials.USERNAME,
                                      credentials.PASSWORD)

    if not classes:
        return update.message.reply_text(strings.NO_CLASSES)

    if period == 'today':
        classes = [c for c in classes
                   if c['weekday'] == datetime.now().isoweekday()]
        if not classes:
            return update.message.reply_text(strings.NOTHING_TODAY)

    elif period == 'tomorrow':
        classes = [c for c in classes
                   if c['weekday'] == datetime.now().isoweekday() + 1]
        if not classes:
            return update.message.reply_text(strings.NOTHING_TOMORROW)

    text = '\n\n'.join(f"*[{c['course']}] {c['course_name']}*\n"
                       f"{calendar.day_name[c['weekday'] - 1]}, "
                       f"{c['time'].strftime('%_Hh%M')} - {c['room']}\n"
                       f"{', '.join(c['professors'])}"
                       for c in classes)

    update.message.reply_text(text, parse_mode='Markdown')


def all_classes(bot, update):
    return show_classes(bot, update, period='week')


def classes_today(bot, update):
    return show_classes(bot, update, period='today')


def classes_tomorrow(bot, update):
    return show_classes(bot, update, period='tomorrow')


def show_help(bot, update):
    update.message.reply_text(strings.HELP, parse_mode='Markdown')
