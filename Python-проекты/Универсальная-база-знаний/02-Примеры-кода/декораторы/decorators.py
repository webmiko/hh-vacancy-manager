"""Примеры декораторов для логирования и обработки ошибок.

> **Дата добавления/обновления:** 2024-12-19
> **Категория:** Декораторы
> **Связанные модули:**
>   - `обработка-данных/spending_analysis.py` - использование декораторов для сохранения отчетов
> **Учебные материалы:**
>   - [01-Учебные-материалы/03-Функции/Декораторы.md](../../01-Учебные-материалы/03-Функции/Декораторы.md)

Этот модуль демонстрирует создание декораторов для логирования выполнения функций
и обработки ошибок.

Когда использовать:
- При необходимости логирования выполнения функций
- При обработке ошибок в функциях
- При расширении функциональности функций без изменения их кода

Особенности:
- Декоратор с параметрами
- Логирование в файл или консоль
- Обработка различных типов ошибок
"""

import sys
from datetime import datetime
from typing import IO, Any, Callable, Optional

# Константы модуля
DEFAULT_LOG_FILE = "logfile.txt"
ENCODING = "utf-8"
FILE_APPEND_MODE = "a"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def log(filename: Optional[str] = DEFAULT_LOG_FILE) -> Callable[..., Any]:
    """
    Декоратор для логирования начала и конца выполнения функции,
    а также ее результатов или возникших ошибок.

    Args:
        filename: Имя файла для записи логов. По умолчанию используется
                 файл "logfile.txt". Если передано значение None или пустая строка,
                 логи выводятся в консоль.

    Returns:
        Callable: Декорированная функция
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Определяем, куда выводить логи
            log_output: IO[str]
            if filename:
                log_output = open(filename, FILE_APPEND_MODE, encoding=ENCODING)
                is_file_output = True
            else:
                log_output = sys.stdout
                is_file_output = False

            try:
                # Выполняем функцию
                result = func(*args, **kwargs)
                # Записываем успешное выполнение
                timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
                log_output.write(f"[{timestamp}] {func.__name__} ok\n")
                # Сбрасываем буфер, если вывод в консоль
                if not is_file_output:
                    log_output.flush()
                return result
            except Exception as e:
                # Записываем ошибку
                timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
                error_type = type(e).__name__
                error_message = f"[{timestamp}] {func.__name__} error: {error_type}. "

                if isinstance(e, ZeroDivisionError):
                    error_message += f"Деление на ноль невозможно! Inputs: {args}, {kwargs}\n"
                else:
                    error_message += f"Inputs: {args}, {kwargs}\n"

                log_output.write(error_message)
                # Сбрасываем буфер, если вывод в консоль
                if not is_file_output:
                    log_output.flush()
                raise
            finally:
                # Закрываем файл, если он был открыт
                if is_file_output:
                    log_output.close()

        return wrapper

    return decorator
