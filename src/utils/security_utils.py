"""Утилиты для проверки безопасности и защиты конфиденциальных данных.

Модуль содержит функции для проверки логов и кода на наличие
конфиденциальных данных, которые не должны попадать в репозиторий.
"""

# 1. Импорты стандартной библиотеки
import logging
import re
from pathlib import Path
from typing import List, Tuple

# 2. Импорты сторонних библиотек
# (нет сторонних библиотек)

# 3. Импорты из проекта
# (нет локальных импортов)

# 4. Константы модуля
LOGS_DIR = "logs"
SENSITIVE_PATTERNS = [
    (r"api[_-]?key\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{20,})['\"]?", "API ключ"),
    (r"token\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{20,})['\"]?", "Токен"),
    (r"password\s*[:=]\s*['\"]?([^\s'\"]{8,})['\"]?", "Пароль"),
    (r"secret\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{20,})['\"]?", "Секрет"),
    (r"apikey\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{20,})['\"]?", "API ключ"),
    (r"authorization\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{20,})['\"]?", "Токен авторизации"),
    (r"bearer\s+([a-zA-Z0-9_-]{20,})", "Bearer токен"),
    (r"x-api-key\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{20,})['\"]?", "API ключ"),
]

DEFAULT_RETURN_VALUE: List[Tuple[str, str, int]] = []


def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля.

    Returns:
        Настроенный логгер для модуля
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent.parent / LOGS_DIR
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "security_utils.log"
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# 5. Создаем логгер для модуля
logger = _setup_logger()


def check_logs_for_leaks(logs_dir: str = LOGS_DIR) -> List[Tuple[str, str, int]]:
    """
    Проверяет логи на наличие конфиденциальных данных.

    Args:
        logs_dir: Путь к директории с логами. По умолчанию "logs"

    Returns:
        Список кортежей (имя_файла, тип_утечки, номер_строки).
        Возвращает пустой список при ошибке или если утечек не найдено.

    Example:
        >>> leaks = check_logs_for_leaks()
        >>> if leaks:
        ...     print(f"Найдено {len(leaks)} потенциальных утечек!")
    """
    logger.info(f"Начало проверки логов на утечку информации в директории: {logs_dir}")

    leaks: List[Tuple[str, str, int]] = []
    logs_path = Path(__file__).parent.parent.parent / logs_dir

    if not logs_path.exists():
        logger.warning(f"Директория с логами не найдена: {logs_path}")
        return DEFAULT_RETURN_VALUE

    try:
        log_files = list(logs_path.glob("*.log"))

        if not log_files:
            logger.info("Логи не найдены для проверки")
            return DEFAULT_RETURN_VALUE

        for log_file in log_files:
            logger.debug(f"Проверка файла: {log_file.name}")

            try:
                with open(log_file, "r", encoding="utf-8") as file:
                    for line_num, line in enumerate(file, start=1):
                        for pattern, leak_type in SENSITIVE_PATTERNS:
                            matches = re.finditer(pattern, line, re.IGNORECASE)
                            for match in matches:
                                # Маскируем найденное значение для безопасности
                                found_value = match.group(1) if match.groups() else match.group(0)
                                masked_value = (
                                    found_value[:4] + "..." + found_value[-4:] if len(found_value) > 8 else "***"
                                )

                                logger.warning(
                                    f"Потенциальная утечка в {log_file.name}:{line_num} - "
                                    f"{leak_type} (значение: {masked_value})"
                                )
                                leaks.append((log_file.name, leak_type, line_num))

            except PermissionError as e:
                # Критично: проблемы с правами доступа требуют внимания админа
                logger.critical(f"КРИТИЧНО: Отсутствуют права доступа к файлу логов {log_file.name}: {e}")
                continue
            except UnicodeDecodeError as e:
                logger.error(f"Ошибка декодирования файла логов {log_file.name}: {type(e).__name__} - {e}")
                continue
            except OSError as e:
                logger.error(f"Ошибка ввода-вывода при чтении файла логов {log_file.name}: {type(e).__name__} - {e}")
                continue

        if leaks:
            logger.warning(f"Найдено {len(leaks)} потенциальных утечек в логах")
        else:
            logger.info("Утечек в логах не обнаружено")

        return leaks

    except PermissionError as e:
        # Критично: проблемы с правами доступа требуют внимания админа
        logger.critical(f"КРИТИЧНО: Отсутствуют права доступа к директории логов {logs_dir}: {e}")
        return DEFAULT_RETURN_VALUE
    except OSError as e:
        logger.error(f"Ошибка ввода-вывода при проверке логов: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE
    except Exception as e:
        # Исключительный случай: обработка любых других неожиданных ошибок
        # для предотвращения падения программы при проверке безопасности
        logger.critical(f"Критическая неожиданная ошибка при проверке логов: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE


def print_leaks_report(leaks: List[Tuple[str, str, int]]) -> None:
    """
    Выводит отчет о найденных утечках в консоль.

    Args:
        leaks: Список кортежей (имя_файла, тип_утечки, номер_строки)

    Example:
        >>> leaks = check_logs_for_leaks()
        >>> print_leaks_report(leaks)
    """
    if not leaks:
        print("✓ Утечек в логах не обнаружено")
        return

    print(f"\n⚠️  ВНИМАНИЕ: Найдено {len(leaks)} потенциальных утечек конфиденциальных данных!\n")
    print("Детали:")

    for filename, leak_type, line_num in leaks:
        print(f"  - {filename}:{line_num} - {leak_type}")

    print("\nРекомендации:")
    print("  1. Удалите конфиденциальные данные из логов")
    print("  2. Проверьте код, который логирует эти данные")
    print("  3. Используйте переменные окружения для хранения секретов")
    print("  4. НЕ коммитьте файлы с конфиденциальными данными\n")


if __name__ == "__main__":
    """Запуск проверки логов при прямом вызове модуля."""
    found_leaks = check_logs_for_leaks()
    print_leaks_report(found_leaks)
