# models.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """
    Модель данных пользователя.

    Attributes:
        id: Уникальный идентификатор пользователя (UUID)
        geo: Код страны (ISO 3166-1 alpha-2)
        apple_id: Email, используемый в качестве Apple ID
        password: Пароль для аккаунта
        number: Номер телефона в международном формате
        name: Полное имя пользователя
        address: Адрес пользователя
        birthday: Дата рождения в формате DD.MM.YYYY
        creation: Дата создания аккаунта в формате DD.MM.YYYY
        proxy: Строка с настройками прокси
    """
    geo: str  # Оставляем гео-код
    apple_id: str
    password: str
    number: str
    name: str
    address: str
    birthday: str
    # Убираем лишние поля: id, number, proxy, creation и т.д.


@dataclass
class UserProfile:
    """
    Расширенная модель профиля пользователя с дополнительными полями.

    Attributes:
        user_id: Ссылка на основную модель User
        language: Предпочитаемый язык
        currency: Предпочитаемая валюта
        time_zone: Часовой пояс
        payment_method: Предпочитаемый способ оплаты
        notification_settings: Настройки уведомлений (JSON строка)
        device_info: Информация об устройстве (JSON строка)
    """
    user_id: str
    language: str
    currency: str
    time_zone: str
    payment_method: Optional[str] = None
    notification_settings: Optional[str] = None
    device_info: Optional[str] = None


@dataclass
class PaymentMethod:
    """
    Модель для хранения данных платежного метода.

    Attributes:
        user_id: Ссылка на модель User
        method_type: Тип платежного метода (card, paypal, etc.)
        card_type: Тип карты (visa, mastercard, etc.)
        last_digits: Последние 4 цифры карты
        expiry_date: Дата истечения срока действия
        billing_address: Адрес для выставления счетов
        is_default: Является ли метод оплаты по умолчанию
    """
    user_id: str
    method_type: str
    card_type: Optional[str] = None
    last_digits: Optional[str] = None
    expiry_date: Optional[str] = None
    billing_address: Optional[str] = None
    is_default: bool = False


@dataclass
class DeviceInfo:
    """
    Модель для хранения информации об устройстве пользователя.

    Attributes:
        user_id: Ссылка на модель User
        device_type: Тип устройства (mobile, tablet, desktop)
        os: Операционная система
        os_version: Версия операционной системы
        model: Модель устройства
        browser: Браузер
        browser_version: Версия браузера
        ip_address: IP-адрес
        user_agent: User-Agent
    """
    user_id: str
    device_type: str
    os: str
    os_version: str
    model: Optional[str] = None
    browser: Optional[str] = None
    browser_version: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
