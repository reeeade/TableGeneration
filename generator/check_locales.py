from faker import Faker
import pprint

# Создаем основной экземпляр Faker
faker = Faker()

print("Проверка доступных локалей в Faker:")
print("-" * 50)

# Альтернативный способ получения локалей
test_all_locales = [
    'en_US', 'en_GB', 'en_CA', 'en_AU', 'en_NZ', 'en_IN',
    'fr_FR', 'fr_CA', 'de_DE', 'it_IT', 'es_ES', 'es_MX',
    'pt_BR', 'pt_PT', 'nl_NL', 'da_DK', 'no_NO', 'sv_SE',
    'fi_FI', 'ru_RU', 'uk_UA', 'pl_PL', 'cs_CZ', 'sk_SK',
    'hu_HU', 'ro_RO', 'bg_BG', 'tr_TR', 'el_GR', 'he_IL',
    'ar_SA', 'ar_EG', 'ja_JP', 'ko_KR', 'zh_CN', 'zh_TW',
    'th_TH', 'id_ID', 'hi_IN'
]

working_locales = []
for locale in test_all_locales:
    try:
        f = Faker(locale)
        name = f.name()  # Проверяем, что локаль работает
        working_locales.append(locale)
        print(f"- {locale}: Работает (пример: {name})")
    except Exception as e:
        print(f"- {locale}: Не работает ({str(e)})")

# Получаем список стран с кодами
print("\nПримеры стран и их кодов из Faker:")
print("-" * 50)
countries_and_codes = set()
for _ in range(30):  # Собираем 30 примеров для разнообразия
    country = faker.country()
    code = faker.country_code()
    countries_and_codes.add((country, code))

for country, code in sorted(countries_and_codes):
    print(f"- {country}: {code}")

# Дополнительно: Установите pycountry для получения полного списка стран
try:
    import pycountry
    print("\nПолный список стран с кодами (из pycountry):")
    print("-" * 50)
    for country in sorted(list(pycountry.countries), key=lambda x: x.name):
        print(f"- {country.name}: {country.alpha_2}")
except ImportError:
    print("\nБиблиотека pycountry не установлена.")
    print("Для получения полного списка стран установите: pip install pycountry")