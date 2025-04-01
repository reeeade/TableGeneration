# data_generator.py
import random
import pandas as pd
import asyncio
from faker import Faker
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
import uuid
import functools
import time

from config import (
    COUNTRY_LOCALES,
    USER_GEN_CONFIG,
    COUNTRY_NAMES,
    get_country_phone_code
)
from gmaps_api import generate_address, reset_used_addresses
from utils import (
    generate_birth_date,
    generate_strong_compliant_password,
    generate_correct_proxy,
    normalize_string,
    generate_email,
    generate_phone_number,
    run_concurrent_tasks
)
from models import User, UserProfile
from dataclasses import asdict

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация кэша Faker объектов
faker_cache = {}


def get_faker_for_country(country_code: str) -> Faker:
    """
    Возвращает объект Faker для указанной страны с кэшированием.
    Если локаль недоступна, возвращает Faker с локалью en_US.

    Args:
        country_code: Код страны

    Returns:
        Объект Faker для указанной страны
    """
    # Если объект уже создан, возвращаем его из кэша
    if country_code in faker_cache:
        return faker_cache[country_code]

    # Получаем локаль для страны
    locale = COUNTRY_LOCALES.get(country_code, 'en_US')

    try:
        # Пробуем создать Faker с указанной локалью
        faker = Faker(locale)
        # Проверяем, что локаль работает (пытаемся получить имя)
        faker.name()
        # Сохраняем в кэш
        faker_cache[country_code] = faker
        logger.debug(f"Создан Faker для локали {locale} (страна {country_code})")
        return faker
    except Exception as e:
        logger.warning(f"Не удалось инициализировать локаль {locale} для страны {country_code}: {e}")
        # Если локаль не поддерживается, используем en_US
        fallback_faker = Faker('en_US')
        faker_cache[country_code] = fallback_faker
        return fallback_faker


# Инициализация дефолтного Faker
default_faker = Faker('en_US')
faker_cache['default'] = default_faker


def retry_on_failure(max_retries=3, delay=1):
    """
    Декоратор для повтора функции при возникновении ошибки.

    Args:
        max_retries: Максимальное количество повторных попыток
        delay: Задержка между попытками в секундах
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Попытка {attempt + 1} не удалась: {e}. Повтор через {delay} сек...")
                        time.sleep(delay)
                    else:
                        logger.error(f"Все {max_retries} попытки не удались: {e}")
                        raise

        return wrapper

    return decorator


def generate_name(country_code: str) -> str:
    """
    Генерирует полное имя пользователя для заданного кода страны.

    Args:
        country_code: Код страны

    Returns:
        Нормализованное полное имя
    """
    faker = get_faker_for_country(country_code)

    max_attempts = 5
    for _ in range(max_attempts):
        first_name = faker.first_name()
        last_name = faker.last_name()
        full_name = f"{first_name} {last_name}"
        normalized_name = normalize_string(full_name)

        # Проверяем, что имя состоит из двух слов и содержит только ASCII символы
        if len(normalized_name.split()) == 2 and normalized_name.isascii():
            return normalized_name

    # Если после нескольких попыток не получили подходящее имя, генерируем с помощью default Faker
    logger.warning(f"Не удалось сгенерировать подходящее имя для страны {country_code}, использую запасной вариант")
    first_name = default_faker.first_name()
    last_name = default_faker.last_name()
    full_name = f"{first_name} {last_name}"
    return normalize_string(full_name)


def generate_creation_date() -> str:
    """
    Генерирует дату создания аккаунта в формате DD.MM.YYYY.
    Дата создания всегда в пределах последних 3 лет.

    Returns:
        Строка с датой в формате DD.MM.YYYY
    """
    current_year = datetime.now().year
    year = random.randint(current_year - 3, current_year)
    month = random.randint(1, 12)

    # Если выбран текущий год и месяц, ограничиваем день текущим днем
    if year == current_year and month == datetime.now().month:
        day = random.randint(1, datetime.now().day)
    else:
        # Определяем количество дней в месяце
        if month in [4, 6, 9, 11]:
            max_day = 30
        elif month == 2:
            # Проверка на високосный год
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                max_day = 29
            else:
                max_day = 28
        else:
            max_day = 31

        day = random.randint(1, max_day)

    return f"{day:02d}.{month:02d}.{year}"


def generate_user_profile(user_id: str, country_code: str) -> Dict[str, Any]:
    """
    Генерирует расширенный профиль пользователя.

    Args:
        user_id: ID пользователя
        country_code: Код страны

    Returns:
        Словарь с данными профиля пользователя
    """
    faker = get_faker_for_country(country_code)

    # Генерируем данные профиля
    profile = UserProfile(
        user_id=user_id,
        language=faker.language_name(),
        currency=faker.currency_code(),
        time_zone=faker.timezone(),
        payment_method=random.choice(['card', 'paypal', 'apple_pay', 'google_pay', None]),
        notification_settings='{"email": true, "push": true, "sms": false}',
        device_info='{"os": "iOS", "model": "iPhone 13", "browser": "Safari"}'
    )

    return asdict(profile)


async def create_user_record(country: str) -> Dict[str, Any]:
    """
    Асинхронно создает запись пользователя для указанной страны.

    Args:
        country: Код страны

    Returns:
        Словарь с данными пользователя
    """
    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        try:
            address = generate_address(country)
            if address:
                # Генерируем основные данные
                user_id = str(uuid.uuid4())
                name = generate_name(country)
                email = generate_email(name)
                birth_date = generate_birth_date()
                password = generate_strong_compliant_password()
                proxy = generate_correct_proxy(country)

                # Генерируем телефонный номер на основе кода страны
                country_code = get_country_phone_code(country)
                phone = generate_phone_number(country, country_code)

                creation_date = generate_creation_date()

                # Создаем основную запись пользователя
                user = User(
                    geo=country,  # Сохраняем гео-код
                    apple_id="",
                    password=generate_strong_compliant_password(),
                    number="",
                    name=generate_name(country),
                    address=address or "",
                    birthday=generate_birth_date()
                )

                # Создаем запись в виде словаря
                user_data = asdict(user)

                # Добавляем информацию о стране в формате ISO и название
                user_data['country_name'] = COUNTRY_NAMES.get(country, country)

                return {
                    "geo": user.geo,
                    "AppleID": user.apple_id,
                    "pass": user.password,
                    "number": user.number,
                    "name": user.name,
                    "address": user.address,
                    "birthday": user.birthday
                }

            attempts += 1
            logger.info(f"Не удалось получить адрес для страны {country} (попытка {attempts}/{max_attempts}).")
            await asyncio.sleep(1)  # Небольшая пауза перед повторной попыткой

        except Exception as e:
            logger.exception(f"Ошибка при создании записи пользователя для страны {country}: {e}")
            attempts += 1
            await asyncio.sleep(1)

    # Если за max_attempts адрес не получен, возвращаем запись с пустым адресом
    logger.warning(
        f"Не удалось получить адрес для страны {country} после {max_attempts} попыток. Запись будет создана с пустым адресом.")

    # Создаем запись с пустым адресом
    user_id = str(uuid.uuid4())
    name = generate_name(country)
    email = generate_email(name, generate=False)
    birth_date = generate_birth_date()
    password = generate_strong_compliant_password()
    proxy = generate_correct_proxy(country)

    # Генерируем телефонный номер на основе кода страны
    country_code = get_country_phone_code(country)
    phone = generate_phone_number(country, generate=False)

    creation_date = generate_creation_date()

    user = User(
        id=user_id,
        geo=country,
        apple_id=email,
        password=password,
        number=phone,
        name=name,
        address="",
        birthday=birth_date,
        creation=creation_date,
        proxy=proxy,
    )

    # Создаем запись в виде словаря
    user_data = asdict(user)

    # Добавляем информацию о стране в формате ISO и название
    user_data['country_name'] = COUNTRY_NAMES.get(country, country)

    return user_data


@reset_used_addresses
async def generate_user_data_async(num_users: int = 20, country_codes: Optional[List[str]] = None) -> pd.DataFrame:
    if country_codes is None:
        country_codes = list(COUNTRY_LOCALES.keys())
    else:
        # Проверяем, что все коды стран существуют
        valid_country_codes = [code for code in country_codes if code in COUNTRY_LOCALES]

        if not valid_country_codes:
            logger.error("Ни один из указанных кодов стран не найден в списке поддерживаемых стран")
            valid_country_codes = ['US']

        country_codes = valid_country_codes

    # Равномерное распределение пользователей
    country_counts = {country: num_users // len(country_codes) for country in country_codes}
    remainder = num_users % len(country_codes)

    # Распределяем остаток
    for i in range(remainder):
        country_counts[country_codes[i]] += 1

    # Создаем задачи
    tasks = []
    for country, count in country_counts.items():
        tasks.extend([create_user_record(country) for _ in range(count)])

    logger.info(f"Генерация данных для {num_users} пользователей из стран: {', '.join(country_counts.keys())}")

    # Максимум 20 одновременных задач
    max_workers = min(20, num_users)
    semaphore = asyncio.Semaphore(max_workers)

    async def limited_task(task):
        async with semaphore:
            return await task

    # Запускаем задачи с ограничением
    data = await asyncio.gather(*[limited_task(task) for task in tasks])

    # Перемешиваем данные перед созданием DataFrame
    random.shuffle(data)

    return pd.DataFrame(data)


def generate_user_data(num_users: int = 20, country_codes: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Синхронная обертка для асинхронной функции generate_user_data_async.

    Args:
        num_users: Количество пользователей для генерации
        country_codes: Список кодов стран. Если None, используются все доступные страны.

    Returns:
        DataFrame с данными пользователей
    """
    # Запускаем асинхронную функцию в событийном цикле
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(generate_user_data_async(num_users, country_codes))
    except Exception as e:
        logger.exception(f"Ошибка при генерации данных пользователей: {e}")
        # Возвращаем пустой DataFrame с теми же столбцами
        return pd.DataFrame(columns=[
            'id', 'geo', 'apple_id', 'password', 'number', 'name', 'address', 'birthday', 'creation', 'proxy',
            'country_name'
        ])
    finally:
        if not loop.is_running():
            loop.close()


def generate_batch_user_data(batch_configs: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
    """
    Генерирует несколько партий данных пользователей с разными конфигурациями.

    Args:
        batch_configs: Список словарей с конфигурациями для каждой партии.
            Каждый словарь должен содержать ключи 'num_users' и 'country_codes'.

    Returns:
        Словарь с названиями партий в качестве ключей и DataFrame в качестве значений
    """
    result = {}

    for i, config in enumerate(batch_configs):
        name = config.get('name', f'batch_{i}')
        num_users = config.get('num_users', 20)
        country_codes = config.get('country_codes')

        logger.info(f"Генерация партии '{name}' с {num_users} пользователями из стран: {country_codes}")

        try:
            df = generate_user_data(num_users, country_codes)
            result[name] = df
        except Exception as e:
            logger.exception(f"Ошибка при генерации партии '{name}': {e}")
            result[name] = pd.DataFrame()

    return result


def generate_large_dataset(total_users: int, batch_size: int = 100,
                           country_codes: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Генерирует большой набор данных пользователей по частям для экономии памяти.

    Args:
        total_users: Общее количество пользователей для генерации
        batch_size: Размер каждой партии
        country_codes: Список кодов стран. Если None, используются все доступные страны.

    Returns:
        DataFrame с данными пользователей
    """
    logger.info(f"Генерация большого набора данных: {total_users} пользователей (размер партии: {batch_size})")

    # Определяем количество полных партий и остаток
    full_batches = total_users // batch_size
    remainder = total_users % batch_size

    data_frames = []

    # Генерируем полные партии
    for i in range(full_batches):
        logger.info(f"Генерация партии {i + 1}/{full_batches + 1}")
        df = generate_user_data(batch_size, country_codes)
        data_frames.append(df)

    # Генерируем оставшуюся партию, если есть
    if remainder > 0:
        logger.info(f"Генерация финальной партии {full_batches + 1}/{full_batches + 1} ({remainder} пользователей)")
        df = generate_user_data(remainder, country_codes)
        data_frames.append(df)

    # Объединяем все партии в один DataFrame
    if data_frames:
        return pd.concat(data_frames, ignore_index=True)
    else:
        return pd.DataFrame()


def validate_user_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Проверяет данные пользователей на корректность и возвращает отфильтрованные данные и список ошибок.

    Args:
        df: DataFrame с данными пользователей

    Returns:
        Кортеж из очищенного DataFrame и списка записей с ошибками
    """
    errors = []
    valid_data = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()
        error_found = False
        error_details = {'id': row_dict.get('id', 'unknown'), 'errors': []}

        # Проверка наличия необходимых полей
        required_fields = ['id', 'geo', 'apple_id', 'password', 'name']
        for field in required_fields:
            if field not in row_dict or not row_dict[field]:
                error_details['errors'].append(f"Отсутствует обязательное поле: {field}")
                error_found = True

        # Проверка формата email
        if 'apple_id' in row_dict and row_dict['apple_id'] and '@' not in row_dict['apple_id']:
            error_details['errors'].append("Некорректный формат email")
            error_found = True

        # Проверка длины пароля
        if 'password' in row_dict and row_dict['password'] and len(row_dict['password']) < 8:
            error_details['errors'].append("Пароль слишком короткий (менее 8 символов)")
            error_found = True

        # Добавляем запись в соответствующий список
        if error_found:
            errors.append(error_details)
        else:
            valid_data.append(row_dict)

    # Создаем DataFrame из корректных записей
    valid_df = pd.DataFrame(valid_data)

    return valid_df, errors

# Функции экспорта данных в различные форматы будут реализованы в clipboard_utils.py
