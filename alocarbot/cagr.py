import datetime

import requests
from bs4 import BeautifulSoup
from robobrowser import RoboBrowser

from .cache import timed_cache


@timed_cache(60)
def fetch_user_classes(user_id, cagr_username, cagr_password):
    browser = RoboBrowser(history=True, parser='html.parser')

    url = 'https://sistemas.ufsc.br/login'
    params = {'service': 'http://forum.cagr.ufsc.br/'}
    browser.open(url, params=params)

    form = browser.get_form('fm1')
    form['username'] = cagr_username
    form['password'] = cagr_password
    browser.submit_form(form)

    url = 'http://forum.cagr.ufsc.br/mostrarPerfil.jsf'
    params = {'usuarioTipo': 'Aluno', 'usuarioId': user_id}
    browser.open(url, params=params)

    courses = browser.find_all('td', class_='coluna2_listar_salas')
    classes = browser.find_all('td', class_='coluna3_listar_salas')
    semesters = browser.find_all('td', class_='coluna4_listar_salas')

    entries = ({'course': a.text, 'class': b.text, 'semester': c.text}
               for a, b, c in zip(courses, classes, semesters)
               if a.text != '-' and b.text != '-')

    entries = fetch_classes_info(entries)

    return sorted(entries, key=lambda x: (x['weekday'], x['time']))


@timed_cache(60)
def fetch_classes_info(entries):
    url = 'https://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/'
    get_response = requests.get(url)

    new_entries = []
    for entry in entries:
        form_data = {
            'AJAXREQUEST': '_viewRoot',
            'formBusca': 'formBusca',
            'javax.faces.ViewState': 'j_id1',
            'formBusca:j_id122': 'formBusca:j_id122',
            'formBusca:selectSemestre': entry['semester'],
            'formBusca:codigoDisciplina': entry['course'],
        }

        post_response = requests.post(url, data=form_data,
                                      cookies=get_response.cookies)
        soup = BeautifulSoup(post_response.text, 'html.parser')

        for row in soup.find_all('tr', class_='rich-table-row'):
            cells = [cell.get_text('\n', strip=True)
                     for cell in row.find_all('td')]
            if cells[4] == entry['class']:
                for time in cells[-2].splitlines():
                    entry = entry.copy()
                    entry['course_name'] = cells[5]
                    entry['professors'] = cells[-1].splitlines()
                    entry.update(parse_time(time))
                    new_entries.append(entry)
                break

    return new_entries


def parse_time(time):
    time, room = time.split(' / ')
    weekday, time = time.split('.')
    time, length = time.split('-')
    time = datetime.time(hour=int(time[:2]),
                         minute=int(time[-2:]))

    return {'weekday': int(weekday) - 1,
            'time': time,
            'length': length,
            'room': room}
