"""Примеры использования генераторов для работы с данными.

> **Дата добавления/обновления:** 2024-12-19
> **Категория:** Генераторы
> **Связанные модули:**
>   - `валидация-и-форматирование/masks.py` - форматирование номеров карт
>   - `обработка-данных/processing.py` - фильтрация транзакций
> **Учебные материалы:**
>   - [01-Учебные-материалы/04-Генераторы/Включения-генераторы.md](../../01-Учебные-материалы/04-Генераторы/Включения-генераторы.md)

Этот модуль демонстрирует использование генераторов для работы с данными
без загрузки всего объема в память.

Когда использовать:
- При работе с большими объемами данных
- При фильтрации данных по условиям
- При генерации последовательностей данных

Особенности:
- Генераторы для фильтрации транзакций
- Генераторы для создания номеров карт
- Эффективное использование памяти
"""

import random
from typing import Any, Dict, Iterator, List


def filter_by_currency(transactions: List[Dict[str, Any]], currency_code: str) -> Iterator[Dict[str, Any]]:
    """
    Фильтрует транзакции по заданной валюте.

    Args:
        transactions: Список словарей с транзакциями
        currency_code: Код валюты для фильтрации (например, "USD")

    Yields:
        Словари транзакций, у которых валюта соответствует заданной
    """
    for transaction in transactions:
        if transaction.get("operationAmount", {}).get("currency", {}).get("code") == currency_code:
            yield transaction


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Возвращает описание каждой операции по очереди.

    Args:
        transactions: Список словарей с транзакциями

    Yields:
        Описание операции из каждой транзакции
    """
    for transaction in transactions:
        yield transaction.get("description", "")


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """
    Генерирует номера банковских карт в формате XXXX XXXX XXXX XXXX.
    Генерирует номера от 0000 0000 0000 0001 до 9999 9999 9999 9999.

    Args:
        start: Начальное значение для генерации
        end: Конечное значение для генерации

    Yields:
        Отформатированные номера карт
    """
    for number in range(start, end + 1):
        # Форматируем число в 16-значную строку с группировкой по 4 цифры
        card = str(number)
        # Дополняем нулями слева до 16 цифр
        while len(card) < 16:
            card = "0" + card
        yield f"{card[:4]} {card[4:8]} {card[8:12]} {card[12:]}"


def random_card_number_generator(count: int) -> Iterator[str]:
    """
    Генерирует случайные номера банковских карт в формате XXXX XXXX XXXX XXXX.
    Генерирует указанное количество случайных 16-значных номеров карт.

    Args:
        count: Количество случайных номеров карт для генерации

    Yields:
        Случайные отформатированные номера карт
    """
    for _ in range(count):
        # Генерируем случайное 16-значное число
        card_number = "".join(str(random.randint(0, 9)) for _ in range(16))
        # Разделяем на группы по 4 цифры и добавляем пробелы
        formatted = f"{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:]}"
        yield formatted
