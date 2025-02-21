import random
import logging
import time
import re
from typing import Optional
import googlemaps
from config import GOOGLE_MAPS_API_KEY, CITY_COORDINATES, RADIUS_DATA, COUNTRY_NAMES
from utils import normalize_string, remove_country_from_address

# Инициализация клиента Google Maps
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


def generate_address(country_code: str) -> Optional[str]:
    """
    Генерирует адрес жилого здания в заданной стране с использованием Google Maps Places API.

    Функция запрашивает подробности места (Place Details) для получения структурированных
    компонентов адреса и формирует строку в формате:
      "улица номер дома, почтовый индекс город[, административная единица]".

    Обязательно должен присутствовать номер дома.

    Допустимые значения для параметра fields см. в документации:
    https://developers.google.com/maps/documentation/places/web-service/details#fields
    """
    query = "residential building"  # уточнённый запрос для поиска жилых домов
    locations = CITY_COORDINATES.get(country_code, [])
    if not locations:
        logging.error(f"Нет координат для страны: {country_code}")
        return None
    location = random.choice(locations)

    radius_info = RADIUS_DATA.get(country_code, {})
    if not radius_info:
        logging.error(f"Нет данных по радиусу для страны: {country_code}")
        return None

    radius = (radius_info.get("border")
              if location in radius_info.get("border_cities", [])
              else radius_info.get("default"))

    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            response = gmaps.places(query, location=location, radius=radius, language="en")
            logging.debug(f"Places response: {response}")
            if response.get("status") == "OK" and response.get("results"):
                place = random.choice(response["results"])
                place_id = place.get("place_id")
                # Передаём поля как кортеж
                details = gmaps.place(
                    place_id=place_id,
                    fields=("address_component", "formatted_address")
                )
                logging.debug(f"Place details: {details}")
                result = details.get("result", {})
                if not result:
                    formatted = place.get("formatted_address")
                    if formatted and re.search(r'\d+', formatted):
                        return normalize_string(formatted)
                    continue

                address_components = result.get("address_components", [])
                if not address_components:
                    continue

                # Извлекаем компоненты адреса
                street_number = next(
                    (comp["long_name"] for comp in address_components if "street_number" in comp.get("types", [])),
                    None,
                )
                route = next(
                    (comp["long_name"] for comp in address_components if "route" in comp.get("types", [])),
                    None,
                )
                postal_code = next(
                    (comp["long_name"] for comp in address_components if "postal_code" in comp.get("types", [])),
                    None,
                )
                locality = next(
                    (comp["long_name"] for comp in address_components if "locality" in comp.get("types", [])),
                    None,
                )
                administrative_area = next(
                    (comp["long_name"] for comp in address_components if
                     "administrative_area_level_1" in comp.get("types", [])),
                    None,
                )

                # Если номер дома отсутствует, считаем адрес недействительным
                if not street_number:
                    logging.info("Номер дома не найден в адресе, повторяем запрос...")
                    raise ValueError("Номер дома обязателен")

                # Если все ключевые компоненты получены, формируем адрес
                if route and street_number and postal_code and locality:
                    formatted_address = f"{route} {street_number}, {postal_code} {locality}"
                    if administrative_area:
                        formatted_address += f", {administrative_area}"
                    normalized = normalize_string(formatted_address)
                    if COUNTRY_NAMES.get(country_code) and COUNTRY_NAMES[country_code] in normalized:
                        return remove_country_from_address(normalized, COUNTRY_NAMES[country_code])
                    return normalized
                else:
                    # Фолбэк: если структурированные компоненты неполные, проверяем fallback-адрес
                    formatted_address = result.get("formatted_address")
                    if formatted_address and re.search(r'\d+', formatted_address):
                        return normalize_string(formatted_address)
        except googlemaps.exceptions.ApiError as e:
            logging.error(f"Google Maps API error: {e}")
        except Exception as e:
            logging.exception("Неожиданная ошибка при вызове Google Maps API")

        attempt += 1
        sleep_time = 2 ** attempt
        logging.info(f"Попытка {attempt}/{max_attempts} не удалась, повтор через {sleep_time} сек...")
        time.sleep(sleep_time)

    logging.error("Не удалось получить адрес с номером дома после нескольких попыток.")
    return None
