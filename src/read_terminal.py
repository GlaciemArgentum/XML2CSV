"""
Модуль для чтения из параметров терминала.
"""

from argparse import ArgumentParser        # Стандартная библиотека для работы с терминалом.
from datetime import date, time, datetime  # Стандартная библиотека для работы с датой и временем.

from yaml import safe_load                 # Сторонняя библиотека для работы с YAML-файлами.


with open('src/config.yaml', 'r') as file:
    config = safe_load(file)

    FMT_DATE = config['read']['fmt_date']
    FMT_TIME = config['read']['fmt_time']

DESCRIPTS = {'is_file': f"""Параметр отвечает за режим работы программы. При вызове с параметром '-f' возвращается 
                таблица по каждому файлу. При вызове без параметра '-f' возвращается таблица по дням.""",

             'date': f"Параметр принимает две даты: начало и конец требуемого промежутка времени.",

             'time': f"""Параметр принимает два времени: начало и конец требуемого промежутка дня.
                 Используется только в режиме работы по дням. По умолчанию для будних дней с 
                 {config['std_time']['begin_weekday']} до 
                 {config['std_time']['end_weekday']}, по выходным с 
                 {config['std_time']['begin_weekend']} до 
                 {config['std_time']['end_weekend']}."""
             }


def read() -> (bool, (date, date, time, time, bool)):
    """
    Функция считывает и возвращает параметры, указанные при вызове программы в терминале.
    """

    parser = ArgumentParser()
    parser.add_argument('-f', '--is_file', nargs='?', const=True, default=False, metavar='F', help=DESCRIPTS['is_file'])
    parser.add_argument('-d', '--date', nargs=2, required=True, metavar='YYYY-MM-DD', help=DESCRIPTS['date'])
    parser.add_argument('-t', '--time', nargs=2, metavar='hh:mm', default=[None, None], help=DESCRIPTS['time'])

    args = parser.parse_args()

    try:
        date_begin = datetime.strptime(args.date[0], FMT_DATE)
        date_end = datetime.strptime(args.date[1], FMT_DATE)

        if args.time[0] or args.time[1]:
            is_time_std = False
            time_begin = datetime.strptime(args.time[0], FMT_TIME)
            time_end = datetime.strptime(args.time[1], FMT_TIME)

        else:
            is_time_std = True
            time_begin = datetime(2000, 1, 1, 11, 0, 0)
            time_end = datetime(2000, 1, 1, 21, 0, 0)

    except ValueError:
        raise SystemExit("Ошибка: неверный формат даты/времени.")

    is_file_mode = bool(args.is_file)
    date_begin = date_begin.date()
    date_end = date_end.date()
    time_begin = time_begin.time()
    time_end = time_end.time()

    if date_begin > date_end or time_begin > time_end:
        raise SystemExit("Ошибка: начальный момент времени не должен быть позже конечного.")

    return is_file_mode, date_begin, date_end, time_begin, time_end, is_time_std
