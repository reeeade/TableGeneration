# main.py

import logging
import argparse
import sys
import pandas as pd
import os
import json
from typing import List, Optional, Dict, Any
import pprint
from datetime import datetime
import asyncio
from data_generator import (
    generate_user_data,
    generate_batch_user_data,
    generate_large_dataset,
    validate_user_data, generate_user_data_async
)
from clipboard_utils import export_data
from gmaps_api import prefill_address_cache
from config import COUNTRY_LOCALES, COUNTRY_NAMES
from encoding_utils import setup_windows_console_encoding


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """
    Настраивает логирование для приложения с поддержкой Unicode.

    Args:
        log_level: Уровень логирования ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Путь к файлу логов. Если None, логи записываются только в стандартный вывод.
    """
    # Словарь соответствия строк уровням логирования
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    # Получаем числовой уровень логирования
    numeric_level = levels.get(log_level.upper(), logging.INFO)

    # Настраиваем формат логирования
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Создаем основной логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Очищаем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Создаем форматтер
    formatter = logging.Formatter(log_format)

    # Добавляем обработчик для консоли с поддержкой Unicode
    # В Windows используем кодировку utf-8 для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)

    # Для Windows Python 3.6+ можно использовать следующий код:
    import sys
    if sys.platform == 'win32':
        # Пробуем настроить кодировку для консоли Windows
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleCP(65001)  # UTF-8
            kernel32.SetConsoleOutputCP(65001)  # UTF-8
        except:
            # Если не удалось переключить кодировку, используем транслитерацию для логов
            class TransliteratingHandler(logging.StreamHandler):
                def emit(self, record):
                    try:
                        msg = self.format(record)
                        # Заменяем русские символы на латинские для логирования
                        from unidecode import unidecode
                        msg = unidecode(msg)
                        stream = self.stream
                        stream.write(msg + self.terminator)
                        self.flush()
                    except Exception:
                        self.handleError(record)

            console_handler = TransliteratingHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(numeric_level)

    root_logger.addHandler(console_handler)

    # Если указан файл логов, добавляем обработчик для записи в файл
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)
    else:
        # По умолчанию записываем в data_generator.log
        file_handler = logging.FileHandler('data_generator.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)

    # Настраиваем логирование для библиотек
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)


def parse_arguments():
    """
    Разбирает аргументы командной строки.

    Returns:
        Разобранные аргументы
    """
    parser = argparse.ArgumentParser(description='Генератор случайных пользовательских данных')

    # Основные параметры
    parser.add_argument('-n', '--num-users', type=int, default=5,
                        help='Количество пользователей для генерации (по умолчанию: 5)')

    parser.add_argument('-c', '--countries', nargs='+', default=['US'],
                        help='Список кодов стран для генерации данных (по умолчанию: US)')

    parser.add_argument('-o', '--output', choices=['clipboard', 'csv', 'tsv', 'json', 'excel', 'sql'],
                        default='clipboard',
                        help='Формат вывода данных (по умолчанию: clipboard)')

    parser.add_argument('-f', '--filename', type=str,
                        help='Имя файла для сохранения данных (если не указано, генерируется автоматически)')

    # Дополнительные параметры
    parser.add_argument('-p', '--prefill-cache', action='store_true',
                        help='Предварительно заполнить кэш адресов для выбранных стран')

    parser.add_argument('-a', '--all-countries', action='store_true',
                        help='Генерировать данные для всех доступных стран')

    parser.add_argument('-l', '--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='Уровень логирования (по умолчанию: INFO)')

    parser.add_argument('--log-file', type=str,
                        help='Путь к файлу логов (по умолчанию: data_generator.log)')

    parser.add_argument('-s', '--show-countries', action='store_true',
                        help='Показать список доступных стран и выйти')

    parser.add_argument('-b', '--batch', action='store_true',
                        help='Режим пакетной генерации данных')

    parser.add_argument('--validate', action='store_true',
                        help='Проверить сгенерированные данные на корректность')

    parser.add_argument('--header', action='store_true',
                        help='Включить заголовки при экспорте в буфер обмена (только для clipboard)')

    parser.add_argument('--large', type=int,
                        help='Генерировать большой набор данных указанного размера')

    parser.add_argument('--batch-size', type=int, default=100,
                        help='Размер партии при генерации большого набора данных (по умолчанию: 100)')

    parser.add_argument('--config', type=str,
                        help='Путь к файлу конфигурации в формате JSON')

    return parser.parse_args()


def load_config_from_file(config_file: str) -> Dict[str, Any]:
    """
    Загружает параметры из файла конфигурации.

    Args:
        config_file: Путь к файлу конфигурации

    Returns:
        Словарь с параметрами
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info(f"Загружена конфигурация из файла {config_file}")
        return config
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла конфигурации {config_file}: {e}")
        return {}


def show_available_countries():
    """
    Выводит список доступных стран и их кодов.
    """
    print("Доступные страны:")
    print("=" * 50)
    print(f"{'Код':6} {'Название':30}")
    print("-" * 50)

    # Сортируем по коду страны
    for code in sorted(COUNTRY_NAMES.keys()):
        print(f"{code:6} {COUNTRY_NAMES[code]:30}")


def batch_generation_mode():
    """
    Режим пакетной генерации данных.
    Запрашивает у пользователя несколько конфигураций и генерирует данные для каждой из них.
    """
    print("Режим пакетной генерации данных")
    print("=" * 50)

    batch_configs = []

    while True:
        print("\nНовая партия данных:")
        name = input("Название партии (или пустая строка для завершения): ")
        if not name:
            break

        try:
            num_users = int(input("Количество пользователей: "))
            if num_users <= 0:
                print("Количество пользователей должно быть больше 0. Установлено значение 1.")
                num_users = 1
        except ValueError:
            print("Некорректное значение. Установлено значение 5.")
            num_users = 5

        countries_input = input("Коды стран (через пробел, или 'all' для всех стран): ")
        if countries_input.lower() == 'all':
            country_codes = list(COUNTRY_LOCALES.keys())
        else:
            country_codes = countries_input.upper().split()
            # Проверяем, что все коды стран существуют
            invalid_codes = [code for code in country_codes if code not in COUNTRY_LOCALES]
            if invalid_codes:
                print(f"Внимание: следующие коды стран не найдены: {', '.join(invalid_codes)}")
                # Фильтруем только существующие коды
                country_codes = [code for code in country_codes if code in COUNTRY_LOCALES]
                if not country_codes:
                    print("Нет корректных кодов стран. Установлено значение 'US'.")
                    country_codes = ['US']

        batch_configs.append({
            'name': name,
            'num_users': num_users,
            'country_codes': country_codes
        })

    if not batch_configs:
        print("Партии не заданы. Выход из режима пакетной генерации.")
        return

    print("\nГенерация данных...")
    batch_results = generate_batch_user_data(batch_configs)

    # Спрашиваем, в каком формате сохранить результаты
    output_format = input("\nФормат вывода (clipboard, csv, tsv, json, excel, sql): ").lower()
    if output_format not in ['clipboard', 'csv', 'tsv', 'json', 'excel', 'sql']:
        print(f"Некорректный формат вывода: {output_format}. Установлено значение 'csv'.")
        output_format = 'csv'

    # Экспортируем каждую партию
    for name, df in batch_results.items():
        if not df.empty:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}"
            if output_format != 'clipboard':
                extensions = {
                    'csv': '.csv',
                    'tsv': '.tsv',
                    'json': '.json',
                    'excel': '.xlsx',
                    'sql': '.sql'
                }
                filename = f"{filename}{extensions.get(output_format, '.csv')}"
                print(f"Сохранение {name} в {filename}...")
                export_data(df, output_format, filename)
            else:
                print(f"Копирование {name} в буфер обмена...")
                export_data(df, 'clipboard')
                input("Нажмите Enter для продолжения...")

    print("\nГенерация данных завершена.")


def interactive_mode():
    """
    Интерактивный режим для генерации данных с запросом параметров от пользователя.
    """
    print("Интерактивный режим генерации данных")
    print("=" * 50)

    # Запрашиваем количество пользователей
    while True:
        try:
            num_users = int(input("Количество пользователей (по умолчанию: 5): ") or "5")
            if num_users <= 0:
                print("Количество пользователей должно быть больше 0.")
                continue
            break
        except ValueError:
            print("Необходимо ввести целое число.")

    # Запрашиваем коды стран
    countries_input = input("Коды стран через пробел (или 'all' для всех стран, по умолчанию: US): ") or "US"
    if countries_input.lower() == 'all':
        country_codes = list(COUNTRY_LOCALES.keys())
    else:
        country_codes = countries_input.upper().split()

    # Запрашиваем формат вывода
    output_formats = ['clipboard', 'csv', 'tsv', 'json', 'excel', 'sql']
    output_format = input(f"Формат вывода ({', '.join(output_formats)}, по умолчанию: clipboard): ") or "clipboard"
    if output_format not in output_formats:
        print(f"Некорректный формат вывода: {output_format}. Установлено значение 'clipboard'.")
        output_format = 'clipboard'

    # Запрашиваем имя файла, если нужно
    filename = None
    if output_format != 'clipboard':
        filename = input(f"Имя файла (по умолчанию: автоматически): ")

    # Генерируем данные
    print(f"\nГенерация {num_users} пользователей из стран: {', '.join(country_codes)}...")
    df = asyncio.run(generate_user_data_async(num_users=num_users, country_codes=country_codes))

    # Экспортируем данные
    if output_format == 'clipboard':
        header = input("Включить заголовки в буфер обмена? (y/n, по умолчанию: n): ").lower() == 'y'
        export_data(df, output_format, None, header)
        print(f"Сгенерировано {len(df)} записей и скопировано в буфер обмена.")
    else:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            extensions = {
                'csv': '.csv',
                'tsv': '.tsv',
                'json': '.json',
                'excel': '.xlsx',
                'sql': '.sql'
            }
            filename = f"user_data_{timestamp}{extensions.get(output_format, '.csv')}"

        export_data(df, output_format, filename)
        print(f"Сгенерировано {len(df)} записей и сохранено в {filename}.")


def main():
    """
    Основная функция программы.
    """
    # Настраиваем кодировку для Windows
    setup_windows_console_encoding()

    args = parse_arguments()

    # Настраиваем логирование
    setup_logging(args.log_level, args.log_file)

    # Показываем список стран и выходим, если запрошено
    if args.show_countries:
        show_available_countries()
        sys.exit(0)

    # Загружаем конфигурацию из файла, если указана
    config = {}
    if args.config:
        config = load_config_from_file(args.config)
        # Применяем параметры из файла, если они не указаны в командной строке
        if 'num_users' in config and args.num_users == 5:  # 5 - значение по умолчанию
            args.num_users = config['num_users']
        if 'countries' in config and args.countries == ['US']:  # ['US'] - значение по умолчанию
            args.countries = config['countries']
        if 'output' in config and args.output == 'clipboard':  # 'clipboard' - значение по умолчанию
            args.output = config['output']
        if 'filename' in config and not args.filename:
            args.filename = config['filename']

    # Интерактивный режим
    if '-i' in sys.argv or '--interactive' in sys.argv:
        interactive_mode()
        sys.exit(0)

    # Режим пакетной генерации
    if args.batch:
        batch_generation_mode()
        sys.exit(0)

    # Определяем список стран
    if args.all_countries:
        country_codes = list(COUNTRY_LOCALES.keys())
    else:
        country_codes = args.countries
        # Проверяем, что все коды стран существуют
        invalid_codes = [code for code in country_codes if code not in COUNTRY_LOCALES]
        if invalid_codes:
            logging.warning(f"Следующие коды стран не найдены: {', '.join(invalid_codes)}")
            # Фильтруем только существующие коды
            country_codes = [code for code in country_codes if code in COUNTRY_LOCALES]
            if not country_codes:
                logging.error("Нет корректных кодов стран. Используется значение по умолчанию 'US'.")
                country_codes = ['US']

    # Предварительно заполняем кэш адресов, если запрошено
    if args.prefill_cache:
        logging.info(f"Предварительное заполнение кэша адресов для стран: {', '.join(country_codes)}")
        prefill_address_cache(country_codes, addresses_per_country=3)

    # Генерируем данные
    if args.large:
        logging.info(f"Генерация большого набора данных: {args.large} записей (размер партии: {args.batch_size})")
        df = asyncio.run(generate_user_data_async(num_users=args.large, country_codes=country_codes))
    else:
        logging.info(f"Генерация данных для {args.num_users} пользователей из стран: {', '.join(country_codes)}")
        df = asyncio.run(generate_user_data_async(num_users=args.num_users, country_codes=country_codes))

    # Проверяем данные, если запрошено
    if args.validate:
        logging.info("Проверка сгенерированных данных на корректность")
        df, errors = validate_user_data(df)
        if errors:
            logging.warning(f"Найдено {len(errors)} записей с ошибками")
            for error in errors:
                logging.warning(f"Ошибка в записи {error['id']}: {', '.join(error['errors'])}")

    # Выводим статистику
    logging.info(f"Сгенерировано {len(df)} записей")
    country_counts = df['geo'].value_counts()
    for country, count in country_counts.items():
        country_name = COUNTRY_NAMES.get(country, country)
        logging.info(f"  {country} ({country_name}): {count} записей")

    # Экспортируем данные
    export_data(df, args.output, args.filename, args.header)

    if args.output == 'clipboard':
        print(f"Генерация данных завершена. {len(df)} записей скопировано в буфер обмена.")
    else:
        filename = args.filename or f"user_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        extensions = {'csv': '.csv', 'tsv': '.tsv', 'json': '.json', 'excel': '.xlsx', 'sql': '.sql'}
        if not args.filename:
            filename += extensions.get(args.output, '.csv')
        print(f"Генерация данных завершена. {len(df)} записей сохранено в {filename}")


def create_sample_config():
    """
    Создает файл с примером конфигурации в формате JSON.
    """
    config = {
        "num_users": 20,
        "countries": ["US", "GB", "DE", "FR", "JP"],
        "output": "json",
        "filename": "user_data.json",
        "validate": True,
        "batch_configs": [
            {
                "name": "us_users",
                "num_users": 10,
                "country_codes": ["US"]
            },
            {
                "name": "eu_users",
                "num_users": 15,
                "country_codes": ["DE", "FR", "GB", "IT", "ES"]
            }
        ],
        "user_gen_config": {
            "min_age": 25,
            "max_age": 45,
            "password_length": 16
        }
    }

    with open('sample_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

    print("Пример файла конфигурации создан: sample_config.json")


if __name__ == "__main__":
    # Обрабатываем специальные команды
    if len(sys.argv) > 1 and sys.argv[1] == '--create-config':
        create_sample_config()
        sys.exit(0)

    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        logging.exception(f"Неожиданная ошибка: {e}")
        sys.exit(1)
