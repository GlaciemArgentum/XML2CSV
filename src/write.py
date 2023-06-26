"""
Модуль для записи отчёта в CSV-файл.
"""

from csv import DictWriter                 # Стандартная библиотека для работы с CSV-файлами.
from datetime import date, time, datetime  # Стандартная библиотека для работы с датой и временем.

from yaml import safe_load                 # Сторонняя библиотека для работы с YAML-файлами.


with open('src/config.yaml', 'r') as file:
    config = safe_load(file)

    PATH = config['write']['path']
    FMT_DATE = config['write']['fmt_date']
    FMT_TIME = config['write']['fmt_time']
    CSV_NAME = config['write']['csv_name']
    CSV_DELIM = config['write']['csv_delim']
    CSV_FLDS = config['write']['csv_flds']


def make_csv_name(is_file_mode: bool, date_begin: date, date_end: date,
                  time_begin: time, time_end: time, is_time_std: bool) -> str:
    """
    Функция создаёт имя для CSV-файла в зависимости от режима работы, дат и времён.
    """

    date_begin = datetime.strftime(date_begin, FMT_DATE)
    date_end = datetime.strftime(date_end, FMT_DATE)

    if not (is_file_mode or is_time_std):
        time_begin = time.strftime(time_begin, FMT_TIME)
        time_end = time.strftime(time_end, FMT_TIME)

        csv_name = '{0}_by_days_{1}_{2}_{3}_{4}.csv'.format(CSV_NAME, date_begin, date_end, time_begin, time_end)

    elif not is_file_mode and is_time_std:
        csv_name = '{0}_by_days_{1}_{2}.csv'.format(CSV_NAME, date_begin, date_end)

    else:
        csv_name = '{0}_by_files_{1}_{2}.csv'.format(CSV_NAME, date_begin, date_end)

    return PATH + '/' + csv_name


def make_csv(params: tuple, xml_data: list):
    """
    Функция создаёт CSV-файл на основе входных данных.
    """

    is_file_mode = params[0]
    if is_file_mode:
        mode = 'file'
    else:
        mode = 'date'

    csv_name = make_csv_name(*params)
    with open(csv_name, 'w', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=CSV_FLDS[mode], delimiter=CSV_DELIM)
        writer.writeheader()

        for xml_data_line in xml_data:
            writer.writerow(xml_data_line)
