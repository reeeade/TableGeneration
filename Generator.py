import random
import string
import pandas as pd
import pyperclip
import googlemaps
from faker import Faker
from unidecode import unidecode

# Замените на ваш собственный API ключ
API_KEY = 'Some key'

# Инициализация клиента Google Maps
gmaps = googlemaps.Client(key=API_KEY)

# Инициализация библиотеки Faker с поддержкой стран
fake = Faker()


# Функция генерации пароля
def generate_strong_compliant_password(length=16):
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
def generate_correct_proxy(geo_code, port_range=(100, 199)):
    port = random.randint(port_range[0], port_range[1])
    return f"xxfyOfwK90p50KT0:wifi;{geo_code.lower()};;;@proxy.froxy.com:9{port}"


# Функция генерации даты рождения
def generate_birth_date(min_age=21, max_age=27):
    today = pd.Timestamp.today()
    start_date = today - pd.DateOffset(years=max_age)
    end_date = today - pd.DateOffset(years=min_age)
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date.strftime("%d.%m.%Y")


# Функция нормализации строк для замены специальных символов
def normalize_string(input_str):
    return unidecode(input_str)


# Функция удаления названия страны из адреса
def remove_country_from_address(address, country_name):
    if address.endswith(country_name):
        address = address[:-(len(country_name) + 2)]  # +2 для ", "
    return address


# Координаты для различных городов в каждой стране
city_coordinates = {
    'ES': [
        '40.416775,-3.703790',  # Madrid
        '41.385064,2.173403',  # Barcelona
        '37.389092,-5.984459',  # Seville
        '39.469907,-0.376288',  # Valencia
        '36.721274,-4.421399'  # Malaga
    ],
    'DE': [
        '52.520008,13.404954',  # Berlin
        '48.135124,11.581981',  # Munich
        '50.110924,8.682127',  # Frankfurt
        '53.551086,9.993682',  # Hamburg
        '51.227741,6.773456'  # Dusseldorf
    ],
    'FR': [
        '48.856613,2.352222',  # Paris
        '43.296482,5.369780',  # Marseille
        '45.764043,4.835659',  # Lyon
        '44.837789,-0.579180',  # Bordeaux
        '43.610769,3.876716'  # Montpellier
    ],
    'GB': [
        '51.507351,-0.127758',  # London
        '53.483959,-2.244644',  # Manchester
        '55.953251,-3.188267',  # Edinburgh
        '52.486244,-1.890401',  # Birmingham
        '51.454513,-2.587910'  # Bristol
    ],
    'PL': [
        '52.229676,21.012229',  # Warsaw
        '50.064650,19.944980',  # Krakow
        '51.107883,17.038538',  # Wroclaw
        '53.428544,14.552812',  # Szczecin
        '51.759249,19.455983'  # Lodz
    ],
    'NL': [
        '52.367573,4.904139',  # Amsterdam
        '51.9225,4.47917',  # Rotterdam
        '52.078663,4.288788',  # The Hague
        '50.850340,5.688889',  # Maastricht
        '52.090737,5.121420'  # Utrecht
    ]
}


# Функция генерации реального адреса на основе случайных координат с использованием Google Maps Places API
def generate_address(country_code):
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
    radius = 50000  # 50 km radius

    response = gmaps.places(query, location=location, radius=radius, language='en')

    if response['status'] == 'OK' and response['results']:
        place = random.choice(response['results'])
        formatted_address = place.get('formatted_address')
        if formatted_address:
            normalized_address = normalize_string(formatted_address)
            return remove_country_from_address(normalized_address, country_names[country_code])
    return None


# Функция генерации имени и фамилии в соответствии со страной
def generate_name(country_code):
    fake = Faker({
                     'ES': 'es_ES',
                     'DE': 'de_DE',
                     'FR': 'fr_FR',
                     'GB': 'en_GB',
                     'PL': 'pl_PL',
                     'NL': 'nl_NL'
                 }[country_code])

    while True:
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        normalized_name = normalize_string(full_name)

        # Проверяем, что имя и фамилия содержат не более двух слов и все символы ASCII
        if len(normalized_name.split()) == 2 and all(ord(c) < 128 for c in normalized_name):
            return normalized_name


# Генерация пользовательских данных
def generate_user_data(num_users=200):
    countries = ['ES', 'DE', 'FR', 'GB', 'PL', 'NL']

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

    columns = ['Geo', 'AppleID', 'pass', 'number', 'name', 'adress', 'birthday', 'creation', 'proxy']
    df = pd.DataFrame(data, columns=columns)
    return df


# Копирование данных в буфер обмена без заголовков
def copy_to_clipboard(df):
    csv_data = df.to_csv(index=False, header=False, sep='\t')
    pyperclip.copy(csv_data)
    print("Data copied to clipboard successfully.")


# Генерация пользовательских данных и копирование в буфер обмена
df = generate_user_data(num_users=200)
copy_to_clipboard(df)
