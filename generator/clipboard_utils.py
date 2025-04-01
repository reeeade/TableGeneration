# clipboard_utils.py
import pyperclip
import pandas as pd
import logging
import json
import os
from typing import Optional, Union, List, Dict, Any
import csv
from io import StringIO

logger = logging.getLogger(__name__)


def copy_to_clipboard(data_frame: pd.DataFrame, with_header: bool = False) -> None:
    """
    Копирует содержимое DataFrame в буфер обмена в формате TSV.

    Args:
        data_frame: DataFrame для копирования
        with_header: Если True, включает заголовки столбцов
    """
    try:
        tsv_data = data_frame.to_csv(index=False, header=with_header, sep="\t")
        pyperclip.copy(tsv_data)
        logger.info(f"Данные успешно скопированы в буфер обмена ({len(data_frame)} строк)")
    except pyperclip.PyperclipException as e:
        logger.error(f"Не удалось скопировать данные в буфер обмена: {e}")
        logger.info("Попытка сохранить данные в файл вместо буфера обмена")
        save_to_file(data_frame, "clipboard_data.tsv", sep="\t")


def save_to_file(data: Union[pd.DataFrame, List[Dict[str, Any]]],
                 filename: str,
                 format: str = None,
                 sep: str = ",") -> None:
    """
    Сохраняет данные в файл.

    Args:
        data: DataFrame или список словарей для сохранения
        filename: Имя файла
        format: Формат файла (csv, json, excel). Если None, определяется по расширению файла.
        sep: Разделитель для CSV файлов
    """
    # Преобразуем список словарей в DataFrame, если необходимо
    if isinstance(data, list):
        data = pd.DataFrame(data)

    # Определяем формат по расширению файла, если не указан
    if format is None:
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.csv':
            format = 'csv'
        elif ext == '.json':
            format = 'json'
        elif ext in ['.xlsx', '.xls']:
            format = 'excel'
        elif ext == '.tsv':
            format = 'csv'
            sep = '\t'
        else:
            format = 'csv'  # По умолчанию - CSV

    try:
        # Сохраняем данные в соответствующем формате
        if format == 'csv':
            data.to_csv(filename, index=False, sep=sep)
        elif format == 'json':
            data.to_json(filename, orient='records', indent=2)
        elif format == 'excel':
            data.to_excel(filename, index=False)

        logger.info(f"Данные успешно сохранены в файл {filename} ({len(data)} строк)")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в файл {filename}: {e}")


def load_from_clipboard() -> Optional[pd.DataFrame]:
    """
    Загружает данные из буфера обмена в DataFrame.
    Пытается автоматически определить формат данных (CSV, TSV, JSON).

    Returns:
        DataFrame с данными из буфера обмена или None в случае ошибки
    """
    try:
        clipboard_content = pyperclip.paste()
        if not clipboard_content:
            logger.warning("Буфер обмена пуст")
            return None

        # Попробуем распознать JSON
        if clipboard_content.strip().startswith('{') or clipboard_content.strip().startswith('['):
            try:
                json_data = json.loads(clipboard_content)
                if isinstance(json_data, list):
                    return pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    return pd.DataFrame([json_data])
            except json.JSONDecodeError:
                pass  # Не JSON, продолжаем с другими форматами

        # Пробуем определить разделитель (CSV или TSV)
        # Проверяем наличие табуляции
        if '\t' in clipboard_content:
            df = pd.read_csv(StringIO(clipboard_content), sep='\t', header=None)
            # Если первая строка похожа на заголовок, используем её
            if all(isinstance(x, str) for x in df.iloc[0]):
                df.columns = df.iloc[0]
                df = df.drop(0).reset_index(drop=True)
            return df
        else:
            # Пробуем с запятой
            df = pd.read_csv(StringIO(clipboard_content), sep=',', header=None)
            # Если первая строка похожа на заголовок, используем её
            if all(isinstance(x, str) for x in df.iloc[0]):
                df.columns = df.iloc[0]
                df = df.drop(0).reset_index(drop=True)
            return df

    except Exception as e:
        logger.error(f"Ошибка при загрузке данных из буфера обмена: {e}")
        return None


def export_data(data_frame: pd.DataFrame,
                export_format: str = 'clipboard',
                filename: Optional[str] = None,
                include_header: bool = True) -> None:
    """
    Экспортирует данные в различных форматах.

    Args:
        data_frame: DataFrame для экспорта
        export_format: Формат экспорта ('clipboard', 'csv', 'tsv', 'json', 'excel')
        filename: Имя файла (только для форматов, отличных от 'clipboard')
        include_header: Включать ли заголовки столбцов (только для 'clipboard')
    """
    if export_format == 'clipboard':
        copy_to_clipboard(data_frame, with_header=include_header)
    elif export_format in ['csv', 'tsv', 'json', 'excel']:
        if filename is None:
            # Генерируем имя файла, если не указано
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            extensions = {'csv': '.csv', 'tsv': '.tsv', 'json': '.json', 'excel': '.xlsx'}
            filename = f"data_export_{timestamp}{extensions.get(export_format, '.csv')}"

        # Определяем разделитель для CSV/TSV
        sep = '\t' if export_format == 'tsv' else ','

        save_to_file(data_frame, filename, format=export_format, sep=sep)
    else:
        logger.error(f"Неизвестный формат экспорта: {export_format}")