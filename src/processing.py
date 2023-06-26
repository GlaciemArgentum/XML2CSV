"""
Модуль для сбора и обработки информации с FTP-сервера.
"""

from datetime import date, time, datetime, timedelta   # Стандартная библиотека для работы с датой и временем.
from ftplib import FTP                                 # Стандартная библиотека для работы с FTP.
from re import match                                   # Стандартная библиотека для работы с регулярными выражениями.
from xml.etree.ElementTree import Element, fromstring  # Стандартная библиотека для работы с XML-файлами.

from alive_progress import alive_bar  # Сторонняя библиотека для создания красивой полоски прогресса.
from yaml import safe_load            # Сторонняя библиотека для работы с YAML-файлами.


with open('src/config.yaml', 'r') as file:
    config = safe_load(file)

    CSV_FLDS = config['write']['csv_flds']
    FMT_DATE = config['write']['fmt_date']
    FMT_TIME = config['write']['fmt_time']
    STD_TIME = {'begin_weekday': datetime.strptime(config['std_time']['begin_weekday'], '%H:%M').time(),
                'end_weekday':   datetime.strptime(config['std_time']['end_weekday'], '%H:%M').time(),
                'begin_weekend': datetime.strptime(config['std_time']['begin_weekend'], '%H:%M').time(),
                'end_weekend':   datetime.strptime(config['std_time']['end_weekend'], '%H:%M').time()}

# Глобальная переменная. Используется в качестве буфера для данных из XML-файла.
xml_buf = ''


def is_valid_name(name: str, is_file=True) -> bool:
    """
    Функция проверяет на правильность формат имени файла или директории.
    """

    if is_file:
        is_match = match(r'^count-data_countdata_([0-9A-F]{2}-){5}([0-9A-F]{2})_\d{4}(-([0-9]{2})){5}\.xml$', name)
        if is_match:
            return True

    else:
        is_match = match(r'^\d+floor$', name)
        if is_match:
            return True

    return False


def is_name_in_date(file_name: str, date_begin: date, date_end: date) -> bool:
    """
    Функция проверяет по имени файла, входит ли дата его создания в требуемый временной промежуток.
    """

    file_name = file_name[file_name.rfind('_')+1:-4]
    chrn = datetime.strptime(file_name, '%Y-%m-%d-%H-%M-%S')
    chrn -= timedelta(hours=1)

    if date_begin <= chrn.date() <= date_end:
        return True

    return False


def count_files(ftp: FTP, date_begin: date, date_end: date) -> int:
    """
    Функция считает количество файлов на FTP-сервере (с учётом формата имени и даты в имени директорий и файлов).
    """

    counter = 0

    dir_list = ftp.nlst()
    for my_dir in dir_list:
        if not is_valid_name(my_dir, False):
            continue

        ftp.cwd(my_dir)
        file_list = ftp.nlst()
        for my_file in file_list:
            if not (is_valid_name(my_file) and is_name_in_date(my_file, date_begin, date_end)):
                continue

            counter += 1

        ftp.cwd('..')

    return counter


def collect_lines(s: str):
    """
    Функция принимает строку и добавляет её в глобальную буферную переменную xml_buf.
    """

    global xml_buf
    xml_buf += s + '\n'


def get_root(ftp: FTP, file_name: str) -> Element:
    """
    Функция запрашивает на сервере XML-файл и возвращает Element-объект c данными из XML-файла.
    """

    global xml_buf
    ftp.retrlines('RETR ' + file_name, collect_lines)
    root = fromstring(xml_buf)
    xml_buf = ''
    return root


def get_xml(root: Element) -> (str, date, date, time, time, int, str, int, int):
    """
    Функция принимает на вход Element-объект с данными из XML-файла и возвращает эти данные.
    """

    ns = {'ns2': 'http://www.xovis.com/count-data-sequence', 'ns1': 'http://www.xovis.com/sensor-status',
          'ns4': 'http://www.xovis.com/common-types', 'ns3': 'http://www.xovis.com/count-line-sequence'}

    name = root.find('ns2:sensor', ns).find('ns1:name', ns).text
    begin = root.find('ns2:date-from', ns).text
    end = root.find('ns2:date-to', ns).text
    granularity = root.find('ns2:granularity', ns).attrib['seconds']
    line_name = root.find('ns2:count-lines', ns).find('ns2:count-line', ns).attrib['line-name']
    fw_count = (root.find('ns2:count-lines', ns).find('ns2:count-line', ns).find('ns2:count-values', ns)
                .find('ns3:value', ns).find('ns3:fw-count', ns).text)
    bw_count = (root.find('ns2:count-lines', ns).find('ns2:count-line', ns).find('ns2:count-values', ns)
                .find('ns3:value', ns).find('ns3:bw-count', ns).text)

    name = str(name)
    begin = datetime.strptime(begin, '%Y-%m-%dT%H:%M:%S%z')
    end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')
    granularity = int(granularity)
    line_name = str(line_name)
    fw_count = int(fw_count)
    bw_count = int(bw_count)

    return name, begin.date(), end.date(), begin.time(), end.time(), granularity, line_name, fw_count, bw_count


def is_date_weekend(my_date: date) -> bool:
    """
    Функция проверяет, является ли дата выходным днём недели.
    """

    if my_date.weekday() >= 5:
        return True

    return False


def is_in_time(my_date: date, time_begin: time, time_end: time, req_time_begin: time, req_time_end: time,
               is_time_std: bool) -> bool:
    """
    Функция проверяет, входит ли указанный временной промежуток в требуемый
    (с учётом выходных, если время не задано).
    """

    if is_time_std:
        if is_date_weekend(my_date):
            req_time_begin = STD_TIME['begin_weekend']
            req_time_end = STD_TIME['end_weekend']
        else:
            req_time_begin = STD_TIME['begin_weekday']
            req_time_end = STD_TIME['end_weekday']

    if req_time_begin <= time_begin and time_end <= req_time_end:
        return True

    return False


def get_time(my_date: date, time_begin: time, time_end: time, is_time_std: bool) -> (str, str):
    """
    Функция возвращает время в виде строки (с учётом выходных, если время не задано).
    """

    if is_time_std:
        if is_date_weekend(my_date):
            time_begin = STD_TIME['begin_weekend']
            time_end = STD_TIME['end_weekend']
        else:
            time_begin = STD_TIME['begin_weekday']
            time_end = STD_TIME['end_weekday']

    time_begin = time.strftime(time_begin, FMT_TIME)
    time_end = time.strftime(time_end, FMT_TIME)

    return time_begin, time_end


def dict_to_list(my_dict: dict) -> list:
    """
    Функция принимает на вход словарь и возвращает массив (без учёта ключа).
    """

    result = []
    for key in my_dict:
        result.append(my_dict[key])

    return result


def get_data(ftp: FTP, is_file_mode: bool, req_date_begin: date, req_date_end: date,
             req_time_begin: time, req_time_end: time, is_time_std: bool) -> list:
    """
    Функция собирает и обрабатывает данные с сервера.
    """

    if is_file_mode:
        xml_data: list = []
    else:
        xml_data: dict = {}

    dir_list = ftp.nlst()
    dir_list.sort()
    with alive_bar(count_files(ftp, req_date_begin, req_date_end), calibrate=25) as bar:
        for my_dir in dir_list:
            if not is_valid_name(my_dir, False):
                continue

            ftp.cwd(my_dir)
            file_list = ftp.nlst()
            file_list.sort()
            for my_file in file_list:
                if not (is_valid_name(my_file) and
                        is_name_in_date(my_file, req_date_begin, req_date_end)):
                    continue

                bar()

                root = get_root(ftp, my_file)
                name, date_begin, date_end, time_begin, time_end, granularity, line_name, fw_count, bw_count \
                    = get_xml(root)

                if date_begin < req_date_begin or req_date_end < date_end:
                    continue

                if is_file_mode:
                    xml_data.append({CSV_FLDS['file'][0]: name,
                                     CSV_FLDS['file'][1]: date_begin,
                                     CSV_FLDS['file'][2]: time_begin,
                                     CSV_FLDS['file'][3]: date_end,
                                     CSV_FLDS['file'][4]: time_end,
                                     CSV_FLDS['file'][5]: granularity,
                                     CSV_FLDS['file'][6]: line_name,
                                     CSV_FLDS['file'][7]: fw_count,
                                     CSV_FLDS['file'][8]: bw_count})
                else:
                    if date_begin != date_end or \
                            not is_in_time(date_begin, time_begin, time_end, req_time_begin, req_time_end, is_time_std):
                        continue

                    try:
                        xml_data[date_begin][CSV_FLDS['date'][3]] += fw_count
                        xml_data[date_begin][CSV_FLDS['date'][4]] += bw_count

                    except KeyError:
                        time_begin, time_end = get_time(date_begin, time_begin, time_end, is_time_std)

                        xml_data[date_begin] = {CSV_FLDS['date'][0]: date.strftime(date_begin, FMT_DATE),
                                                CSV_FLDS['date'][1]: time_begin,
                                                CSV_FLDS['date'][2]: time_end,
                                                CSV_FLDS['date'][3]: fw_count,
                                                CSV_FLDS['date'][4]: bw_count}

            ftp.cwd('..')

    if not is_file_mode:
        xml_data = dict_to_list(xml_data)

    return xml_data
