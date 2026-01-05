"""Вспомогательные функции для работы с вводом пользователя.

Модуль содержит функции для валидации и обработки пользовательского ввода.
"""

# 1. Импорты стандартной библиотеки
from typing import Optional

# 2. Импорты сторонних библиотек
# (нет сторонних библиотек)

# 3. Импорты из проекта
# (нет локальных импортов)

# 4. Константы модуля
MIN_TOP_N = 1
MAX_TOP_N = 1000


def validate_top_n(value: str) -> Optional[int]:
    """
    Валидирует значение для топ N вакансий.

    Args:
        value: Строка с числом

    Returns:
        Валидное число или None при ошибке

    Example:
        >>> validate_top_n("10")
        10
        >>> validate_top_n("-5")
        None
    """
    try:
        num = int(value.strip())
        if MIN_TOP_N <= num <= MAX_TOP_N:
            return num
        return None
    except (ValueError, AttributeError):
        return None


def validate_keyword(value: str) -> Optional[str]:
    """
    Валидирует ключевое слово для поиска.

    Args:
        value: Строка с ключевым словом

    Returns:
        Валидное ключевое слово или None при ошибке

    Example:
        >>> validate_keyword("Python")
        'Python'
        >>> validate_keyword("   ")
        None
    """
    if not value or not value.strip():
        return None

    return value.strip()
