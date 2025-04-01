# data_generator.py
import random
import pandas as pd
import asyncio
from faker import Faker
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
import uuid

from config import COUNTRY_LOCALES, USER_GEN_CONFIG
from gmaps_api import generate_address
from utils import (
    generate_birth_date,
    generate_strong_compliant_password,
    generate_correct_proxy,
    normalize_string,
    generate_email,
    generate_phone_number,
    run_concurrent_tasks
)
from models import User
from dataclasses import asdict

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация объектов Faker для каждой локали
faker_objects = {code: Faker(locale) for code, locale in COUNTRY_LOCALES.items()}
# Добавляем запасной Faker для случаев, когда локаль не найдена
faker_objects['default'] = Faker()


def generate_name(country_code: str) -> str:
    """
    Генерирует полное имя пользователя для заданного кода страны.

    Args:
        country_code: Код страны

    Returns:
        Нормализованное полное имя
    """
    faker = faker_objects.get(country_code, faker_objects['default'])

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
    first_name = faker_objects['default'].first_name()
    last_name = faker_objects['default'].last_name()
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
                # Генерируем остальные данные
                name = generate_name(country)
                email = generate_email(name)
                birth_date = generate_birth_date()
                password = generate_strong_compliant_password()
                proxy = generate_correct_proxy(country)
                phone = generate_phone_number(country)
                creation_date = generate_creation_date()

                user = User(
                    id=str(uuid.uuid4()),
                    geo=country,
                    apple_id=email,
                    password=password,
                    number=phone,
                    name=name,
                    address=address,
                    birthday=birth_date,
                    creation=creation_date,
                    proxy=proxy,
                )
                return asdict(user)

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
    name = generate_name(country)
    email = generate_email(name)
    birth_date = generate_birth_date()
    password = generate_strong_compliant_password()
    proxy = generate_correct_proxy(country)
    phone = generate_phone_number(country)
    creation_date = generate_creation_date()

    user = User(
        id=str(uuid.uuid4()),
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
    return asdict(user)


async def generate_user_data_async(num_users: int = 20, country_codes: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Асинхронно генерирует DataFrame с пользовательскими данными.

    Args:
        num_users: Количество пользователей для генерации
        country_codes: Список кодов стран. Если None, используются все доступные страны.

    Returns:
        DataFrame с данными пользователей
    """
    if country_codes is None:
        country_codes = list(COUNTRY_LOCALES.keys())

    # Распределяем пользователей по странам
    countries = random.choices(country_codes, k=num_users)

    # Создаем задачи для асинхронного выполнения
    tasks = [create_user_record(country) for country in countries]

    # Запускаем задачи с ограничением на количество одновременных задач
    max_workers = min(20, num_users)  # Максимум 20 одновременных задач

    logger.info(f"Генерация данных для {num_users} пользователей из стран: {', '.join(set(countries))}")

    # Используем семафор для ограничения одновременных задач
    semaphore = asyncio.Semaphore(max_workers)

    async def limited_task(country):
        async with semaphore:
            return await create_user_record(country)

    # Запускаем задачи с ограничением
    data = await asyncio.gather(*[limited_task(country) for country in countries])

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
            'id', 'geo', 'apple_id', 'password', 'number', 'name', 'address', 'birthday', 'creation', 'proxy'
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