"""
Модуль для подключения к FTP-серверу.
"""

from ftplib import FTP        # Стандартная библиотека для работы с FTP.

from yaml import safe_load    # Сторонняя библиотека для работы с YAML-файлами.


with open('src/config.yaml', 'r') as file:
    config = safe_load(file)

    HOST = config['server']['host']
    PORT = config['server']['port']
    USERNAME = config['server']['username']
    PASSWORD = config['server']['password']
    PASV_MODE = config['server']['pasv_mode']


def connect_ftp() -> FTP:
    """
    Функция выполняет подключение к FTP-серверу.
    """

    try:
        ftp = FTP()
        message_connect = ftp.connect(HOST, PORT)
        print(message_connect)
    except Exception:
        raise SystemExit("Не удалось подлючиться: {0}:{1}".format(HOST, PORT))

    try:
        message_login = ftp.login(USERNAME, PASSWORD)
        print(message_login)
    except Exception:
        raise SystemExit("Неверный логин или пароль.")

    ftp.set_pasv(PASV_MODE)

    return ftp
