#!/usr/bin/env python3

# xml2csv.py

"""
Описание: Эта программа подключается к FTP-серверу и делает отчёт на основе данных с сервера в виде CSV-файла.
Сервер содержит данные (XML-файлы) о том, сколько людей и когда вошло и вышло из торгового центра, какими входами они
пользовались и другие метаданные.

Автор: Трофимов Егор

Дата создания: 18.06.2023
Дата изменения: 27.06.2023

Версия: 1.1
Версия Python: 3.10.9

Зависимости: alive_bar, yaml
alive_bar:
    Сайт: https://pypi.org/project/alive-progress/
    Установить с помощью pip: $ pip3 install alive-progress
yaml:
    Сайт: https://pyyaml.org/
    Установить с помощью pip: $ pip3 install pyyaml
"""

from src.main import main

if __name__ == "__main__":
    main()
