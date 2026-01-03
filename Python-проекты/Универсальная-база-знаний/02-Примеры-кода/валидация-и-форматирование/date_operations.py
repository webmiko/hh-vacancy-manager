"""Модуль для работы с датами.

> **Дата добавления/обновления:** 2024-12-19
> **Категория:** Валидация и форматирование
> **Связанные модули:**
>   - `обработка-данных/spending_analysis.py` - использование функций для анализа трат
>   - `утилиты/web_data_generation.py` - форматирование дат для веб-интерфейса
> **Учебные материалы:**
>   - [01-Учебные-материалы/06-Данные/JSON-requests-datetime.md](../../01-Учебные-материалы/06-Данные/JSON-requests-datetime.md)

Этот модуль содержит функции для парсинга, форматирования
и вычисления диапазонов дат.

Когда использовать:
- При парсинге дат из строк
- При форматировании дат для отображения
- При вычислении диапазонов дат (месяц, неделя, год)
- При работе с финансовыми периодами

Особенности:
- Парсинг дат из различных форматов
- Форматирование дат для отображения
- Вычисление диапазонов (месяц, последние 3 месяца)
- Логирование операций
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

# Константы модуля
ENCODING = "utf-8"
FILE_WRITE_MODE = "w"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_OPERATION_FORMAT = "%d.%m.%Y %H:%M:%S"
DATE_PAYMENT_FORMAT = "%d.%m.%Y"
DATE_FORMAT = "%d.%m.%Y"
DATE_FORMAT_OUTPUT = "%d.%m.%Y"


def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля date_operations.

    Returns:
        Настроенный логгер для модуля date_operations
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "date_operations.log"
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


def parse_date(date_string: str) -> datetime:
    """
    Парсит дату из строки формата DD.MM.YYYY.

    Args:
        date_string: Строка с датой в формате DD.MM.YYYY

    Returns:
        Объект datetime с распарсенной датой

    Raises:
        ValueError: Если строка не соответствует формату DD.MM.YYYY

    Example:
        >>> date = parse_date("15.03.2024")
        >>> print(date)
        2024-03-15 00:00:00
    """
    try:
        parsed_date = datetime.strptime(date_string, DATE_FORMAT)
        logger.debug(f"Успешно распарсена дата: {date_string}")
        return parsed_date
    except ValueError as e:
        error_msg = f"Некорректный формат даты: {date_string}"
        logger.error(f"{error_msg}. Ожидается формат: {DATE_FORMAT}")
        raise ValueError(error_msg) from e


def format_date(date: datetime) -> str:
    """
    Форматирует дату в строку формата DD.MM.YYYY.

    Args:
        date: Объект datetime для форматирования

    Returns:
        Строка с датой в формате DD.MM.YYYY

    Example:
        >>> date = datetime(2024, 3, 15)
        >>> formatted = format_date(date)
        >>> print(formatted)
        15.03.2024
    """
    formatted = date.strftime(DATE_FORMAT_OUTPUT)
    logger.debug(f"Дата отформатирована: {formatted}")
    return formatted


def get_month_start(date: datetime) -> datetime:
    """
    Возвращает начало месяца для указанной даты.

    Args:
        date: Дата, для которой нужно найти начало месяца

    Returns:
        Объект datetime с началом месяца (первый день, 00:00:00)

    Example:
        >>> date = datetime(2024, 3, 15, 14, 30, 0)
        >>> month_start = get_month_start(date)
        >>> print(month_start)
        2024-03-01 00:00:00
    """
    month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    logger.debug(f"Начало месяца для {date.strftime(DATE_FORMAT_OUTPUT)}: {month_start.strftime(DATE_FORMAT_OUTPUT)}")
    return month_start


def get_month_range(date: datetime) -> Tuple[datetime, datetime]:
    """
    Возвращает диапазон месяца (начало и конец) для указанной даты.

    Args:
        date: Дата, для которой нужно найти диапазон месяца

    Returns:
        Кортеж (начало_месяца, конец_месяца)
        Конец месяца - последний день месяца, 23:59:59

    Example:
        >>> date = datetime(2024, 3, 15)
        >>> start, end = get_month_range(date)
        >>> print(start, end)
        2024-03-01 00:00:00 2024-03-31 23:59:59
    """
    month_start = get_month_start(date)

    # Вычисляем начало следующего месяца
    if date.month == 12:
        next_month_start = datetime(date.year + 1, 1, 1)
    else:
        next_month_start = datetime(date.year, date.month + 1, 1)

    # Конец месяца = начало следующего месяца минус 1 секунда
    month_end = next_month_start - timedelta(seconds=1)

    logger.debug(
        f"Диапазон месяца для {date.strftime(DATE_FORMAT_OUTPUT)}: "
        f"{month_start.strftime(DATE_FORMAT_OUTPUT)} - {month_end.strftime(DATE_FORMAT_OUTPUT)}"
    )
    return (month_start, month_end)


def get_three_months_back(date: datetime) -> Tuple[datetime, datetime]:
    """
    Возвращает диапазон последних 3 месяцев от указанной даты.

    Args:
        date: Дата, от которой отсчитываются последние 3 месяца

    Returns:
        Кортеж (начало_периода, конец_периода)
        Начало периода - начало месяца, который был 3 месяца назад
        Конец периода - конец указанного месяца

    Example:
        >>> date = datetime(2024, 3, 15)
        >>> start, end = get_three_months_back(date)
        >>> # Вернет период с начала декабря 2023 по конец марта 2024
    """
    # Конец периода - конец указанного месяца
    _, period_end = get_month_range(date)

    # Начало периода - начало месяца, который был 3 месяца назад
    # Вычисляем дату 3 месяца назад
    if date.month <= 3:
        # Если текущий месяц <= 3, нужно перейти в предыдущий год
        start_year = date.year - 1
        start_month = date.month + 9  # 12 - 3 + date.month
    else:
        start_year = date.year
        start_month = date.month - 3

    period_start = datetime(start_year, start_month, 1, 0, 0, 0)

    logger.debug(
        f"Диапазон последних 3 месяцев от {date.strftime(DATE_FORMAT_OUTPUT)}: "
        f"{period_start.strftime(DATE_FORMAT_OUTPUT)} - {period_end.strftime(DATE_FORMAT_OUTPUT)}"
    )
    return (period_start, period_end)

