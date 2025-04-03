# clipboard_utils.py
import logging

import pandas as pd
import pyperclip


def copy_to_clipboard(data_frame: pd.DataFrame) -> None:
    """
    Копирует содержимое DataFrame в буфер обмена в формате TSV (без заголовков).
    """
    try:
        tsv_data = data_frame.to_csv(index=False, header=False, sep="\t")
        pyperclip.copy(tsv_data)
        logging.info("Данные успешно скопированы в буфер обмена.")
    except pyperclip.PyperclipException as e:
        logging.error(f"Не удалось скопировать данные в буфер обмена: {e}")
