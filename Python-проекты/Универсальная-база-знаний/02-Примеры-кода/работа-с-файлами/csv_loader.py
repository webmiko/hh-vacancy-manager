import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd  # type: ignore[import-untyped]
from pandas import isna  # type: ignore[import-untyped]


def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля csv_loader.

    Returns:
        Настроенный логгер для модуля csv_loader
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "csv_loader.log"
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# Создаем логгер для модуля
logger = _setup_logger()

# 4. Константы модуля
ENCODING = "utf-8"
DEFAULT_RETURN_VALUE: List[Dict[str, Any]] = []
CSV_SEPARATOR = ";"  # Разделитель для CSV файлов

# 5. Функции модуля


def load_transactions_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает список транзакций из CSV-файла.

    Преобразует плоскую структуру CSV (amount, currency_code, currency_name)
    во вложенную структуру JSON (operationAmount.amount, operationAmount.currency.code),
    совместимую с остальным кодом проекта.

    Args:
        file_path: Путь до CSV-файла с транзакциями

    Returns:
        Список словарей с данными о финансовых транзакциях в формате:
        {
            "id": int,
            "state": str,
            "date": str,
            "description": str,
            "from": str,
            "to": str,
            "operationAmount": {
                "amount": str,
                "currency": {
                    "code": str,
                    "name": str
                }
            }
        }
        Возвращает пустой список, если:
        - файл не найден
        - произошла ошибка при чтении CSV
    """
    logger.debug(f"Начало загрузки транзакций из CSV файла: {file_path}")

    # Проверяем существование файла
    if not Path(file_path).exists():
        logger.warning(f"Файл не найден: {file_path}")
        return DEFAULT_RETURN_VALUE

    try:
        # Чтение CSV через pandas
        df = pd.read_csv(file_path, sep=CSV_SEPARATOR, encoding=ENCODING)

        # Преобразование DataFrame в список словарей
        transactions_raw = df.to_dict("records")

        # Преобразование плоской структуры CSV в вложенную структуру JSON
        transactions: List[Dict[str, Any]] = []
        for transaction_raw in transactions_raw:
            transaction: Dict[str, Any] = {}

            # Копируем базовые поля
            for key in ["id", "state", "date", "description", "from", "to"]:
                if key in transaction_raw:
                    value = transaction_raw[key]
                    if isna(value):
                        continue
                    # Преобразуем float в int для id
                    if key == "id" and isinstance(value, float):
                        transaction[key] = int(value)
                    else:
                        transaction[key] = value

            # Преобразуем плоскую структуру валюты в вложенную структуру operationAmount
            if "amount" in transaction_raw and not isna(transaction_raw["amount"]):
                amount = transaction_raw["amount"]
                # Преобразуем float в str для amount
                if isinstance(amount, float):
                    amount_str = str(amount)
                else:
                    amount_str = str(amount)

                currency_code = transaction_raw.get("currency_code", "")
                currency_name = transaction_raw.get("currency_name", "")

                # Пропускаем NaN значения для валюты
                if not isna(currency_code) and not isna(currency_name):
                    transaction["operationAmount"] = {
                        "amount": amount_str,
                        "currency": {
                            "code": str(currency_code),
                            "name": str(currency_name),
                        },
                    }

            if transaction:  # Добавляем только если есть данные
                transactions.append(transaction)

        logger.info(f"Успешно загружено {len(transactions)} транзакций из CSV файла: {file_path}")
        return transactions

    except pd.errors.EmptyDataError:
        logger.warning(f"CSV файл пустой: {file_path}")
        return DEFAULT_RETURN_VALUE
    except Exception as e:
        logger.error(f"Ошибка при чтении CSV файла {file_path}: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE


def load_transactions_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает список транзакций из Excel-файла (XLSX).

    Преобразует плоскую структуру Excel (amount, currency_code, currency_name)
    во вложенную структуру JSON (operationAmount.amount, operationAmount.currency.code),
    совместимую с остальным кодом проекта.

    Args:
        file_path: Путь до Excel-файла с транзакциями

    Returns:
        Список словарей с данными о финансовых транзакциях в формате:
        {
            "id": int,
            "state": str,
            "date": str,
            "description": str,
            "from": str,
            "to": str,
            "operationAmount": {
                "amount": str,
                "currency": {
                    "code": str,
                    "name": str
                }
            }
        }
        Возвращает пустой список, если:
        - файл не найден
        - произошла ошибка при чтении Excel
    """
    logger.debug(f"Начало загрузки транзакций из Excel файла: {file_path}")

    # Проверяем существование файла
    if not Path(file_path).exists():
        logger.warning(f"Файл не найден: {file_path}")
        return DEFAULT_RETURN_VALUE

    try:
        # Чтение Excel через pandas
        df = pd.read_excel(file_path, engine="openpyxl")

        # Преобразование DataFrame в список словарей
        transactions_raw = df.to_dict("records")

        # Преобразование плоской структуры Excel в вложенную структуру JSON
        transactions: List[Dict[str, Any]] = []
        for transaction_raw in transactions_raw:
            transaction: Dict[str, Any] = {}

            # Копируем базовые поля
            for key in ["id", "state", "date", "description", "from", "to"]:
                if key in transaction_raw:
                    value = transaction_raw[key]
                    if isna(value):
                        continue
                    # Преобразуем float в int для id
                    if key == "id" and isinstance(value, float):
                        transaction[key] = int(value)
                    else:
                        transaction[key] = value

            # Преобразуем плоскую структуру валюты в вложенную структуру operationAmount
            if "amount" in transaction_raw and not isna(transaction_raw["amount"]):
                amount = transaction_raw["amount"]
                # Преобразуем float в str для amount
                if isinstance(amount, float):
                    amount_str = str(amount)
                else:
                    amount_str = str(amount)

                currency_code = transaction_raw.get("currency_code", "")
                currency_name = transaction_raw.get("currency_name", "")

                # Пропускаем NaN значения для валюты
                if not isna(currency_code) and not isna(currency_name):
                    transaction["operationAmount"] = {
                        "amount": amount_str,
                        "currency": {
                            "code": str(currency_code),
                            "name": str(currency_name),
                        },
                    }

            if transaction:  # Добавляем только если есть данные
                transactions.append(transaction)

        logger.info(f"Успешно загружено {len(transactions)} транзакций из Excel файла: {file_path}")
        return transactions

    except pd.errors.EmptyDataError:
        logger.warning(f"Excel файл пустой: {file_path}")
        return DEFAULT_RETURN_VALUE
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel файла {file_path}: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE
