import os
import random
import string
import pandas as pd
import pyperclip
import googlemaps
from faker import Faker
from unidecode import unidecode
from dotenv import load_dotenv
from datetime import datetime, timedelta
from Cityes import city_coordinates, radius_data, country_names, country_locales

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение API ключа Google Maps из переменных окружения
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

# Проверка наличия API ключа
if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY не установлен в переменных окружения.")

# Инициализация клиента Google Maps
gmaps = googlemaps.Client(key=API_KEY)

# Предварительная инициализация объектов Faker для каждой локали
faker_objects = {code: Faker(locale) for code, locale in country_locales.items()}


def generate_strong_compliant_password(length: int = 16) -> str:
    """
    Генерирует надежный пароль заданной длины, соответствующий требованиям.
    Пароль должен содержать как минимум одну цифру, одну строчную букву,
    одну заглавную букву и один специальный символ.
    Первый символ должен быть буквенно-цифровым, и никакие два подряд идущих
    символа не должны быть одинаковыми.
    """
    import secrets

    if length < 4:
        raise ValueError("Длина пароля должна быть не менее 4 символов.")

    while True:
        # Обеспечиваем наличие хотя бы одного символа из каждой категории
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice(string.punctuation),
        ]

        # Заполняем оставшуюся длину пароля
        remaining_length = length - 4
        all_chars = string.ascii_letters + string.digits + string.punctuation
        password += [secrets.choice(all_chars) for _ in range(remaining_length)]

        # Перемешиваем символы в пароле
        random.shuffle(password)

        # Убеждаемся, что первый символ является буквенно-цифровым
        if not password[0].isalnum():
            # Меняем местами с первым буквенно-цифровым символом
            for i in range(1, length):
                if password[i].isalnum():
                    password[0], password[i] = password[i], password[0]
                    break
            else:
                continue  # Повторяем, если не найден буквенно-цифровой символ

        # Проверяем, что нет двух одинаковых подряд идущих символов
        if not any(password[i] == password[i + 1] for i in range(len(password) - 1)):
            return ''.join(password)


def generate_correct_proxy(geo_code: str, port_range: tuple = (100, 199)) -> str:
    """
    Генерирует корректный прокси-адрес с случайным портом в указанном диапазоне.
    """
    port = random.randint(*port_range)
    return f"socks5://xxfyOfwK90p50KT0:wifi;{geo_code.lower()};;;@proxy.froxy.com:9{port}"


def generate_birth_date(min_age: int = 25, max_age: int = 35) -> str:
    """
    Генерирует случайную дату рождения в указанном диапазоне возрастов.
    """
    today = datetime.today()
    start_date = today - timedelta(days=365 * max_age)
    end_date = today - timedelta(days=365 * min_age)
    delta_days = (end_date - start_date).days
    random_days = random.randint(0, delta_days)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%d.%m.%Y")


def normalize_string(input_str: str) -> str:
    """
    Нормализует строку, заменяя специальные символы на их ASCII-эквиваленты.
    """
    return unidecode(input_str)


def remove_country_from_address(address: str, country_name: str) -> str:
    """
    Удаляет указанное название страны из конца адреса.
    """
    suffix = f", {country_name}"
    if address.endswith(suffix):
        return address[:-len(suffix)]
    return address


def generate_address(country_code: str) -> str or None:
    """
    Генерирует реальный адрес в указанной стране с использованием Google Maps Places API.
    """
    query = 'residential building'
    location = random.choice(city_coordinates[country_code])

    # Определение радиуса на основе местоположения
    radius_info = radius_data[country_code]
    if location in radius_info['border_cities']:
        radius = radius_info['border']
    else:
        radius = radius_info['default']

    attempts = 0
    max_attempts = 5  # Максимальное количество попыток для избежания бесконечного цикла

    while attempts < max_attempts:
        try:
            response = gmaps.places(query, location=location, radius=radius, language='en')
        except googlemaps.exceptions.ApiError as e:
            print(f"Ошибка API: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None

        if response.get('status') == 'OK' and response.get('results'):
            place = random.choice(response['results'])
            formatted_address = place.get('formatted_address')
            if formatted_address:
                normalized_address = normalize_string(formatted_address)
                if country_names[country_code] in normalized_address:
                    return remove_country_from_address(normalized_address, country_names[country_code])
        attempts += 1

    return None


def generate_name(country_code: str) -> str:
    """
    Генерирует полное имя пользователя на основе указанного кода страны.
    """
    faker = faker_objects[country_code]

    while True:
        first_name = faker.first_name()
        last_name = faker.last_name()
        full_name = f"{first_name} {last_name}"
        normalized_name = normalize_string(full_name)

        # Проверяем, что имя состоит из двух слов и содержит только ASCII-символы
        if len(normalized_name.split()) == 2 and normalized_name.isascii():
            return normalized_name


def generate_user_data(num_users: int = 20, country_codes: list = None) -> pd.DataFrame:
    """
    Генерирует DataFrame с пользовательскими данными для указанного количества пользователей.
    """

    if country_codes is None:
        countries = list(country_locales.keys())
    else:
        countries = country_codes

    def create_user_record():
        while True:
            country = random.choice(countries)
            address = generate_address(country)
            if address:
                birth_date = generate_birth_date()
                name = generate_name(country)
                password = generate_strong_compliant_password()
                proxy = generate_correct_proxy(country)
                return [country, '', password, '', name, address, birth_date, '', proxy]

    data = [create_user_record() for _ in range(num_users)]
    columns = ['Geo', 'AppleID', 'pass', 'number', 'name', 'address', 'birthday', 'creation', 'proxy']
    return pd.DataFrame(data, columns=columns)


def copy_to_clipboard(data_frame: pd.DataFrame) -> None:
    """
    Копирует данные из DataFrame в буфер обмена без заголовков.
    """
    try:
        csv_data = data_frame.to_csv(index=False, header=False, sep='\t')
        pyperclip.copy(csv_data)
        print("Данные успешно скопированы в буфер обмена.")
    except pyperclip.PyperclipException as e:
        print(f"Не удалось скопировать данные в буфер обмена: {e}")


# 'ES', 'DE', 'FR', 'GB', 'PL', 'NL', 'AT', 'DK', 'UA','RO', 'EE', 'LV', 'LT', 'BG']

# Генерация пользовательских данных и копирование в буфер обмена
df = generate_user_data(num_users=10, country_codes=['RO', 'EE', 'LV'])
copy_to_clipboard(df)
