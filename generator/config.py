import os
from dotenv import load_dotenv

load_dotenv()

# Получение API-ключа Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY не установлен в переменных окружения.")

# Словарь локализации по странам, добавлены новые страны
COUNTRY_LOCALES = {
    'ES': 'es_ES',  # Испания
    'DE': 'de_DE',  # Германия
    'FR': 'fr_FR',  # Франция
    'GB': 'en_GB',  # Великобритания
    'PL': 'pl_PL',  # Польша
    'NL': 'nl_NL',  # Нидерланды
    'AT': 'de_AT',  # Австрия
    'DK': 'da_DK',  # Дания
    'UA': 'uk_UA',  # Украина
    'RO': 'ro_RO',  # Румыния
    'EE': 'et_EE',  # Эстония
    'LV': 'lv_LV',  # Латвия
    'LT': 'lt_LT',  # Литва
    'BG': 'bg_BG',  # Болгария
    'GE': 'ka_GE',  # Грузия
    'FI': 'fi_FI',  # Финляндия
    'CZ': 'cs_CZ',  # Чехия
    'IT': 'it_IT',  # Италия
    # Новые страны
    'US': 'en_US',  # США
    'CA': 'en_CA',  # Канада
    'AU': 'en_AU',  # Австралия
    'NZ': 'en_NZ',  # Новая Зеландия
    'JP': 'ja_JP',  # Япония
    'KR': 'ko_KR',  # Южная Корея
    'CN': 'zh_CN',  # Китай
    'IN': 'hi_IN',  # Индия
    'BR': 'pt_BR',  # Бразилия
    'MX': 'es_MX',  # Мексика
    'AE': 'ar_AE',  # ОАЭ
    'ZA': 'en_ZA',  # ЮАР
    'SE': 'sv_SE',  # Швеция
    'NO': 'nb_NO',  # Норвегия
    'IE': 'en_IE',  # Ирландия
    'CH': 'de_CH',  # Швейцария
    'PT': 'pt_PT',  # Португалия
    'GR': 'el_GR',  # Греция
    'IL': 'he_IL',  # Израиль
    'SG': 'en_SG',  # Сингапур
}

# Сопоставление кода страны с названием страны (добавлены новые страны)
COUNTRY_NAMES = {
    'ES': 'Spain',
    'DE': 'Germany',
    'FR': 'France',
    'GB': 'United Kingdom',
    'PL': 'Poland',
    'NL': 'Netherlands',
    'AT': 'Austria',
    'DK': 'Denmark',
    'UA': 'Ukraine',
    'RO': 'Romania',
    'EE': 'Estonia',
    'LV': 'Latvia',
    'LT': 'Lithuania',
    'BG': 'Bulgaria',
    'GE': 'Georgia',
    'FI': 'Finland',
    'CZ': 'Czech Republic',
    'IT': 'Italy',
    # Новые страны
    'US': 'United States',
    'CA': 'Canada',
    'AU': 'Australia',
    'NZ': 'New Zealand',
    'JP': 'Japan',
    'KR': 'South Korea',
    'CN': 'China',
    'IN': 'India',
    'BR': 'Brazil',
    'MX': 'Mexico',
    'AE': 'United Arab Emirates',
    'ZA': 'South Africa',
    'SE': 'Sweden',
    'NO': 'Norway',
    'IE': 'Ireland',
    'CH': 'Switzerland',
    'PT': 'Portugal',
    'GR': 'Greece',
    'IL': 'Israel',
    'SG': 'Singapore',
}

# Координаты городов для новых стран
CITY_COORDINATES = {
    'ES': [
        '40.416775,-3.703790',  # Madrid
        '41.385064,2.173403',  # Barcelona
        '37.389092,-5.984459',  # Seville
        '39.469907,-0.376288',  # Valencia
        '36.721274,-4.421399',  # Malaga
        '40.970104,-5.663540',  # Salamanca
        '38.707750,-9.136591',  # Lisbon
        '42.237964,-8.720244',  # Vigo
        '37.992240,-1.130654',  # Murcia
        '39.569600,2.650160',  # Palma
        '40.656635,-4.697438',  # Ávila
        '40.331950,-1.107018',  # Teruel
        '41.656060,-0.877340'  # Zaragoza
    ],
    'DE': [
        '52.520008,13.404954',  # Berlin
        '48.135124,11.581981',  # Munich
        '50.110924,8.682127',  # Frankfurt
        '53.551086,9.993682',  # Hamburg
        '51.227741,6.773456',  # Dusseldorf
        '51.514942,7.466963',  # Dortmund
        '49.006889,8.403653',  # Karlsruhe
        '49.452103,11.076665',  # Nuremberg
        '51.339695,12.373075',  # Leipzig
        '49.791304,9.953354',  # Würzburg
        '50.775346,6.083887',  # Aachen
        '50.641200,10.121810',  # Eisenach
        '50.828710,8.773710'  # Marburg
    ],
    # Остальные существующие страны...

    # Добавляем новые страны:
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
        '36.169941,-115.139832',  # Las Vegas
        '25.761681,-80.191788',  # Miami
        '39.768402,-86.158066'  # Indianapolis
    ],
    'CA': [
        '43.651070,-79.347015',  # Toronto
        '45.508888,-73.561668',  # Montreal
        '49.282730,-123.120735',  # Vancouver
        '51.048615,-114.070847',  # Calgary
        '53.544388,-113.490929',  # Edmonton
        '45.421530,-75.697193',  # Ottawa
        '49.895077,-97.138451',  # Winnipeg
        '46.811969,-71.214313',  # Quebec City
        '50.445210,-104.618896'  # Regina
    ],
    'AU': [
        '-33.865143,151.209900',  # Sydney
        '-37.813629,144.963058',  # Melbourne
        '-27.469771,153.025124',  # Brisbane
        '-31.953004,115.857469',  # Perth
        '-34.928499,138.600746',  # Adelaide
        '-42.880554,147.324997',  # Hobart
        '-12.462827,130.841782',  # Darwin
        '-35.282001,149.128998'  # Canberra
    ],
    'NZ': [
        '-36.848460,174.763332',  # Auckland
        '-41.286460,174.776236',  # Wellington
        '-43.532054,172.636225',  # Christchurch
        '-45.878761,170.502792',  # Dunedin
        '-37.787000,175.279000',  # Hamilton
        '-40.355000,175.611000'  # Palmerston North
    ],
    'JP': [
        '35.689487,139.691711',  # Tokyo
        '34.693738,135.502165',  # Osaka
        '35.011635,135.768036',  # Kyoto
        '43.066666,141.350006',  # Sapporo
        '33.590355,130.401716',  # Fukuoka
        '34.385203,132.455293',  # Hiroshima
        '38.268223,140.869415',  # Sendai
        '35.442739,139.638031'  # Yokohama
    ],
    'KR': [
        '37.566536,126.977966',  # Seoul
        '35.179554,129.075642',  # Busan
        '35.871433,128.601440',  # Daegu
        '37.456257,126.705208',  # Incheon
        '35.160012,126.851349',  # Gwangju
        '36.350412,127.384548',  # Daejeon
        '36.565127,128.725056'  # Andong
    ],
    'CN': [
        '39.904202,116.407394',  # Beijing
        '31.230391,121.473702',  # Shanghai
        '22.396427,114.109497',  # Hong Kong
        '30.274084,120.155070',  # Hangzhou
        '23.129110,113.264381',  # Guangzhou
        '29.563010,106.551557',  # Chongqing
        '43.825592,87.616848'  # Urumqi
    ],
    'IN': [
        '28.613939,77.209023',  # New Delhi
        '19.075983,72.877655',  # Mumbai
        '12.971599,77.594566',  # Bangalore
        '22.572645,88.363892',  # Kolkata
        '13.082680,80.270721',  # Chennai
        '17.385044,78.486671',  # Hyderabad
        '18.520430,73.856743'  # Pune
    ],
    'BR': [
        '-23.550520,-46.633308',  # Sao Paulo
        '-22.906847,-43.172897',  # Rio de Janeiro
        '-15.794229,-47.882166',  # Brasilia
        '-19.916683,-43.934265',  # Belo Horizonte
        '-12.971598,-38.501587',  # Salvador
        '-3.731862,-38.526669',  # Fortaleza
        '-8.054277,-34.881256'  # Recife
    ],
    'MX': [
        '19.432608,-99.133209',  # Mexico City
        '20.666891,-103.392955',  # Guadalajara
        '25.685710,-100.311129',  # Monterrey
        '21.161908,-86.851528',  # Cancun
        '20.967198,-89.591913',  # Merida
        '31.722116,-106.462497'  # Ciudad Juarez
    ],
    'AE': [
        '25.204849,55.270782',  # Dubai
        '24.466667,54.366669',  # Abu Dhabi
        '25.317644,55.524660',  # Sharjah
        '25.785839,55.973403',  # Ras Al Khaimah
        '25.412439,55.435543'  # Ajman
    ],
    'ZA': [
        '-33.924870,18.424055',  # Cape Town
        '-26.204103,28.047305',  # Johannesburg
        '-29.858681,31.021839',  # Durban
        '-25.747868,28.229270',  # Pretoria
        '-33.660297,25.603434'  # Port Elizabeth
    ],
    'SE': [
        '59.329323,18.068581',  # Stockholm
        '57.708870,11.974560',  # Gothenburg
        '55.604980,13.003822',  # Malmö
        '59.858562,17.638927',  # Uppsala
        '58.410807,15.621373'  # Linköping
    ],
    'NO': [
        '59.911491,10.757933',  # Oslo
        '60.391263,5.322054',  # Bergen
        '63.430515,10.395053',  # Trondheim
        '58.969975,5.733107',  # Stavanger
        '69.649208,18.955324'  # Tromsø
    ],
    'IE': [
        '53.349805,-6.260310',  # Dublin
        '51.898110,-8.475050',  # Cork
        '53.270668,-9.056790',  # Galway
        '52.668018,-8.630498',  # Limerick
        '54.597285,-5.930120'  # Belfast
    ],
    'CH': [
        '47.376888,8.541694',  # Zurich
        '46.204391,6.143158',  # Geneva
        '46.947975,7.447447',  # Bern
        '47.559601,7.588576',  # Basel
        '46.994876,6.931704'  # Neuchâtel
    ],
    'PT': [
        '38.722252,-9.139337',  # Lisbon
        '41.157944,-8.629105',  # Porto
        '37.019356,-7.930440',  # Faro
        '38.571431,-7.913095',  # Évora
        '32.649382,-16.916227'  # Funchal
    ],
    'GR': [
        '37.983917,23.729360',  # Athens
        '40.640061,22.944419',  # Thessaloniki
        '35.337496,25.144896',  # Heraklion
        '39.074208,21.824312',  # Agrinio
        '39.366487,22.942764'  # Larissa
    ],
    'IL': [
        '32.085300,34.781768',  # Tel Aviv
        '31.768319,35.213710',  # Jerusalem
        '32.794044,34.989571',  # Haifa
        '31.263139,34.801763',  # Beersheba
        '32.794241,35.545310'  # Tiberias
    ],
    'SG': [
        '1.352083,103.819836',  # Singapore City
        '1.329058,103.829025',  # Tampines
        '1.371900,103.893356',  # Changi
        '1.354115,103.686289',  # Jurong East
        '1.301080,103.915640'  # Marine Parade
    ],
}

# Радиусы для поиска для всех стран
RADIUS_DATA = {
    'ES': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '40.970104,-5.663540',  # Salamanca
            '42.237964,-8.720244',  # Vigo
            '37.992240,-1.130654',  # Murcia
            '40.656635,-4.697438',  # Ávila
            '40.331950,-1.107018',  # Teruel
            '41.656060,-0.877340'  # Zaragoza
        ]
    },
    'DE': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '50.775346,6.083887',  # Aachen
            '50.641200,10.121810',  # Eisenach
            '50.828710,8.773710'  # Marburg
        ]
    },
    # Остальные существующие страны...

    # Добавляем новые страны
    'US': {
        'default': 35000,
        'border': 25000,
        'border_cities': [
            '29.760427,-95.369804',  # Houston
            '33.748997,-84.387985',  # Atlanta
            '42.360082,-71.058880',  # Boston
            '25.761681,-80.191788',  # Miami
            '39.768402,-86.158066'  # Indianapolis
        ]
    },
    'CA': {
        'default': 35000,
        'border': 25000,
        'border_cities': [
            '49.282730,-123.120735',  # Vancouver
            '43.651070,-79.347015',  # Toronto
            '45.508888,-73.561668',  # Montreal
            '46.811969,-71.214313',  # Quebec City
        ]
    },
    'AU': {
        'default': 40000,
        'border': 30000,
        'border_cities': [
            '-33.865143,151.209900',  # Sydney
            '-37.813629,144.963058',  # Melbourne
            '-12.462827,130.841782',  # Darwin
        ]
    },
    'NZ': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '-36.848460,174.763332',  # Auckland
            '-41.286460,174.776236',  # Wellington
            '-43.532054,172.636225',  # Christchurch
        ]
    },
    'JP': {
        'default': 25000,
        'border': 15000,
        'border_cities': [
            '35.689487,139.691711',  # Tokyo
            '34.693738,135.502165',  # Osaka
            '43.066666,141.350006',  # Sapporo
        ]
    },
    'KR': {
        'default': 25000,
        'border': 15000,
        'border_cities': [
            '37.566536,126.977966',  # Seoul
            '35.179554,129.075642',  # Busan
            '37.456257,126.705208',  # Incheon
        ]
    },
    'CN': {
        'default': 40000,
        'border': 30000,
        'border_cities': [
            '39.904202,116.407394',  # Beijing
            '31.230391,121.473702',  # Shanghai
            '22.396427,114.109497',  # Hong Kong
        ]
    },
    'IN': {
        'default': 40000,
        'border': 30000,
        'border_cities': [
            '28.613939,77.209023',  # New Delhi
            '19.075983,72.877655',  # Mumbai
            '12.971599,77.594566',  # Bangalore
        ]
    },
    'BR': {
        'default': 40000,
        'border': 30000,
        'border_cities': [
            '-23.550520,-46.633308',  # Sao Paulo
            '-22.906847,-43.172897',  # Rio de Janeiro
            '-15.794229,-47.882166',  # Brasilia
        ]
    },
    'MX': {
        'default': 35000,
        'border': 25000,
        'border_cities': [
            '19.432608,-99.133209',  # Mexico City
            '20.666891,-103.392955',  # Guadalajara
            '21.161908,-86.851528',  # Cancun
        ]
    },
    'AE': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '25.204849,55.270782',  # Dubai
            '24.466667,54.366669',  # Abu Dhabi
            '25.317644,55.524660',  # Sharjah
        ]
    },
    'ZA': {
        'default': 35000,
        'border': 25000,
        'border_cities': [
            '-33.924870,18.424055',  # Cape Town
            '-26.204103,28.047305',  # Johannesburg
            '-29.858681,31.021839',  # Durban
        ]
    },
    'SE': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '59.329323,18.068581',  # Stockholm
            '57.708870,11.974560',  # Gothenburg
            '55.604980,13.003822',  # Malmö
        ]
    },
    'NO': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '59.911491,10.757933',  # Oslo
            '60.391263,5.322054',  # Bergen
            '69.649208,18.955324',  # Tromsø
        ]
    },
    'IE': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '53.349805,-6.260310',  # Dublin
            '51.898110,-8.475050',  # Cork
            '54.597285,-5.930120',  # Belfast
        ]
    },
    'CH': {
        'default': 25000,
        'border': 15000,
        'border_cities': [
            '47.376888,8.541694',  # Zurich
            '46.204391,6.143158',  # Geneva
            '47.559601,7.588576',  # Basel
        ]
    },
    'PT': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '38.722252,-9.139337',  # Lisbon
            '41.157944,-8.629105',  # Porto
            '37.019356,-7.930440',  # Faro
        ]
    },
    'GR': {
        'default': 30000,
        'border': 20000,
        'border_cities': [
            '37.983917,23.729360',  # Athens
            '40.640061,22.944419',  # Thessaloniki
            '35.337496,25.144896',  # Heraklion
        ]
    },
    'IL': {
        'default': 25000,
        'border': 15000,
        'border_cities': [
            '32.085300,34.781768',  # Tel Aviv
            '31.768319,35.213710',  # Jerusalem
            '32.794044,34.989571',  # Haifa
        ]
    },
    'SG': {
        'default': 15000,
        'border': 10000,
        'border_cities': [
            '1.352083,103.819836',  # Singapore City
            '1.329058,103.829025',  # Tampines
            '1.371900,103.893356',  # Changi
        ]
    },
}

# Настройки для генерации данных пользователей
USER_GEN_CONFIG = {
    'min_age': 25,
    'max_age': 45,
    'proxy_port_range': (100, 299),  # Расширенный диапазон портов
    'password_length': 18,  # Увеличенная длина пароля
}

# Настройки для Google Maps API
GMAPS_CONFIG = {
    'max_retries': 5,
    'retry_base_delay': 2,  # секунды
    'language': 'en',
    'place_types': ['street_address', 'premise', 'subpremise'],
    'required_components': ['street_number', 'route', 'postal_code', 'locality'],
}