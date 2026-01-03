import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List


def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля utils.

    Returns:
        Настроенный логгер для модуля utils
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "utils.log"
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


def load_transactions_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает список транзакций из JSON-файла.

    Args:
        file_path: Путь до JSON-файла с транзакциями

    Returns:
        Список словарей с данными о финансовых транзакциях.
        Возвращает пустой список, если:
        - файл не найден
        - файл пустой
        - файл содержит не список (например, словарь)
        - произошла ошибка при парсинге JSON
    """
    logger.debug(f"Начало загрузки транзакций из файла: {file_path}")

    # Проверяем существование файла
    if not os.path.exists(file_path):
        logger.warning(f"Файл не найден: {file_path}")
        return []

    try:
        # Открываем файл в режиме чтения
        with open(file_path, "r", encoding="utf-8") as file:
            # Читаем содержимое файла
            content = file.read().strip()

            # Если файл пустой, возвращаем пустой список
            if not content:
                logger.warning(f"Файл пустой: {file_path}")
                return []

            # Парсим JSON
            data = json.loads(content)

            # Проверяем, что результат является списком
            if not isinstance(data, list):
                logger.warning(f"Файл содержит не список: {file_path}, тип: {type(data)}")
                return []

            # Возвращаем список транзакций
            logger.info(f"Успешно загружено транзакций: {len(data)} из файла {file_path}")
            return data

    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        # Обрабатываем возможные ошибки:
        # - FileNotFoundError: файл не найден (хотя мы уже проверили через os.path.exists)
        # - json.JSONDecodeError: невалидный JSON
        # - OSError: ошибки при чтении файла
        logger.error(f"Ошибка при загрузке файла {file_path}: {type(e).__name__} - {e}")
        return []
