# gmaps_api.py
import random
import logging
import time
import re
import json
import os
from typing import Optional, Dict, List, Any
import googlemaps
from functools import lru_cache
from config import (
    GOOGLE_MAPS_API_KEY,
    CITY_COORDINATES,
    RADIUS_DATA,
    COUNTRY_NAMES,
    GMAPS_CONFIG
)
from utils import (
    normalize_string,
    remove_country_from_address,
    is_valid_address,
    format_address_components
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация клиента Google Maps
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Путь к файлу кэша адресов
CACHE_FILE = "address_cache.json"

# Инициализация кэша адресов
address_cache = {}

USED_ADDRESSES = set()


def reset_used_addresses(func):
    """
    Декоратор для автоматической очистки USED_ADDRESSES
    перед вызовом функции генерации данных
    """

    def wrapper(*args, **kwargs):
        global USED_ADDRESSES
        USED_ADDRESSES.clear()
        logger.info("Список использованных адресов очищен перед генерацией")
        return func(*args, **kwargs)

    return wrapper


def load_address_cache():
    """Загружает кэш адресов из файла."""
    global address_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                address_cache = json.load(f)
            logger.info(f"Загружен кэш адресов: {len(address_cache)} записей")
        except Exception as e:
            logger.error(f"Ошибка при загрузке кэша адресов: {e}")
            address_cache = {}
    else:
        address_cache = {}


def save_address_cache():
    """Сохраняет кэш адресов в файл."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(address_cache, f, ensure_ascii=False, indent=2)
        logger.info(f"Кэш адресов сохранен: {len(address_cache)} записей")
    except Exception as e:
        logger.error(f"Ошибка при сохранении кэша адресов: {e}")


# Загружаем кэш при импорте модуля
load_address_cache()


def get_cached_address(country_code: str) -> Optional[str]:
    """
    Получает случайный адрес из кэша для указанной страны.

    Args:
        country_code: Код страны

    Returns:
        Адрес из кэша или None, если кэш пуст для данной страны
    """
    country_addresses = address_cache.get(country_code, [])
    if country_addresses:
        return random.choice(country_addresses)
    return None


def add_to_cache(country_code: str, address: str):
    """
    Добавляет адрес в кэш для указанной страны.

    Args:
        country_code: Код страны
        address: Адрес для добавления в кэш
    """
    if country_code not in address_cache:
        address_cache[country_code] = []

    # Добавляем только если адрес уникален
    if address not in address_cache[country_code]:
        address_cache[country_code].append(address)

        # Если кэш превышает 1000 адресов для страны, удаляем старые записи
        if len(address_cache[country_code]) > 1000:
            address_cache[country_code] = address_cache[country_code][-1000:]

        # Сохраняем кэш каждые 10 новых адресов
        if sum(len(addresses) for addresses in address_cache.values()) % 10 == 0:
            save_address_cache()


@lru_cache(maxsize=128)
def get_nearby_places(location: str, radius: int, query: str = "residential building") -> List[Dict[str, Any]]:
    """
    Получает список мест рядом с указанной локацией.
    Результаты кэшируются для повторного использования.

    Args:
        location: Координаты локации в формате "lat,lng"
        radius: Радиус поиска в метрах
        query: Запрос для поиска

    Returns:
        Список мест
    """
    try:
        response = gmaps.places(
            query,
            location=location,
            radius=radius,
            language=GMAPS_CONFIG['language']
        )

        if response.get("status") == "OK" and response.get("results"):
            return response["results"]
        else:
            logger.warning(f"Нет результатов для запроса: {query} в локации {location}")
            return []

    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Maps API error: {e}")
        return []
    except Exception as e:
        logger.exception(f"Неожиданная ошибка при вызове Google Maps API: {e}")
        return []


def get_place_details(place_id: str) -> Dict[str, Any]:
    """
    Получает подробности о месте по его ID.

    Args:
        place_id: ID места

    Returns:
        Словарь с подробностями о месте
    """
    try:
        details = gmaps.place(
            place_id=place_id,
            fields=("address_component", "formatted_address")
        )
        return details.get("result", {})
    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Maps API error при получении деталей места: {e}")
        return {}
    except Exception as e:
        logger.exception(f"Неожиданная ошибка при получении деталей места: {e}")
        return {}


def extract_address_components(address_components: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Извлекает компоненты адреса из ответа API.

    Args:
        address_components: Список компонентов адреса

    Returns:
        Словарь с компонентами адреса
    """
    components = {}

    for comp in address_components:
        types = comp.get("types", [])

        # Маппинг типов компонентов адреса
        component_mapping = {
            "street_number": "street_number",
            "route": "route",
            "postal_code": "postal_code",
            "locality": "locality",
            "administrative_area_level_1": "administrative_area_level_1",
            "country": "country"
        }

        for type_key, comp_key in component_mapping.items():
            if type_key in types:
                components[comp_key] = comp["long_name"]

    return components


def generate_address(country_code: str) -> Optional[str]:
    """
    Генерирует уникальный адрес жилого здания в заданной стране.
    """
    # Максимальное количество попыток генерации уникального адреса
    max_unique_attempts = 10

    for _ in range(max_unique_attempts):
        # Пробуем получить адрес из кэша (с вероятностью 70%)
        if random.random() < 0.7:
            cached_address = get_cached_address(country_code)
            if cached_address and cached_address not in USED_ADDRESSES:
                logger.info(f"Использован кэшированный адрес для страны {country_code}")
                USED_ADDRESSES.add(cached_address)
                return cached_address

        # Если не получили уникальный адрес из кэша, генерируем новый
        logger.info(f"Генерация нового адреса для страны {country_code}")

        # Получаем координаты для заданной страны
        locations = CITY_COORDINATES.get(country_code, [])
        if not locations:
            logger.error(f"Нет координат для страны: {country_code}")
            return None

        # Выбираем случайную локацию
        location = random.choice(locations)

        # Получаем информацию о радиусе поиска
        radius_info = RADIUS_DATA.get(country_code, {})
        if not radius_info:
            logger.error(f"Нет данных по радиусу для страны: {country_code}")
            return None

        # Определяем радиус поиска в зависимости от локации
        radius = (radius_info.get("border")
                  if location in radius_info.get("border_cities", [])
                  else radius_info.get("default"))

        # Максимальное количество попыток получения адреса
        max_attempts = GMAPS_CONFIG['max_retries']
        attempt = 0

        while attempt < max_attempts:
            try:
                # Получаем список мест поблизости
                places = get_nearby_places(location, radius)

                if not places:
                    logger.warning(f"Нет подходящих мест для локации {location}")
                    attempt += 1
                    continue

                # Выбираем случайное место
                place = random.choice(places)
                place_id = place.get("place_id")

                # Получаем подробности о месте
                details = get_place_details(place_id)

                # Если не получили детали, пробуем использовать форматированный адрес из результатов поиска
                if not details:
                    formatted = place.get("formatted_address")
                    if formatted and re.search(r'\d+', formatted):
                        address = normalize_string(formatted)
                        if is_valid_address(address) and address not in USED_ADDRESSES:
                            # Удаляем название страны, если оно присутствует
                            if COUNTRY_NAMES.get(country_code) and COUNTRY_NAMES[country_code] in address:
                                address = remove_country_from_address(address, COUNTRY_NAMES[country_code])

                            # Добавляем в кэш, список использованных и возвращаем
                            add_to_cache(country_code, address)
                            USED_ADDRESSES.add(address)
                            return address
                    attempt += 1
                    continue

                # Извлекаем компоненты адреса
                address_components = details.get("address_components", [])
                if not address_components:
                    attempt += 1
                    continue

                # Извлекаем компоненты адреса
                components = extract_address_components(address_components)

                # Проверяем наличие необходимых компонентов
                required_components = GMAPS_CONFIG['required_components']
                if not all(comp in components for comp in required_components):
                    # Если номер дома отсутствует, считаем адрес недействительным
                    if 'street_number' not in components:
                        logger.info("Номер дома не найден в адресе, повторяем запрос...")
                        attempt += 1
                        continue

                # Форматируем адрес
                formatted_address = format_address_components(components)

                # Если не удалось сформировать адрес, пробуем использовать форматированный адрес из API
                if not formatted_address:
                    formatted_address = details.get("formatted_address")
                    if not formatted_address or not re.search(r'\d+', formatted_address):
                        attempt += 1
                        continue

                # Нормализуем адрес
                normalized = normalize_string(formatted_address)

                # Удаляем название страны, если оно присутствует
                if COUNTRY_NAMES.get(country_code) and COUNTRY_NAMES[country_code] in normalized:
                    normalized = remove_country_from_address(normalized, COUNTRY_NAMES[country_code])

                # Проверяем валидность и уникальность адреса
                if is_valid_address(normalized) and normalized not in USED_ADDRESSES:
                    # Добавляем в кэш, список использованных и возвращаем
                    add_to_cache(country_code, normalized)
                    USED_ADDRESSES.add(normalized)
                    return normalized

            except googlemaps.exceptions.ApiError as e:
                logger.error(f"Google Maps API error: {e}")
            except Exception as e:
                logger.exception("Неожиданная ошибка при вызове Google Maps API")

            # Увеличиваем счетчик попыток и ждем перед повторным запросом
            attempt += 1
            if attempt < max_attempts:
                sleep_time = GMAPS_CONFIG['retry_base_delay'] ** attempt
                logger.info(f"Попытка {attempt}/{max_attempts} не удалась, повтор через {sleep_time} сек...")
                time.sleep(sleep_time)

        logger.error(
            f"Не удалось получить уникальный адрес для страны {country_code} после {max_unique_attempts} попыток.")

    return None


def batch_generate_addresses(country_code: str, count: int = 10) -> List[str]:
    """
    Генерирует несколько адресов для указанной страны.
    Полезно для предварительного заполнения кэша.

    Args:
        country_code: Код страны
        count: Количество адресов для генерации

    Returns:
        Список сгенерированных адресов
    """
    logger.info(f"Генерация {count} адресов для страны {country_code}")
    addresses = []

    for i in range(count):
        address = generate_address(country_code)
        if address:
            addresses.append(address)
            logger.info(f"Сгенерирован адрес {i + 1}/{count} для страны {country_code}")
        else:
            logger.warning(f"Не удалось сгенерировать адрес {i + 1}/{count} для страны {country_code}")

    return addresses


def prefill_address_cache(country_codes: List[str], addresses_per_country: int = 5):
    """
    Предварительно заполняет кэш адресов для указанных стран.

    Args:
        country_codes: Список кодов стран
        addresses_per_country: Количество адресов для генерации для каждой страны
    """
    logger.info(f"Предварительное заполнение кэша адресов для стран: {', '.join(country_codes)}")

    for country_code in country_codes:
        batch_generate_addresses(country_code, addresses_per_country)

    # Сохраняем кэш
    save_address_cache()
    logger.info("Предварительное заполнение кэша адресов завершено")
