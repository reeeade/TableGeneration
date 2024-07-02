import os
import random
import string
import pandas as pd
import pyperclip
import googlemaps
from faker import Faker
from unidecode import unidecode
from dotenv import load_dotenv
from Cityes import city_coordinates

# Загружаем переменные окружения из файла .env
load_dotenv()

# Замените на ваш собственный API ключ
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

# Инициализация клиента Google Maps
gmaps = googlemaps.Client(key=API_KEY)

# Инициализация библиотеки Faker с поддержкой стран
fake = Faker()


# Функция генерации пароля
def generate_strong_compliant_password(length: int = 16) -> str:
    while True:
        password = ''.join(
            random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation,
                           k=length))
        if (
                len(password) == length and
                any(c.isdigit() for c in password) and
                any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                password[0].isalnum() and
                not any(password[i] == password[i + 1] for i in range(len(password) - 1))
        ):
            return password


# Функция генерации прокси-адреса
def generate_correct_proxy(geo_code: str, port_range: tuple = (100, 199)) -> str:
    port = random.randint(port_range[0], port_range[1])
    return f"xxfyOfwK90p50KT0:wifi;{geo_code.lower()};;;@proxy.froxy.com:9{port}"


# Функция генерации даты рождения
def generate_birth_date(min_age: int = 21, max_age: int = 27) -> str:
    today = pd.Timestamp.today()
    start_date = today - pd.DateOffset(years=max_age)
    end_date = today - pd.DateOffset(years=min_age)
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date.strftime("%d.%m.%Y")


# Функция нормализации строк для замены специальных символов
def normalize_string(input_str):
    return unidecode(input_str)


# Функция удаления названия страны из адреса
def remove_country_from_address(address: str, country_name: str) -> str:
    if address.endswith(country_name):
        address = address[:-(len(country_name) + 2)]  # +2 для ", "
    return address


# Функция генерации реального адреса на основе случайных координат с использованием Google Maps Places API
def generate_address(country_code: str) -> str or None:
    country_names = {
        'ES': 'Spain',
        'DE': 'Germany',
        'FR': 'France',
        'GB': 'United Kingdom',
        'PL': 'Poland',
        'NL': 'Netherlands'
    }
    query = 'residential building'
    location = random.choice(city_coordinates[country_code])
    radius = 30000  # 30 km radius

    response = gmaps.places(query, location=location, radius=radius, language='en')

    if response['status'] == 'OK' and response['results']:
        place = random.choice(response['results'])
        formatted_address = place.get('formatted_address')
        if formatted_address:
            normalized_address = normalize_string(formatted_address)
            return remove_country_from_address(normalized_address, country_names[country_code])
    return None


# Функция генерации имени и фамилии в соответствии со страной
def generate_name(country_code: str) -> str:
    faker = Faker({
                      'ES': 'es_ES',
                      'DE': 'de_DE',
                      'FR': 'fr_FR',
                      'GB': 'en_GB',
                      'PL': 'pl_PL',
                      'NL': 'nl_NL'
                  }[country_code])

    while True:
        first_name = faker.first_name()
        last_name = faker.last_name()
        full_name = f"{first_name} {last_name}"
        normalized_name = normalize_string(full_name)

        # Проверяем, что имя и фамилия содержат не более двух слов и все символы ASCII
        if len(normalized_name.split()) == 2 and all(ord(c) < 128 for c in normalized_name):
            return normalized_name


# Генерация пользовательских данных
def generate_user_data(num_users: int = 20, country_codes: list = None) -> pd.DataFrame:
    if country_codes is None:
        countries = ['ES', 'DE', 'FR', 'GB', 'PL', 'NL']
    else:
        countries = country_codes
    data = []
    for _ in range(num_users):
        country = random.choice(countries)
        address = generate_address(country)
        if address:
            birth_date = generate_birth_date()
            name = generate_name(country)
            password = generate_strong_compliant_password()
            proxy = generate_correct_proxy(country)
            data.append([country, '', password, '', name, address, birth_date, '', proxy])

    columns = ['Geo', 'AppleID', 'pass', 'number', 'name', 'address', 'birthday', 'creation', 'proxy']
    data_frame = pd.DataFrame(data, columns=columns)
    return data_frame


# Копирование данных в буфер обмена без заголовков
def copy_to_clipboard(data_frame: pd.DataFrame) -> None:
    csv_data = data_frame.to_csv(index=False, header=False, sep='\t')
    pyperclip.copy(csv_data)
    print("Data copied to clipboard successfully.")


# ['ES', 'DE', 'FR', 'GB', 'PL', 'NL']
# Генерация пользовательских данных и копирование в буфер обмена
df = generate_user_data(num_users=20, country_codes=['ES', 'DE', 'PL', 'NL'])
copy_to_clipboard(df)
