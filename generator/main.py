# main.py

import logging
from data_generator import generate_user_data
from clipboard_utils import copy_to_clipboard


# Доступные страны:
# ["ES", "DE", "FR", "GB", "PL", "NL", "AT", "DK", "UA", "RO", "EE", "LV", "LT", "BG", "GE", "FI", "CZ", "IT","US"]

def main():
    logging.basicConfig(level=logging.INFO)

    # Здесь можно выбрать нужные страны из списка выше
    selected_countries = ["ES", "DE", "FR", "GB", "PL", "NL", "FI", "CZ", "IT"]

    df = generate_user_data(num_users=10, country_codes=selected_countries)
    copy_to_clipboard(df)
    print("Генерация данных завершена. Данные скопированы в буфер обмена.")


if __name__ == "__main__":
    main()
