# main.py
import logging
from data_generator import generate_user_data
from clipboard_utils import copy_to_clipboard

def main():
    logging.basicConfig(level=logging.INFO)
    # Генерация данных для выбранных стран
    df = generate_user_data(num_users=10, country_codes=["ES", "DE", "FR", "GB", "PL", "AT"])
    copy_to_clipboard(df)
    print("Генерация данных завершена.")

if __name__ == "__main__":
    main()
