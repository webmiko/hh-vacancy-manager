"""Модуль для маскирования номеров карт и счетов.

> **Дата добавления/обновления:** 2024-12-19
> **Категория:** Валидация и форматирование
> **Связанные модули:**
>   - `утилиты/widget.py` - использование масок для отображения данных
>   - `генераторы/generators.py` - генерация номеров карт для тестирования
> **Учебные материалы:**
>   - [01-Учебные-материалы/10-ООП/Property-декоратор.md](../../01-Учебные-материалы/10-ООП/Property-декоратор.md)

Этот модуль содержит функции для маскирования чувствительных данных:
номеров банковских карт и счетов.

Когда использовать:
- При отображении номеров карт и счетов в интерфейсе
- При логировании чувствительных данных
- При валидации номеров карт и счетов

Особенности:
- Маскирование номеров карт (первые 6 и последние 4 цифры)
- Маскирование номеров счетов (последние 4 цифры)
- Валидация формата номеров
- Логирование операций
"""

import logging
from pathlib import Path
from typing import Union

# Константы модуля
MIN_CARD_LENGTH = 13
MAX_CARD_LENGTH = 19
STANDARD_CARD_LENGTH = 16
DEFAULT_BLOCK_SIZE = 4
FIRST_VISIBLE_DIGITS = 6
LAST_VISIBLE_DIGITS = 4
ENCODING = "utf-8"
FILE_WRITE_MODE = "w"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
ACCOUNT_MASK_PREFIX = "**"
MIN_ACCOUNT_TAIL_LENGTH = 4


def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля masks.

    Returns:
        Настроенный логгер для модуля masks
    """
    # Создаем логгер с именем модуля
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Предотвращаем дублирование логов (если логгер уже настроен)
    if logger.handlers:
        return logger

    # Создаем директорию logs, если её нет
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Создаем обработчик для записи в файл
    log_file = logs_dir / "masks.log"
    file_handler = logging.FileHandler(log_file, mode=FILE_WRITE_MODE, encoding=ENCODING)
    file_handler.setLevel(logging.DEBUG)

    # Создаем форматтер
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=TIMESTAMP_FORMAT,
    )
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)

    return logger


# Создаем логгер для модуля
logger = _setup_logger()


def only_digits(value: str) -> bool:
    """
    Возвращает True, если строка состоит только из цифр.

    Args:
        value: Строка для проверки

    Returns:
        True, если строка состоит только из цифр, иначе False
    """
    logger.debug(f"Проверка строки на наличие только цифр: {value}")
    result = value.isdigit()
    logger.info(f"Результат проверки: {result}")
    return result


def format_in_blocks(text: str, block_size: int = DEFAULT_BLOCK_SIZE) -> str:
    """
    Возвращает строку, разбитую пробелами на блоки по block_size символов.

    Args:
        text: Строка для форматирования
        block_size: Размер блока (по умолчанию 4)

    Returns:
        Строка, разбитая пробелами на блоки указанного размера
    """
    logger.debug(f"Форматирование строки в блоки: text={text}, block_size={block_size}")
    if not text:
        logger.debug("Пустая строка, возврат без изменений")
        return text
    result = " ".join(text[i : i + block_size] for i in range(0, len(text), block_size))
    logger.info(f"Результат форматирования: {result}")
    return result


def get_mask_card_number(card_number: Union[int, str]) -> str:
    """
    Маскирует номер карты.

    По умолчанию показываются первые 6 и последние 4 цифры, остальное скрывается звёздочками.
    Для классического 16-значного PAN формируется вид: "XXXX XX** **** XXXX".

    Args:
        card_number: Номер карты (целое число или строка из цифр)

    Returns:
        Замаскированный номер карты в виде строки

    Raises:
        ValueError: если встречаются нецифровые символы или длина вне [13, 19]
    """
    logger.debug(f"Начало маскирования номера карты: {type(card_number)}")
    card_str = str(card_number).strip()

    if not only_digits(card_str):
        logger.error(f"Номер карты содержит нецифровые символы: {card_str}")
        raise ValueError("Номер карты должен содержать только цифры")

    length = len(card_str)
    if length < MIN_CARD_LENGTH or length > MAX_CARD_LENGTH:
        logger.error(f"Некорректная длина номера карты: {length}")
        raise ValueError(f"Длина номера карты должна быть от {MIN_CARD_LENGTH} до {MAX_CARD_LENGTH} цифр")

    logger.debug(f"Длина номера карты: {length}")

    # Для 16-значного номера фиксированная расстановка пробелов: XXXX XX** **** XXXX
    if length == STANDARD_CARD_LENGTH:
        masked_number = f"{card_str[:4]} {card_str[4:6]}** **** {card_str[-4:]}"
    else:
        # Для прочих длин: первые 6, звёздочки, последние 4
        first6 = card_str[:FIRST_VISIBLE_DIGITS]
        last4 = card_str[-LAST_VISIBLE_DIGITS:]
        middle_len = max(0, length - FIRST_VISIBLE_DIGITS - LAST_VISIBLE_DIGITS)
        masked_middle = "*" * middle_len
        masked_raw = f"{first6}{masked_middle}{last4}"
        # Возвращаем строку, разбитую пробелами каждые 4 символа
        masked_number = format_in_blocks(masked_raw)

    logger.info(f"Номер карты успешно замаскирован, длина: {length}")
    return masked_number


def get_mask_account(account_number: Union[int, str]) -> str:
    """
    Маскирует номер счёта: показывает только последние 4 цифры, добавляя префикс "**".

    Args:
        account_number: Номер счёта (целое число или строка из цифр)

    Returns:
        Замаскированный номер счёта в виде строки

    Raises:
        ValueError: если встречаются нецифровые символы
    """
    logger.debug(f"Начало маскирования номера счета: {type(account_number)}")
    acc_str = str(account_number).strip()

    if not only_digits(acc_str):
        logger.error(f"Номер счета содержит нецифровые символы: {acc_str}")
        raise ValueError("Номер счёта должен содержать только цифры")

    tail = acc_str[-MIN_ACCOUNT_TAIL_LENGTH:] if len(acc_str) >= MIN_ACCOUNT_TAIL_LENGTH else acc_str
    masked_account = f"{ACCOUNT_MASK_PREFIX}{tail}"
    logger.info(f"Номер счета успешно замаскирован, длина: {len(acc_str)}")
    # Для маски счёта пробелы не требуются
    return masked_account
