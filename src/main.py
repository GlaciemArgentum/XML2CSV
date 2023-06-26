from src.processing import get_data  # Локальный модуль для сбора и обработки информации.
from src.read_terminal import read   # Локальный модуль для чтения из терминала.
from src.server import connect_ftp   # Локальный модуль для подключения к серверу.
from src.write import make_csv       # Локальный модуль для записи отчёта.


def main():
    """
    Начало программы.
    """

    params = read()

    ftp = connect_ftp()

    xml_data = get_data(ftp, *params)
    ftp.quit()

    make_csv(params, xml_data)

    print("xml2csv: Done!")
