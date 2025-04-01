#!/usr/bin/env python
# setup.py
import os
import sys
import subprocess
import platform
from pathlib import Path


def setup_environment():
    """Настраивает окружение для генератора пользовательских данных."""
    print("Настройка окружения для генератора пользовательских данных...")

    # Проверяем версию Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("ОШИБКА: Требуется Python 3.7 или выше!")
        sys.exit(1)

    print(f"Обнаружена версия Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Проверяем наличие pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("ОШИБКА: pip не установлен или не работает!")
        sys.exit(1)

    # Устанавливаем зависимости
    print("Установка зависимостей из requirements.txt...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    except subprocess.CalledProcessError:
        print("ОШИБКА: Не удалось установить зависимости!")
        sys.exit(1)

    # Создаем файл .env, если он не существует
    env_file = Path(".env")
    if not env_file.exists():
        print("Создание файла .env...")
        api_key = input("Введите ваш Google Maps API ключ (или нажмите Enter, чтобы пропустить): ")
        with open(env_file, "w") as f:
            f.write(f"GOOGLE_MAPS_API_KEY={api_key}\n")
        print("Файл .env создан.")
    else:
        print("Файл .env уже существует.")

    # Проверяем наличие API ключа в .env
    with open(env_file, "r") as f:
        env_content = f.read()

    if "GOOGLE_MAPS_API_KEY=" not in env_content or "GOOGLE_MAPS_API_KEY=\n" in env_content:
        print("ВНИМАНИЕ: Google Maps API ключ не указан в файле .env!")
        print("Для полноценной работы генератора адресов необходимо добавить ключ в файл .env.")

    # Проверяем работу pyperclip
    print("Проверка работы с буфером обмена...")
    try:
        import pyperclip
        pyperclip.copy("test")
        test_clipboard = pyperclip.paste()

        if test_clipboard != "test":
            raise Exception("Данные в буфере обмена не совпадают с ожидаемыми")

        print("Буфер обмена работает корректно.")
    except Exception as e:
        print(f"ВНИМАНИЕ: Проблемы с буфером обмена: {e}")

        if platform.system() == "Linux":
            print("На Linux может потребоваться установка дополнительных пакетов:")
            print("  Для Debian/Ubuntu: sudo apt-get install xclip or xsel")
            print("  Для Fedora: sudo dnf install xclip or xsel")
            print("  Для CentOS/RHEL: sudo yum install xclip or xsel")
        elif platform.system() == "Darwin":
            print("На macOS обычно нет проблем с буфером обмена.")
            print("Если проблема остается, попробуйте: pip install pyobjc-framework-Cocoa")

    print("\nНастройка окружения завершена!")
    print("Для запуска генератора данных выполните: python main.py")
    print("Для просмотра справки выполните: python main.py --help")


if __name__ == "__main__":
    setup_environment()