import os
import random
import string
import pandas as pd
import pyperclip
import googlemaps
from faker import Faker
from unidecode import unidecode
from dotenv import load_dotenv
from Cityes import city_coordinates, radius_data

# Загружаем переменные окружения из файла .env
load_dotenv()

# Замените на ваш собственный API ключ
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

# Проверка наличия API ключа
if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY не установлен в переменных окружения.")

# Инициализация клиента Google Maps
gmaps = googlemaps.Client(key=API_KEY)

# Инициализация библиотеки Faker с поддержкой стран
fake = Faker()


# Функция генерации пароля
def generate_strong_compliant_password(length: int = 16) -> str:
    """
    Generates a strong, compliant password with the specified length.
    The password must contain at least one digit, one lowercase letter, one uppercase letter, and one special character.
    The first character must be an alphanumeric character and no two consecutive characters should be the same.

    :param length: The desired length of the password (default is 16)
    :type length: int
    :return: A strong, compliant password of the specified length
    :rtype: str
    """
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
    """
    Generates a correct proxy address with a random port within the specified range.

    :param geo_code: The ISO 3166-1 alpha-2 code of the country for which the proxy should be generated.
    :type geo_code: str
    :param port_range: A tuple containing the minimum and maximum port numbers for the proxy.
    :type port_range: tuple
    :return: A correct proxy address in the format "xxfyOfwK90p50KT0:wifi;{geo_code.lower()};;;@proxy.froxy.com:9{port}"
    :rtype: str
    """
    port = random.randint(port_range[0], port_range[1])
    return f"xxfyOfwK90p50KT0:wifi;{geo_code.lower()};;;@proxy.froxy.com:9{port}"


# Функция генерации даты рождения
def generate_birth_date(min_age: int = 25, max_age: int = 35) -> str:
    """
    Generates a random birthdate within the specified age range.

    :param min_age: The minimum age of the generated birthdate (default is 25)
    :type min_age: int
    :param max_age: The maximum age of the generated birthdate (default is 35)
    :type max_age: int
    :return: A random birthdate in the format "dd.mm.yyyy"
    :rtype: str
    """
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
    """
    Removes the specified country name from the end of the given address.
    The function assumes that the country name is followed by a comma and a space.

    :param address: The full address string from which the country name should be removed.
    :type address: str
    :param country_name: The name of the country to be removed from the address.
    :type country_name: str
    :return: The address string with the country name removed.
    :rtype: str
    """
    if address.endswith(country_name):
        address = address[:-(len(country_name) + 2)]  # +2 для ", "
    return address


# Функция генерации реального адреса на основе случайных координат с использованием Google Maps Places API
def generate_address(country_code: str) -> str or None:
    """
    Generates a real address in a specified country using Google Maps Places API.

    :param country_code: The ISO 3166-1 alpha-2 code of the country for which the address should be generated.
    :type country_code: str
    :return: A real address in the specified country, or None if the address could not be generated.
    :rtype: str or None
    """
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

    # Определение радиуса на основе координат
    radius = radius_data[country_code]['border'] if location in radius_data[country_code]['border_cities'] else \
        radius_data[country_code]['default']

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

        if response['status'] == 'OK' and response['results']:
            place = random.choice(response['results'])
            formatted_address = place.get('formatted_address')
            if formatted_address:
                normalized_address = normalize_string(formatted_address)
                if country_names[country_code] in normalized_address:
                    return remove_country_from_address(normalized_address, country_names[country_code])
        attempts += 1

    return None


# Функция генерации имени и фамилии в соответствии со страной
def generate_name(country_code: str) -> str:
    """
    Generates a full name for a user based on the specified country code.

    :param country_code: The ISO 3166-1 alpha-2 code of the country for which the name should be generated.
    :type country_code: str
    :return: A full name in the format "FirstName LastName" for a user in the specified country.
    :rtype: str
    """
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
    """
    Generates a DataFrame containing user data for the specified number of users.

    :param num_users: The number of users for which data should be generated. Default is 20.
    :type num_users: int
    :param country_codes: A list of ISO 3166-1 alpha-2 country codes for which data should be generated.
    If not provided, the function will generate data for six predefined countries.
    :type country_codes: list
    :return: A DataFrame containing user data, including country, address, birthdate, name, and password.
    :rtype: pd.DataFrame
    """
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
    """
    Copies the DataFrame data to the clipboard without headers.

    :param data_frame: A pandas DataFrame containing the data to be copied to the clipboard.
    :type data_frame: pd.DataFrame
    :return: None
    :rtype: None
    """
    csv_data = data_frame.to_csv(index=False, header=False, sep='\t')
    pyperclip.copy(csv_data)
    print("Data copied to clipboard successfully.")


# ['ES', 'DE', 'FR', 'GB', 'PL', 'NL']
# Генерация пользовательских данных и копирование в буфер обмена
df = generate_user_data(num_users=20, country_codes=['ES', 'DE', 'FR', 'PL', 'NL'])
copy_to_clipboard(df)
