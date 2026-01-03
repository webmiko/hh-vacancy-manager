"""Helper модуль для упрощения импорта bank-code из проектов.

Этот модуль автоматически добавляет bank-code в sys.path,
что позволяет импортировать модули bank-code из любого проекта.

Использование в структуре Мои_проекты/:
    # В начале любого файла проекта (например, project1/src/main.py)
    import sys
    from pathlib import Path
    
    # Определяем путь к bank-code (на 2 уровня выше от проекта)
    # Мои_проекты/project1/src/main.py -> Мои_проекты/bank-code
    bank_code_path = Path(__file__).parent.parent.parent / "bank-code"
    sys.path.insert(0, str(bank_code_path))
    
    # Теперь можно импортировать bank-code
    from bank_code.data_loading import load_transactions_from_excel
    from bank_code.date_operations import format_date
"""

import sys
from pathlib import Path

# Определяем путь к bank-code
# Если helpers.py находится в bank-code/, то bank-code - это родительская директория
_BANK_CODE_PATH = Path(__file__).parent

# Добавляем в sys.path, если еще не добавлен
if _BANK_CODE_PATH.exists() and str(_BANK_CODE_PATH) not in sys.path:
    sys.path.insert(0, str(_BANK_CODE_PATH))


def get_bank_code_path() -> Path:
    """
    Возвращает путь к bank-code.
    
    Returns:
        Path к директории bank-code
    """
    return _BANK_CODE_PATH


def is_bank_code_available() -> bool:
    """
    Проверяет, доступен ли bank-code для импорта.
    
    Returns:
        True, если bank-code доступен, False иначе
    """
    try:
        import bank_code  # noqa: F401
        return True
    except ImportError:
        return False

