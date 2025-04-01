# utils.py
import string
import secrets
import random
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from unidecode import unidecode
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import USER_GEN_CONFIG


def generate_strong_compliant_password(length: int = None) -> str:
    """
    Генерирует надежный пароль заданной длины, содержащий:
      - хотя бы одну заглавную букву,
      - хотя бы одну строчную букву,
      - хотя бы одну цифру,
      - хотя бы один специальный символ.

    Первый символ должен быть буквенно-цифровым, и подряд не должно идти повторяющихся символов.
    Также проверяется отсутствие слишком очевидных шаблонов и последовательностей.
    """
    if length is None:
        length = USER_GEN_CONFIG['password_length']

    if length < 8:
        raise ValueError("Длина пароля должна быть не менее 8 символов для соответствия требованиям безопасности.")

    # Набор символов для разных категорий
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"

    # Исключаем легко путаемые символы
    uppercase = uppercase.replace('O', '').replace('I', '').replace('Q', '')
    lowercase = lowercase.replace('l', '').replace('i', '').replace('o', '')
    digits = digits.replace('0', '').replace('1', '')
    special = special.replace('|', '').replace('I', '').replace('l', '')

    # Потенциальные последовательности, которые надо избегать
    sequences = [
        'qwer', 'asdf', 'zxcv', 'wasd', '1234', '2345', '3456', '4567',
        'abcd', 'wxyz', 'aeiou', 'password', 'admin', 'user', 'login'
    ]

    # Системный рандом для криптографической безопасности
    sys_random = secrets.SystemRandom()

    attempt_count = 0
    max_attempts = 10

    while attempt_count < max_attempts:
        attempt_count += 1

        # Гарантированно включаем по одному символу каждой категории
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special),
        ]

        # Дополняем оставшимися символами
        remaining_length = length - 4
        all_chars = uppercase + lowercase + digits + special
        password.extend(secrets.choice(all_chars) for _ in range(remaining_length))

        # Перемешиваем пароль
        sys_random.shuffle(password)

        # Убеждаемся, что первый символ буквенно-цифровой
        if not password[0].isalnum():
            for i in range(1, length):
                if password[i].isalnum():
                    password[0], password[i] = password[i], password[0]
                    break
            else:
                continue  # Если не нашли буквенно-цифровой символ, генерируем пароль заново

        # Убеждаемся, что нет повторяющихся символов подряд
        has_repeats = False
        for i in range(len(password) - 1):
            if password[i] == password[i + 1]:
                has_repeats = True
                break

        if has_repeats:
            continue  # Если есть повторы, генерируем пароль заново

        # Проверяем на наличие известных последовательностей
        password_str = ''.join(password).lower()
        has_sequence = False
        for seq in sequences:
            if seq in password_str:
                has_sequence = True
                break

        if has_sequence:
            continue  # Если есть последовательности, генерируем пароль заново

        # Если все проверки пройдены, возвращаем пароль
        return ''.join(password)

    # Если после max_attempts пароль все еще не был сгенерирован, используем базовый вариант
    logging.warning(
        "Не удалось сгенерировать оптимальный пароль за максимальное число попыток. Использую базовый вариант.")
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    sys_random.shuffle(password)
    return ''.join(password)


def generate_birth_date(min_age: int = None, max_age: int = None) -> str:
    """
    Генерирует случайную дату рождения в заданном диапазоне возраста.
    Возвращает строку в формате DD.MM.YYYY.
    """
    if min_age is None:
        min_age = USER_GEN_CONFIG['min_age']
    if max_age is None:
        max_age = USER_GEN_CONFIG['max_age']

    if min_age >= max_age:
        raise ValueError("Минимальный возраст должен быть меньше максимального.")

    today = datetime.today()
    start_date = today - timedelta(days=365.25 * max_age)  # Учитываем високосные годы
    end_date = today - timedelta(days=365.25 * min_age)

    delta_days = (end_date - start_date).days
    random_days = random.randint(0, delta_days)
    random_date = start_date + timedelta(days=random_days)

    # Проверка на наличие будущих дат (из-за високосных лет)
    if random_date > today:
        random_date = today - timedelta(days=365.25 * min_age)

    return random_date.strftime("%d.%m.%Y")


def generate_correct_proxy(geo_code: str, port_range: Tuple[int, int] = None) -> str:
    """
    Генерирует корректный прокси-адрес с использованием случайного порта из заданного диапазона.

    Args:
        geo_code: Код страны (например, 'us', 'gb', и т.д.)
        port_range: Кортеж с минимальным и максимальным значением порта

    Returns:
        Строка с адресом прокси
    """
    if port_range is None:
        port_range = USER_GEN_CONFIG['proxy_port_range']

    port = random.randint(*port_range)
    auth_token = generate_proxy_auth_token()

    return f"socks5://{auth_token}:wifi;{geo_code.lower()};;;@proxy.froxy.com:9{port}"


def generate_proxy_auth_token(length: int = 12) -> str:
    """
    Генерирует случайный токен для аутентификации на прокси.
    """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def normalize_string(input_str: str) -> str:
    """
    Преобразует строку, заменяя специальные символы на их ASCII-эквиваленты
    и удаляя лишние пробелы.
    """
    if not input_str:
        return ""

    # Транслитерация не-ASCII символов
    ascii_str = unidecode(input_str)

    # Замена множественных пробелов на один
    normalized = re.sub(r'\s+', ' ', ascii_str)

    # Удаление начальных и конечных пробелов
    return normalized.strip()


def remove_country_from_address(address: str, country_name: str) -> str:
    """
    Удаляет из конца адреса название страны (если присутствует).
    Работает с разными форматами записи названия страны.
    """
    if not address or not country_name:
        return address

    # Нормализуем адрес и название страны
    address = normalize_string(address)
    country_name = normalize_string(country_name)

    # Регулярное выражение для поиска страны в конце адреса с разными разделителями
    # паттерн 1: ", Country"
    # паттерн 2: " Country"
    patterns = [
        f',\\s*{re.escape(country_name)}\\s*,',
        f'\\s+{re.escape(country_name)}\\s*,'
    ]

    # Применяем каждый паттерн
    for pattern in patterns:
        address = re.sub(pattern, '', address, flags=re.IGNORECASE)

    return address.strip()


def is_valid_address(address: str) -> bool:
    """
    Проверяет, является ли адрес действительным.
    Адрес считается действительным, если он содержит как минимум:
    - Название улицы
    - Номер дома/здания
    - Почтовый индекс или город
    """
    if not address:
        return False

    # Проверка на наличие цифр (скорее всего номер дома или почтовый индекс)
    has_numbers = bool(re.search(r'\d', address))

    # Проверка на наличие буквенных символов (название улицы или города)
    has_letters = bool(re.search(r'[a-zA-Z]', address))

    # Проверка наличия хотя бы одной запятой (разделитель между улицей и городом/индексом)
    has_separator = ',' in address

    # Проверка минимальной длины адреса
    min_length = len(address) > 10

    return has_numbers and has_letters and has_separator and min_length


def format_address_components(components: dict) -> str:
    """
    Форматирует компоненты адреса в строку адреса.

    Args:
        components: Словарь с компонентами адреса

    Returns:
        Отформатированная строка адреса
    """
    street = components.get('route', '')
    number = components.get('street_number', '')
    postal = components.get('postal_code', '')
    city = components.get('locality', '')
    area = components.get('administrative_area_level_1', '')

    address_parts = []

    # Улица и номер дома
    if street and number:
        address_parts.append(f"{street} {number}")
    elif street:
        address_parts.append(street)

    # Почтовый индекс и город
    if postal and city:
        address_parts.append(f"{postal} {city}")
    elif postal:
        address_parts.append(postal)
    elif city:
        address_parts.append(city)

    # Административная единица (если есть)
    if area:
        address_parts.append(area)

    return ", ".join(address_parts)


async def run_concurrent_tasks(tasks, max_workers=10):
    """
    Запускает задачи параллельно с использованием ThreadPoolExecutor.

    Args:
        tasks: Список функций для выполнения
        max_workers: Максимальное количество параллельных рабочих потоков

    Returns:
        Список результатов выполнения задач
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(executor, task) for task in tasks]
        return await asyncio.gather(*futures)


def generate_email(name: str, domain: str = None) -> str:
    """
    Генерирует email на основе имени пользователя.

    Args:
        name: Имя пользователя (например, "John Doe")
        domain: Домен для email (если None, выбирается случайно)

    Returns:
        Сгенерированный email
    """
    if domain is None:
        domains = ["gmail.com", "outlook.com", "yahoo.com", "protonmail.com",
                   "icloud.com", "mail.com", "zoho.com", "aol.com"]
        domain = random.choice(domains)

    # Очищаем и нормализуем имя
    name = normalize_string(name.lower())
    name_parts = name.split()

    if len(name_parts) >= 2:
        # Варианты форматирования email
        formats = [
            f"{name_parts[0]}.{name_parts[-1]}@{domain}",
            f"{name_parts[0]}{name_parts[-1]}@{domain}",
            f"{name_parts[0]}{name_parts[-1][0]}@{domain}",
            f"{name_parts[0][0]}{name_parts[-1]}@{domain}",
            f"{name_parts[-1]}.{name_parts[0]}@{domain}"
        ]
        email = random.choice(formats)
    else:
        # Если имя состоит только из одной части
        email = f"{name_parts[0]}{random.randint(1, 999)}@{domain}"

    return email.lower()


def generate_phone_number(country_code: str) -> str:
    """
    Генерирует телефонный номер для указанной страны.

    Args:
        country_code: Код страны (например, 'US', 'GB', и т.д.)

    Returns:
        Строка с телефонным номером в международном формате
    """
    # Словарь кодов стран и форматов номеров
    country_phone_formats = {
        'US': '+1{}{}{}{}{}{}{}{}{}{} формат +1XXXXXXXXXX',
        'CA': '+1{}{}{}{}{}{}{}{}{}{} формат +1XXXXXXXXXX',
        'GB': '+44{}{}{}{}{}{}{}{}{} формат +44XXXXXXXXX',
        'DE': '+49{}{}{}{}{}{}{}{}{} формат +49XXXXXXXXX',
        'FR': '+33{}{}{}{}{}{}{}{}{} формат +33XXXXXXXXX',
        'IT': '+39{}{}{}{}{}{}{}{}{}{} формат +39XXXXXXXXXX',
        'ES': '+34{}{}{}{}{}{}{}{}{} формат +34XXXXXXXXX',
        'JP': '+81{}{}{}{}{}{}{}{}{}{} формат +81XXXXXXXXXX',
        'AU': '+61{}{}{}{}{}{}{}{}{} формат +61XXXXXXXXX',
        'CN': '+86{}{}{}{}{}{}{}{}{}{}{} формат +86XXXXXXXXXXX',
        'IN': '+91{}{}{}{}{}{}{}{}{}{} формат +91XXXXXXXXXX',
        'RU': '+7{}{}{}{}{}{}{}{}{}{} формат +7XXXXXXXXXX',
        'BR': '+55{}{}{}{}{}{}{}{}{}{}{} формат +55XXXXXXXXXXX',
        'KR': '+82{}{}{}{}{}{}{}{}{}{} формат +82XXXXXXXXXX',
    }

    # Значение по умолчанию, если код страны не найден
    default_format = '+1{}{}{}{}{}{}{}{}{}{} формат +1XXXXXXXXXX'

    # Получаем формат для указанной страны или используем значение по умолчанию
    phone_format = country_phone_formats.get(country_code, default_format)

    # Заменяем каждый {} случайной цифрой
    digits = [str(random.randint(0, 9)) for _ in range(phone_format.count("{}"))]

    # Форматируем номер телефона
    formatted_phone = phone_format.format(*digits)

    # Возвращаем только номер без дополнительной информации о формате
    return formatted_phone.split(' формат ')[0]