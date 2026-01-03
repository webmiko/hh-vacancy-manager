"""Модуль для загрузки и сохранения данных.

Этот модуль содержит функции для загрузки данных из файлов,
работы с настройками пользователя и сохранения данных.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Константы модуля
ENCODING = "utf-8"
DATE_OPERATION_FORMAT = "%d.%m.%Y %H:%M:%S"
DATE_PAYMENT_FORMAT = "%d.%m.%Y"
FILE_WRITE_MODE = "w"
FILE_READ_MODE = "r"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_RETURN_VALUE: List[Dict[str, Any]] = []
DEFAULT_RETURN_DICT: Dict[str, Any] = {}
REQUIRED_COLUMNS = [
    "Дата операции",
    "Дата платежа",
    "Номер карты",
    "Статус",
    "Сумма операции",
    "Валюта операции",
    "Сумма платежа",
    "Валюта платежа",
    "Кэшбэк",
    "Категория",
    "MCC",
    "Описание",
    "Бонусы (включая кэшбэк)",
    "Округление на инвесткопилку",
    "Сумма операции с округлением",
]
USER_SETTINGS_FILE = "user_settings.json"


def _sanitize_error_message(error_msg: str) -> str:
    """
    Удаляет чувствительные данные (API ключи) из сообщения об ошибке.

    Args:
        error_msg: Исходное сообщение об ошибке

    Returns:
        Сообщение об ошибке без чувствительных данных

    Example:
        >>> msg = "Error: https://api.example.com?key=secret123"
        >>> _sanitize_error_message(msg)
        'Error: https://api.example.com?key=***'
    """
    # Маскируем API ключи в URL параметрах
    # Паттерны для различных форматов API ключей
    patterns = [
        (r"(access_key=)([^&\s]+)", r"\1***"),
        (r"(apikey=)([^&\s]+)", r"\1***"),
        (r"(api_key=)([^&\s]+)", r"\1***"),
        (r"(key=)([^&\s]+)", r"\1***"),
    ]

    sanitized = error_msg
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля data_loading.

    Returns:
        Настроенный логгер для модуля data_loading
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "data_loading.log"
    file_handler = logging.FileHandler(log_file, mode=FILE_WRITE_MODE, encoding=ENCODING)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=TIMESTAMP_FORMAT,
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# Создаем логгер для модуля
logger = _setup_logger()


def load_transactions_from_excel(file_path: str) -> pd.DataFrame:
    """
    Загружает транзакции из Excel-файла и возвращает DataFrame.

    Функция загружает данные из Excel-файла, обрабатывает формат дат
    и выполняет валидацию данных. Логирует операции без конфиденциальных данных.

    Args:
        file_path: Путь к Excel-файлу с транзакциями

    Returns:
        DataFrame с транзакциями. Возвращает пустой DataFrame при ошибке.

    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если файл не содержит необходимых колонок

    Example:
        >>> df = load_transactions_from_excel("data/operations.xlsx")
        >>> print(df.shape)
        (100, 15)
    """
    logger.info("Начало загрузки транзакций из файла")

    # Проверка существования файла
    if not os.path.exists(file_path):
        error_msg = "Файл не найден"
        logger.error(f"{error_msg}: {Path(file_path).name}")
        raise FileNotFoundError(f"{error_msg}: {file_path}")

    try:
        # Загрузка данных из Excel
        logger.debug(f"Чтение Excel-файла: {Path(file_path).name}")
        df = pd.read_excel(file_path, engine="openpyxl")

        # Валидация: проверка наличия необходимых колонок
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            error_msg = f"Отсутствуют необходимые колонки: {', '.join(missing_columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Загружено строк: {len(df)}")

        # Обработка формата дат
        logger.debug("Обработка формата дат")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format=DATE_OPERATION_FORMAT, errors="coerce")
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format=DATE_PAYMENT_FORMAT, errors="coerce")

        # Проверка успешности парсинга дат
        invalid_dates_operation = df["Дата операции"].isna().sum()
        invalid_dates_payment = df["Дата платежа"].isna().sum()

        if invalid_dates_operation > 0:
            logger.warning(f"Найдено некорректных дат операции: {invalid_dates_operation}")
        if invalid_dates_payment > 0:
            logger.warning(f"Найдено некорректных дат платежа: {invalid_dates_payment}")

        # Валидация: проверка на пустой DataFrame
        if df.empty:
            logger.warning("Загружен пустой файл")
            return df

        logger.info(f"Загрузка завершена успешно: {len(df)} транзакций")
        return df

    except FileNotFoundError:
        # Повторно пробрасываем FileNotFoundError
        raise
    except ValueError:
        # Повторно пробрасываем ValueError (валидация колонок)
        raise
    except Exception as e:
        error_msg = "Ошибка при загрузке файла"
        logger.error(f"{error_msg}: {type(e).__name__} - {e}")
        # Возвращаем пустой DataFrame вместо проброса исключения
        return pd.DataFrame()


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает настройки пользователя из файла user_settings.json.

    Returns:
        Словарь с настройками пользователя. Возвращает пустой словарь при ошибке.

    Example:
        >>> settings = load_user_settings()
        >>> print(settings.get('user_currencies'))
        ['USD', 'EUR']
    """
    logger.info("Загрузка настроек пользователя")

    if not os.path.exists(USER_SETTINGS_FILE):
        logger.warning(f"Файл {USER_SETTINGS_FILE} не найден. Возвращаем пустой словарь.")
        return {}

    try:
        with open(USER_SETTINGS_FILE, FILE_READ_MODE, encoding=ENCODING) as f:
            settings: Dict[str, Any] = json.load(f)

        logger.info(f"Настройки успешно загружены из {USER_SETTINGS_FILE}")
        return settings

    except json.JSONDecodeError as e:
        error_msg = f"Ошибка парсинга JSON в файле {USER_SETTINGS_FILE}"
        logger.error(f"{error_msg}: {type(e).__name__} - {e}")
        return {}
    except Exception as e:
        error_msg = f"Ошибка при загрузке настроек из {USER_SETTINGS_FILE}"
        logger.error(f"{error_msg}: {type(e).__name__} - {e}")
        return {}


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """
    Сохраняет данные в JSON-файл.

    Args:
        data: Словарь с данными для сохранения
        file_path: Путь к файлу для сохранения

    Raises:
        OSError: Если не удалось создать или записать файл

    Example:
        >>> data = {"key": "value"}
        >>> save_json(data, "output.json")
    """
    logger.info(f"Сохранение данных в JSON-файл: {Path(file_path).name}")

    try:
        with open(file_path, FILE_WRITE_MODE, encoding=ENCODING) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Данные успешно сохранены в {Path(file_path).name}")

    except OSError as e:
        error_msg = f"Ошибка при сохранении файла {Path(file_path).name}"
        logger.error(f"{error_msg}: {type(e).__name__} - {e}")
        raise
    except Exception as e:
        error_msg = "Неожиданная ошибка при сохранении JSON"
        logger.error(f"{error_msg}: {type(e).__name__} - {e}")
        raise

