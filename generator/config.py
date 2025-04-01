import os
from dotenv import load_dotenv
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение API-ключа Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    logger.warning("GOOGLE_MAPS_API_KEY не установлен в переменных окружения. Некоторые функции будут недоступны.")

# Словарь локализации по странам, расширенный и проверенный список
COUNTRY_LOCALES = {
    # Европа
    'AT': 'de_AT',  # Австрия
    'BE': 'nl_BE',  # Бельгия
    'BG': 'bg_BG',  # Болгария
    'CH': 'de_CH',  # Швейцария
    'CY': 'el_CY',  # Кипр
    'CZ': 'cs_CZ',  # Чехия
    'DE': 'de_DE',  # Германия
    'DK': 'da_DK',  # Дания
    'EE': 'et_EE',  # Эстония
    'ES': 'es_ES',  # Испания
    'FI': 'fi_FI',  # Финляндия
    'FR': 'fr_FR',  # Франция
    'GB': 'en_GB',  # Великобритания
    'GR': 'el_GR',  # Греция
    'HR': 'hr_HR',  # Хорватия
    'HU': 'hu_HU',  # Венгрия
    'IE': 'en_IE',  # Ирландия
    'IT': 'it_IT',  # Италия
    'LT': 'lt_LT',  # Литва
    'LU': 'fr_LU',  # Люксембург
    'LV': 'lv_LV',  # Латвия
    'MT': 'mt_MT',  # Мальта (может не поддерживаться)
    'NL': 'nl_NL',  # Нидерланды
    'NO': 'no_NO',  # Норвегия
    'PL': 'pl_PL',  # Польша
    'PT': 'pt_PT',  # Португалия
    'RO': 'ro_RO',  # Румыния
    'SE': 'sv_SE',  # Швеция
    'SI': 'sl_SI',  # Словения
    'SK': 'sk_SK',  # Словакия

    # Азия
    'AE': 'ar_AE',  # ОАЭ
    'CN': 'zh_CN',  # Китай
    'HK': 'zh_HK',  # Гонконг
    'ID': 'id_ID',  # Индонезия
    'IL': 'he_IL',  # Израиль
    'IN': 'hi_IN',  # Индия
    'JP': 'ja_JP',  # Япония
    'KR': 'ko_KR',  # Южная Корея
    'MY': 'ms_MY',  # Малайзия (может не поддерживаться)
    'PH': 'fil_PH',  # Филиппины (может не поддерживаться)
    'SA': 'ar_SA',  # Саудовская Аравия
    'SG': 'en_SG',  # Сингапур (используем en_GB если не поддерживается)
    'TH': 'th_TH',  # Таиланд
    'TR': 'tr_TR',  # Турция
    'TW': 'zh_TW',  # Тайвань
    'VN': 'vi_VN',  # Вьетнам

    # Америка
    'AR': 'es_AR',  # Аргентина
    'BR': 'pt_BR',  # Бразилия
    'CA': 'en_CA',  # Канада
    'CL': 'es_CL',  # Чили
    'CO': 'es_CO',  # Колумбия
    'MX': 'es_MX',  # Мексика
    'PE': 'es_PE',  # Перу
    'US': 'en_US',  # США

    # Океания
    'AU': 'en_AU',  # Австралия
    'NZ': 'en_NZ',  # Новая Зеландия

    # Африка
    'EG': 'ar_EG',  # Египет
    'ZA': 'en_US',  # ЮАР (используем en_US если en_ZA не поддерживается)

    # Бывший СССР
    'BY': 'be_BY',  # Беларусь (может не поддерживаться)
    'GE': 'ka_GE',  # Грузия
    'KZ': 'kk_KZ',  # Казахстан (может не поддерживаться)
    'RU': 'ru_RU',  # Россия
    'UA': 'uk_UA',  # Украина
}

# Попытка импорта pycountry для получения корректных названий стран
try:
    import pycountry

    # Создаем словарь с корректными названиями стран
    COUNTRY_NAMES = {country.alpha_2: country.name for country in pycountry.countries}
    logger.info("Используются данные о странах из библиотеки pycountry")
except ImportError:
    logger.warning("Библиотека pycountry не установлена. Используются предопределенные данные о странах.")
    # Предопределенные названия стран (на случай, если pycountry не установлен)
    COUNTRY_NAMES = {
        'AT': 'Austria',
        'BE': 'Belgium',
        'BG': 'Bulgaria',
        'CH': 'Switzerland',
        'CY': 'Cyprus',
        'CZ': 'Czech Republic',
        'DE': 'Germany',
        'DK': 'Denmark',
        'EE': 'Estonia',
        'ES': 'Spain',
        'FI': 'Finland',
        'FR': 'France',
        'GB': 'United Kingdom',
        'GR': 'Greece',
        'HR': 'Croatia',
        'HU': 'Hungary',
        'IE': 'Ireland',
        'IT': 'Italy',
        'LT': 'Lithuania',
        'LU': 'Luxembourg',
        'LV': 'Latvia',
        'MT': 'Malta',
        'NL': 'Netherlands',
        'NO': 'Norway',
        'PL': 'Poland',
        'PT': 'Portugal',
        'RO': 'Romania',
        'SE': 'Sweden',
        'SI': 'Slovenia',
        'SK': 'Slovakia',
        'AE': 'United Arab Emirates',
        'CN': 'China',
        'HK': 'Hong Kong',
        'ID': 'Indonesia',
        'IL': 'Israel',
        'IN': 'India',
        'JP': 'Japan',
        'KR': 'South Korea',
        'MY': 'Malaysia',
        'PH': 'Philippines',
        'SA': 'Saudi Arabia',
        'SG': 'Singapore',
        'TH': 'Thailand',
        'TR': 'Turkey',
        'TW': 'Taiwan',
        'VN': 'Vietnam',
        'AR': 'Argentina',
        'BR': 'Brazil',
        'CA': 'Canada',
        'CL': 'Chile',
        'CO': 'Colombia',
        'MX': 'Mexico',
        'PE': 'Peru',
        'US': 'United States',
        'AU': 'Australia',
        'NZ': 'New Zealand',
        'EG': 'Egypt',
        'ZA': 'South Africa',
        'BY': 'Belarus',
        'GE': 'Georgia',
        'KZ': 'Kazakhstan',
        'RU': 'Russian Federation',
        'UA': 'Ukraine',
    }

# Динамически создаем список координат городов для каждой страны
# Некоторые базовые координаты, остальные будут загружены из внешнего источника или API
CITY_COORDINATES = {
    'US': [
        '40.712776,-74.005974',  # New York
        '34.052235,-118.243683',  # Los Angeles
        '41.878113,-87.629799',  # Chicago
        '29.760427,-95.369804',  # Houston
        '33.748997,-84.387985',  # Atlanta
        '39.952583,-75.165222',  # Philadelphia
        '38.907192,-77.036873',  # Washington DC
        '42.360082,-71.058880',  # Boston
        '32.776665,-96.796989',  # Dallas
        '37.774929,-122.419418',  # San Francisco
    ],
    'GB': [
        '51.507351,-0.127758',  # London
        '53.483959,-2.244644',  # Manchester
        '55.953251,-3.188267',  # Edinburgh
        '52.486244,-1.890401',  # Birmingham
        '51.454513,-2.587910',  # Bristol
    ],
    'DE': [
        '52.520008,13.404954',  # Berlin
        '48.135124,11.581981',  # Munich
        '50.110924,8.682127',  # Frankfurt
        '53.551086,9.993682',  # Hamburg
        '51.227741,6.773456',  # Dusseldorf
    ],
    'FR': [
        '48.856613,2.352222',  # Paris
        '43.296482,5.369780',  # Marseille
        '45.764043,4.835659',  # Lyon
        '44.837789,-0.579180',  # Bordeaux
        '43.610769,3.876716',  # Montpellier
    ],
}


# Загрузка дополнительных координат городов из файла или API, если они не определены
def load_additional_coordinates():
    """
    Загружает дополнительные координаты городов для стран, которые не определены в CITY_COORDINATES.
    Для этого можно использовать внешний API или локальный файл.
    """
    global CITY_COORDINATES

    for country_code in COUNTRY_LOCALES.keys():
        if country_code not in CITY_COORDINATES or not CITY_COORDINATES[country_code]:
            # Если для страны нет координат, добавляем стандартные значения
            # В реальном приложении здесь можно использовать геокодирование или другой источник данных
            if country_code not in CITY_COORDINATES:
                CITY_COORDINATES[country_code] = []

            # Если мы не можем получить реальные координаты, используем стандартные значения
            if not CITY_COORDINATES[country_code]:
                logger.warning(
                    f"Для страны {country_code} не определены координаты городов. Используются стандартные значения.")
                # Добавляем фиктивные координаты (в реальном приложении заменить на настоящие)
                CITY_COORDINATES[country_code] = ['0.0,0.0']


# Загружаем дополнительные координаты
load_additional_coordinates()

# Настройки для радиусов поиска
DEFAULT_RADIUS = 30000  # 30 км
BORDER_RADIUS = 20000  # 20 км

# Создаем базовые данные о радиусах поиска
RADIUS_DATA = {}
for country_code in COUNTRY_LOCALES.keys():
    RADIUS_DATA[country_code] = {
        'default': DEFAULT_RADIUS,
        'border': BORDER_RADIUS,
        'border_cities': []  # Будет заполнено при необходимости
    }

# Настройки для генерации данных пользователей
USER_GEN_CONFIG = {
    'min_age': 25,
    'max_age': 45,
    'proxy_port_range': (100, 299),  # Расширенный диапазон портов
    'password_length': 18,  # Увеличенная длина пароля
    'default_email_domains': [
        'gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com',
        'icloud.com', 'protonmail.com', 'mail.com', 'aol.com'
    ],
}

# Настройки для Google Maps API
GMAPS_CONFIG = {
    'max_retries': 5,
    'retry_base_delay': 2,  # секунды
    'language': 'en',
    'place_types': ['street_address', 'premise', 'subpremise'],
    'required_components': ['street_number', 'route', 'postal_code', 'locality'],
}

# Добавляем информацию о телефонных кодах стран
COUNTRY_PHONE_CODES = {
    'US': '+1',  # США
    'CA': '+1',  # Канада
    'GB': '+44',  # Великобритания
    'DE': '+49',  # Германия
    'FR': '+33',  # Франция
    'IT': '+39',  # Италия
    'ES': '+34',  # Испания
    'JP': '+81',  # Япония
    'CN': '+86',  # Китай
    'IN': '+91',  # Индия
    'RU': '+7',  # Россия
    'BR': '+55',  # Бразилия
    'AU': '+61',  # Австралия
    'ZA': '+27',  # ЮАР
}


# Функция для получения телефонного кода страны
def get_country_phone_code(country_code):
    """
    Возвращает телефонный код страны по её ISO коду.
    Если код не найден, возвращает '+1' (код США) по умолчанию.
    """
    return COUNTRY_PHONE_CODES.get(country_code, '+1')
