import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .widget import get_date

# Константы модуля
DEFAULT_STATE = "EXECUTED"
DATE_FORMAT = "%d.%m.%Y"
DEFAULT_RETURN_VALUE: List[Dict[str, Any]] = []
DEFAULT_RETURN_DICT: Dict[str, int] = {}
ENCODING = "utf-8"
FILE_WRITE_MODE = "w"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
EMPTY_STRING = ""
DEFAULT_COUNTER_VALUE = 0
REGEX_FLAG_CASE_INSENSITIVE = re.IGNORECASE


def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля processing.

    Returns:
        Настроенный логгер для модуля processing
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "processing.log"
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


def filter_by_state(transactions: List[Dict[str, Any]], state: str = DEFAULT_STATE) -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по значению ключа 'state'.

    Args:
        transactions: Список словарей для фильтрации
        state: Значение состояния для фильтрации (по умолчанию 'EXECUTED')

    Returns:
        Новый список, содержащий только словари с указанным значением состояния
    """
    # Используем .get() для безопасного доступа к ключу, чтобы избежать KeyError
    return [tx for tx in transactions if tx.get("state") == state]


def sort_by_date(transactions: List[Dict[str, Any]], is_reverse_order: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список словарей по ключу 'date' в формате ISO.

    Args:
        transactions: Список словарей, содержащих ключи 'date'
        is_reverse_order: Порядок сортировки (по умолчанию True - по убыванию)

    Returns:
        Новый список, отсортированный по дате c возможностью обратного порядка из функции get_date
    """
    # Сортировка с использованием преобразования строки даты в объект datetime
    # Явно указываем тип данных для ключа сортировки, чтобы улучшить читаемость

    return sorted(
        transactions, key=lambda tx: datetime.strptime(get_date(tx["date"]), DATE_FORMAT), reverse=is_reverse_order
    )


def filter_by_currency(transactions: List[Dict[str, Any]], currency_code: str) -> List[Dict[str, Any]]:
    """
    Фильтрует список транзакций по коду валюты.

    Args:
        transactions: Список словарей с транзакциями
        currency_code: Код валюты для фильтрации (например, "RUB", "USD", "EUR")

    Returns:
        Новый список, содержащий только транзакции с указанной валютой.
        Возвращает пустой список, если:
        - передан пустой список транзакций
        - не найдено транзакций с указанной валютой
    """
    logger.info(f"Начало фильтрации транзакций по валюте: {currency_code}")

    if not transactions:
        logger.warning("Передан пустой список транзакций")
        return DEFAULT_RETURN_VALUE

    if not currency_code:
        logger.warning("Передан пустой код валюты")
        return DEFAULT_RETURN_VALUE

    try:
        result: List[Dict[str, Any]] = []
        for transaction in transactions:
            transaction_currency = transaction.get("operationAmount", {}).get("currency", {}).get("code", "")
            if transaction_currency == currency_code:
                result.append(transaction)

        logger.info(f"Найдено транзакций с валютой {currency_code}: {len(result)}")
        return result

    except (AttributeError, TypeError) as e:
        logger.error(f"Ошибка при фильтрации по валюте: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE
    except Exception as e:
        logger.error(f"Неожиданная ошибка при фильтрации по валюте: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """
    Ищет транзакции по заданной строке в описании с использованием регулярных выражений.

    Args:
        data: Список словарей с транзакциями
        search: Строка для поиска в поле description

    Returns:
        Список словарей с транзакциями, у которых в описании найдена строка поиска.
        Возвращает пустой список, если:
        - передан пустой список транзакций
        - строка поиска не найдена ни в одной транзакции
    """
    logger.info(f"Начало поиска транзакций по строке: '{search}'")

    if not data:
        logger.warning("Передан пустой список транзакций")
        return DEFAULT_RETURN_VALUE

    if not search:
        logger.warning("Передана пустая строка поиска")
        return DEFAULT_RETURN_VALUE

    try:
        # Компилируем регулярное выражение для регистронезависимого поиска
        pattern = re.compile(re.escape(search), REGEX_FLAG_CASE_INSENSITIVE)

        result: List[Dict[str, Any]] = []

        # Итерация по транзакциям
        for transaction in data:
            description = transaction.get("description", EMPTY_STRING)

            # Поиск с помощью регулярного выражения
            if pattern.search(description):
                result.append(transaction)

        logger.info(f"Найдено транзакций: {len(result)}")
        return result

    except (re.error, AttributeError, TypeError) as e:
        logger.error(f"Ошибка при поиске транзакций: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE
    except Exception as e:
        logger.error(f"Неожиданная ошибка при поиске транзакций: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE


def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество банковских операций определенного типа.

    Args:
        data: Список словарей с транзакциями
        categories: Список категорий операций для подсчета (на основе поля description)

    Returns:
        Словарь, в котором ключи — это названия категорий, а значения — это количество операций в каждой категории.
        Возвращает пустой словарь, если:
        - передан пустой список транзакций
        - передан пустой список категорий
    """
    logger.info(f"Начало подсчета операций по категориям: {categories}")

    if not data:
        logger.warning("Передан пустой список транзакций")
        return DEFAULT_RETURN_DICT

    if not categories:
        logger.warning("Передан пустой список категорий")
        return DEFAULT_RETURN_DICT

    try:
        # Извлекаем все описания из транзакций
        descriptions: List[str] = []
        for transaction in data:
            description = transaction.get("description", EMPTY_STRING)
            if description != EMPTY_STRING:
                descriptions.append(description)

        # Подсчет с помощью Counter
        counter = Counter(descriptions)

        # Формируем результат только для запрошенных категорий
        result: Dict[str, int] = {}
        for category in categories:
            result[category] = counter.get(category, DEFAULT_COUNTER_VALUE)

        logger.info(f"Подсчет завершен: {result}")
        return result

    except (AttributeError, TypeError) as e:
        logger.error(f"Ошибка при подсчете операций: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_DICT
    except Exception as e:
        logger.error(f"Неожиданная ошибка при подсчете операций: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_DICT
