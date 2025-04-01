import os
import sys
import logging
import codecs

def setup_windows_console_encoding():
    """
    Настраивает кодировку консоли Windows для корректного отображения Unicode-символов.
    """
    if sys.platform == 'win32':
        try:
            # Способ 1: Через API консоли Windows
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleCP(65001)  # UTF-8
            kernel32.SetConsoleOutputCP(65001)  # UTF-8

            # Способ 2: Через переменные окружения
            os.environ['PYTHONIOENCODING'] = 'utf-8'

            # Способ 3: Через sys.stdout
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')

            # Способ 4: Принудительно меняем стандартные потоки
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

            print("Кодировка консоли Windows успешно настроена на UTF-8")
        except Exception as e:
            print(f"Предупреждение: Не удалось настроить кодировку консоли Windows: {e}")
            print("Русские символы в логах могут отображаться некорректно.")

            # Альтернативный вариант: использовать транслитерацию для логов
            try:
                from unidecode import unidecode

                class TransliteratedStreamHandler(logging.StreamHandler):
                    def emit(self, record):
                        try:
                            msg = self.format(record)
                            # Конвертируем все не-ASCII символы в их ASCII-эквиваленты
                            msg = unidecode(msg)
                            stream = self.stream
                            stream.write(msg + self.terminator)
                            self.flush()
                        except Exception as ex:
                            self.handleError(record)

                # Применяем для корневого логгера
                root_logger = logging.getLogger()
                for handler in root_logger.handlers[:]:
                    if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                        root_logger.removeHandler(handler)

                # Добавляем транслитерирующий обработчик
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                transliterated_handler = TransliteratedStreamHandler()
                transliterated_handler.setFormatter(formatter)
                root_logger.addHandler(transliterated_handler)

                print("Настроена транслитерация русских символов в логах для консоли Windows")
            except ImportError:
                print("Для транслитерации логов установите библиотеку unidecode: pip install unidecode")
    else:
        # Для Unix-подобных систем (Linux, macOS) UTF-8 обычно используется по умолчанию
        pass