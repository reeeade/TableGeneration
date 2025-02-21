# data_generator.py
import random
import pandas as pd
from faker import Faker
from typing import List, Optional
from config import COUNTRY_LOCALES
from gmaps_api import generate_address
from utils import (
    generate_birth_date,
    generate_strong_compliant_password,
    generate_correct_proxy,
    normalize_string,
)
from models import User
from dataclasses import asdict
import logging

# Инициализация объектов Faker для каждой локали
faker_objects = {code: Faker(locale) for code, locale in COUNTRY_LOCALES.items()}


def generate_name(country_code: str) -> str:
    """
    Генерирует полное имя пользователя для заданного кода страны.
    """
    faker = faker_objects.get(country_code, Faker())
    while True:
        first_name = faker.first_name()
        last_name = faker.last_name()
        full_name = f"{first_name} {last_name}"
        normalized_name = normalize_string(full_name)
        if len(normalized_name.split()) == 2 and normalized_name.isascii():
            return normalized_name


def generate_user_data(num_users: int = 20, country_codes: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Генерирует DataFrame с пользовательскими данными.
    """
    if country_codes is None:
        country_codes = list(COUNTRY_LOCALES.keys())

    def create_user_record() -> dict:
        max_attempts = 10
        attempts = 0
        country = random.choice(country_codes)
        while attempts < max_attempts:
            address = generate_address(country)
            if address:
                # Генерируем остальные данные
                birth_date = generate_birth_date()
                name = generate_name(country)
                password = generate_strong_compliant_password()
                proxy = generate_correct_proxy(country)
                user = User(
                    geo=country,
                    apple_id="",
                    password=password,
                    number="",
                    name=name,
                    address=address,
                    birthday=birth_date,
                    creation="",
                    proxy=proxy,
                )
                return asdict(user)
            attempts += 1
            logging.info(f"Не удалось получить адрес для страны {country} (попытка {attempts}/{max_attempts}).")
        # Если за max_attempts адрес не получен, возвращаем запись с пустым адресом
        logging.warning(
            f"Не удалось получить адрес для страны {country} после {max_attempts} попыток. Запись будет создана с пустым адресом.")
        birth_date = generate_birth_date()
        name = generate_name(country)
        password = generate_strong_compliant_password()
        proxy = generate_correct_proxy(country)
        user = User(
            geo=country,
            apple_id="",
            password=password,
            number="",
            name=name,
            address="",
            birthday=birth_date,
            creation="",
            proxy=proxy,
        )
        return asdict(user)

    data = [create_user_record() for _ in range(num_users)]
    return pd.DataFrame(data)
