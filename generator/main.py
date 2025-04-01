# main.py

import logging
import argparse
import sys
import pandas as pd
import os
from typing import List, Optional

from data_generator import generate_user_data, generate_batch_user_data
from clipboard_utils import export_data
from gmaps_api import prefill_address_cache
from config import COUNTRY_LOCALES


def setup_logging(log_level: str = 'INFO') -> None:
    """
    Настраивает логирование для приложения.

    Args:
        log_level: Уровень логирования ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
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

    # Настраиваем логгер
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('data_generator.log')
        ]
    )


def parse_arguments():
    """
    Разбирает аргументы командной строки.

    Returns:
        Разобранные аргументы
    """
    parser = argparse.ArgumentParser(description='Генератор случайных пользовательских данных')

    parser.add_argument('-n', '--num-users', type=int, default=5,
                        help='Количество пользователей для генерации (по умолчанию: 5)')

    parser.add_argument('-c', '--countries', nargs='+', default=['US'],
                        help='Список кодов стран для генерации данных (по умолчанию: US)')

    parser.add_argument('-o', '--output', choices=['clipboard', 'csv', 'tsv', 'json', 'excel'],
                        default='clipboard',
                        help='Формат вывода данных (по умолчанию: clipboard)')

    parser.add_argument('-f', '--filename', type=str,
                        help='Имя файла для сохранения данных (если не указано, генерируется автоматически)')

    parser.add_argument('-p', '--prefill-cache', action='store_true',
                        help='Предварительно заполнить кэш адресов для выбранных стран')

    parser.add_argument('-a', '--all-countries', action='store_true',
                        help='Генерировать данные для всех доступных стран')

    parser.add_argument('-l', '--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='Уровень логирования (по умолчанию: INFO)')

    parser.add_argument('-s', '--show-countries', action='store_true',
                        help='Показать список доступных стран и выйти')

    parser.add_argument('-b', '--batch', action='store_true',
                        help='Режим пакетной генерации данных')

    return parser.parse_args()


def show_available_countries():
    """
    Выводит список доступных стран и их кодов.
    """
    from config import COUNTRY_NAMES

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
    output_format = input("\nФормат вывода (clipboard, csv, tsv, json, excel): ").lower()
    if output_format not in ['clipboard', 'csv', 'tsv', 'json', 'excel']:
        print(f"Некорректный формат вывода: {output_format}. Установлено значение 'csv'.")
        output_format = 'csv'

    # Экспортируем каждую партию
    for name, df in batch_results.items():
        if not df.empty:
            filename = f"{name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            if output_format != 'clipboard':
                filename = f"{filename}.{output_format}" if output_format != 'excel' else f"{filename}.xlsx"
                print(f"Сохранение {name} в {filename}...")
                export_data(df, output_format, filename)
            else:
                print(f"Копирование {name} в буфер обмена...")
                export_data(df, 'clipboard')
                input("Нажмите Enter для продолжения...")

    print("\nГенерация данных завершена.")


def main():
    """
    Основная функция программы.
    """
    args = parse_arguments()

    # Настраиваем логирование
    setup_logging(args.log_level)

    # Показываем список стран и выходим, если запрошено
    if args.show_countries:
        show_available_countries()
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
    logging.info(f"Генерация данных для {args.num_users} пользователей из стран: {', '.join(country_codes)}")
    df = generate_user_data(num_users=args.num_users, country_codes=country_codes)

    # Выводим статистику
    logging.info(f"Сгенерировано {len(df)} записей")
    country_counts = df['geo'].value_counts()
    for country, count in country_counts.items():
        logging.info(f"  {country}: {count} записей")

    # Экспортируем данные
    export_data(df, args.output, args.filename)

    if args.output == 'clipboard':
        print(f"Генерация данных завершена. {len(df)} записей скопировано в буфер обмена.")
    else:
        filename = args.filename or f"user_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
        extensions = {'csv': '.csv', 'tsv': '.tsv', 'json': '.json', 'excel': '.xlsx'}
        if not args.filename:
            filename += extensions.get(args.output, '.csv')
        print(f"Генерация данных завершена. {len(df)} записей сохранено в {filename}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        logging.exception(f"Неожиданная ошибка: {e}")
        sys.exit(1)