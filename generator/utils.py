# utils.py
import string
import secrets
import random
from datetime import datetime, timedelta
from typing import Optional
from unidecode import unidecode


def generate_strong_compliant_password(length: int = 16) -> Optional[str]:
    """
    Генерирует надежный пароль заданной длины, содержащий:
      - хотя бы одну заглавную букву,
      - одну строчную букву,
      - одну цифру,
      - один специальный символ.
    Первый символ должен быть буквенно-цифровым, и подряд не должно идти повторяющихся символов.
    """
    if length < 4:
        raise ValueError("Длина пароля должна быть не менее 4 символов.")

    sys_random = secrets.SystemRandom()

    while True:
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice(string.punctuation),
        ]
        remaining_length = length - 4
        all_chars = string.ascii_letters + string.digits + string.punctuation
        password.extend(secrets.choice(all_chars) for _ in range(remaining_length))

        sys_random.shuffle(password)

        # Проверка: первый символ должен быть буквенно-цифровым
        if not password[0].isalnum():
            for i in range(1, length):
                if password[i].isalnum():
                    password[0], password[i] = password[i], password[0]
                    break
            else:
                continue

        # Проверка: нет двух подряд одинаковых символов
        if not any(password[i] == password[i + 1] for i in range(len(password) - 1)):
            return "".join(password)


def generate_birth_date(min_age: int = 25, max_age: int = 35) -> str:
    """
    Генерирует случайную дату рождения с указанным диапазоном возраста.
    """
    today = datetime.today()
    start_date = today - timedelta(days=365 * max_age)
    end_date = today - timedelta(days=365 * min_age)
    delta_days = (end_date - start_date).days
    random_days = random.randint(0, delta_days)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%d.%m.%Y")


def generate_correct_proxy(geo_code: str, port_range: tuple = (100, 199)) -> str:
    """
    Генерирует корректный прокси-адрес с использованием случайного порта из заданного диапазона.
    """
    port = random.randint(*port_range)
    return f"socks5://xxfyOfwK90p50KT0:wifi;{geo_code.lower()};;;@proxy.froxy.com:9{port}"


def normalize_string(input_str: str) -> str:
    """
    Преобразует строку, заменяя специальные символы на их ASCII-эквиваленты.
    """
    return unidecode(input_str)


def remove_country_from_address(address: str, country_name: str) -> str:
    """
    Удаляет из конца адреса название страны (если присутствует).
    """
    suffix = f", {country_name}"
    if address.endswith(suffix):
        return address[:-len(suffix)]
    return address
