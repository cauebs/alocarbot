import calendar
import logging
from datetime import datetime

from cagrex import CAGR
import dataset
from telegram import ReplyKeyboardMarkup, KeyboardButton

from .cache import timed_cache
from . import config
from . import strings


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
        db = dataset.connect(f'sqlite:///{config.DB_PATH}')
        table = db.get_table('users', primary_id='telegram_id')
        table.upsert({'telegram_id': update.message.from_user.id,
                      'cagr_id': text}, ['telegram_id'])

        keyboard = ReplyKeyboardMarkup([[KeyboardButton(c)]
                                        for c in strings.COMMANDS.keys()])

        update.message.reply_text(strings.UPDATED,
                                  reply_markup=keyboard,
                                  parse_mode='Markdown')


@timed_cache(60)
def fetch_student(telegram_id):
    db = dataset.connect(f'sqlite:///{config.DB_PATH}')
    table = db.get_table('users', primary_id='telegram_id')
    user = table.find_one(telegram_id=telegram_id)

    if not user:
        raise KeyError('User not found in database')

    cagr = CAGR()
    cagr.login(config.USERNAME, config.PASSWORD)
    return cagr.student(user['cagr_id'])


@timed_cache(30)
def fetch_student_classes(student):
    course_class = {c['id']: c['turma']
                    for c in student['disciplinas']}

    cagr = CAGR()

    semesters = cagr.semesters()
    if student['curso'].lower() == 'engenharia de materiais':
        semester = semesters[0]
    else:
        semester, *_ = (s for s in semesters if not s.endswith('3'))

    all_classes = []
    courses = list(cagr.courses(course_class.keys(), semester))
    for c in courses:
        classes = c.pop('turmas')
        class_id = course_class[c['id']]
        c.update(classes[class_id])
        times = c.pop('horarios')
        for time in times:
            all_classes.append({**c.copy(), **time})

    return sorted(all_classes, key=lambda c: (c['dia_da_semana'], c['horario']))


def show_classes(bot, update, period='week'):
    try:
        student = fetch_student(update.message.from_user.id)
    except KeyError:
        return update.message.reply_text(strings.NOT_FOUND)

    classes = fetch_student_classes(student)

    if not classes:
        return update.message.reply_text(strings.NO_CLASSES)

    today_weekday = datetime.now().isoweekday()

    if period == 'today':
        classes = [
            c for c in classes
            if c['dia_da_semana'] == today_weekday
        ]
        if not classes:
            return update.message.reply_text(strings.NOTHING_TODAY)

    elif period == 'tomorrow':
        classes = [
            c for c in classes
            if c['dia_da_semana'] == (today_weekday + 1) % 7
        ]
        if not classes:
            return update.message.reply_text(strings.NOTHING_TOMORROW)

    text = '\n\n'.join(
        f"*[{c['id']}] {c['nome']}*\n"
        f"{calendar.day_name[c['dia_da_semana'] - 1].title()}, "
        f"{c['horario'][:-2]}h{c['horario'][-2:]} ({c['sala']})\n"
        f"{', '.join(c['professores'])}"
        for c in classes
    )

    update.message.reply_text(text, parse_mode='Markdown')


def all_classes(bot, update):
    return show_classes(bot, update, period='week')


def classes_today(bot, update):
    return show_classes(bot, update, period='today')


def classes_tomorrow(bot, update):
    return show_classes(bot, update, period='tomorrow')


def show_help(bot, update):
    update.message.reply_text(strings.HELP, parse_mode='Markdown')
