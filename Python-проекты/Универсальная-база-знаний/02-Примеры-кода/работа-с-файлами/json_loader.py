"""Пример загрузки данных из JSON файла с созданием объектов классов.

> **Дата добавления/обновления:** 2026-01-02
> **Категория:** Работа с файлами
> **Связанные модули:** 
>   - `работа-с-файлами/data_loading.py` - загрузка данных из Excel
>   - `работа-с-файлами/csv_loader.py` - загрузка данных из CSV
>   - `ооп/oop_classes.py` - примеры классов для создания объектов
>   - `ооп/advanced_oop.py` - продвинутые примеры ООП с обработкой исключений
> **Учебные материалы:** 
>   - [01-Учебные-материалы/06-Данные/JSON-requests-datetime.md](../../01-Учебные-материалы/06-Данные/JSON-requests-datetime.md)
>   - [01-Учебные-материалы/10-ООП/Классы-и-объекты.md](../../01-Учебные-материалы/10-ООП/Классы-и-объекты.md)
>   - [01-Учебные-материалы/12-Исключения/Блоки-try-except.md](../../01-Учебные-материалы/12-Исключения/Блоки-try-except.md)

Этот модуль демонстрирует загрузку структурированных данных из JSON файла
и создание объектов классов на основе этих данных.

Когда использовать:
- При загрузке конфигурации из JSON
- При загрузке данных для создания объектов классов
- При работе с вложенными структурами данных в JSON

Особенности:
- Обработка всех типов ошибок (JSONDecodeError, KeyError, IOError)
- Логирование всех операций с защитой конфиденциальных данных
- Защита от изменений исходного списка
- Возврат безопасных значений по умолчанию
- Валидация данных перед созданием объектов
- Обработка пользовательских исключений
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

# Константы модуля
ENCODING = "utf-8"
FILE_READ_MODE = "r"
FILE_APPEND_MODE = "a"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_RETURN_VALUE: List[dict] = []


def _sanitize_path(file_path: str) -> str:
    """
    Очищает путь к файлу от конфиденциальной информации.

    Удаляет полные пути, оставляя только имя файла для защиты
    конфиденциальной информации о структуре файловой системы.

    Args:
        file_path: Полный путь к файлу

    Returns:
        Только имя файла или относительный путь
    """
    path = Path(file_path)
    # Если путь относительный, возвращаем как есть
    if not path.is_absolute():
        return file_path
    # Для абсолютных путей возвращаем только имя файла
    return path.name


def _sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Очищает данные от конфиденциальной информации для логирования.

    Оставляет только структуру (ключи) без значений для защиты
    конфиденциальных данных.

    Args:
        data: Словарь с данными

    Returns:
        Словарь с ключами, но без значений
    """
    sanitized: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized[key] = _sanitize_data(value)
        elif isinstance(value, list):
            sanitized[key] = f"[список из {len(value)} элементов]"
        else:
            sanitized[key] = "[скрыто]"
    return sanitized


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

    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "json_loader.log"
    file_handler = logging.FileHandler(log_file, mode=FILE_APPEND_MODE, encoding=ENCODING)
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


def load_categories_from_json(file_path: str) -> List[dict]:
    """
    Загружает категории и продукты из JSON-файла.

    Функция читает JSON-файл, содержащий список категорий с продуктами,
    и возвращает структурированные данные. Демонстрирует защиту конфиденциальных
    данных при логировании.

    Args:
        file_path: Путь к JSON-файлу с данными о категориях и продуктах

    Returns:
        Список словарей с данными категорий. Возвращает пустой список при ошибке.

    Example:
        >>> categories = load_categories_from_json("data/products.json")
        >>> assert len(categories) > 0
        >>> assert "name" in categories[0]
        >>> assert "products" in categories[0]
    """
    sanitized_path = _sanitize_path(file_path)
    logger.info(f"Загрузка категорий из файла: {sanitized_path}")

    # Проверка существования файла
    if not Path(file_path).exists():
        logger.warning(f"Файл не найден: {sanitized_path}")
        return DEFAULT_RETURN_VALUE[:]

    try:
        # Чтение JSON из файла
        with open(file_path, FILE_READ_MODE, encoding=ENCODING) as f:
            data = json.load(f)

        # Проверка типа данных
        if not isinstance(data, list):
            logger.warning("Файл содержит не список")
            return DEFAULT_RETURN_VALUE[:]

        # Обработка пустого файла
        if not data:
            logger.warning("Файл содержит пустой список")
            return DEFAULT_RETURN_VALUE[:]

        logger.info(f"Успешно загружено {len(data)} категорий")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE[:]
    except KeyError as e:
        logger.error(f"Отсутствует обязательное поле в JSON: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE[:]
    except (OSError, IOError) as e:
        # Логируем только тип ошибки, без полного пути
        error_msg = str(e).replace(file_path, sanitized_path) if file_path in str(e) else str(e)
        logger.error(f"Ошибка ввода-вывода при работе с файлом {sanitized_path}: {type(e).__name__} - {error_msg}")
        return DEFAULT_RETURN_VALUE[:]
    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка типа данных или значения: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE[:]
    # Не перехватываем все остальные исключения - они должны быть видны
    # согласно принципу "Errors should never pass silently"


def create_objects_from_json(file_path: str, ProductClass: type, CategoryClass: type) -> List[Any]:
    """
    Загружает данные из JSON и создает объекты классов.

    Демонстрирует полный цикл: загрузка JSON → валидация → создание объектов.
    Включает обработку пользовательских исключений и детальное логирование.

    Args:
        file_path: Путь к JSON-файлу
        ProductClass: Класс для создания продуктов (например, Product)
        CategoryClass: Класс для создания категорий (например, Category)

    Returns:
        Список объектов Category. Возвращает пустой список при ошибке.

    Example:
        >>> from ооп.oop_classes import Product, Category
        >>> categories = create_objects_from_json("data/products.json", Product, Category)
        >>> assert len(categories) > 0
        >>> assert isinstance(categories[0], Category)
    """
    sanitized_path = _sanitize_path(file_path)
    logger.info(f"Загрузка категорий из файла: {sanitized_path}")

    # Проверка существования файла
    if not Path(file_path).exists():
        logger.warning(f"Файл не найден: {sanitized_path}")
        return []

    try:
        # Чтение JSON из файла
        with open(file_path, FILE_READ_MODE, encoding=ENCODING) as f:
            data = json.load(f)

        # Проверка типа данных
        if not isinstance(data, list):
            logger.warning("Файл содержит не список")
            return []

        # Обработка пустого файла
        if not data:
            logger.warning("Файл содержит пустой список")
            return []

        # Создание объектов Category и Product
        categories: List[Any] = []

        for category_data in data:
            # Проверка структуры данных категории
            if not isinstance(category_data, dict):
                logger.warning(f"Элемент категории должен быть словарем, получен {type(category_data).__name__}")
                continue

            # Проверка обязательных ключей категории
            if "name" not in category_data or "description" not in category_data:
                sanitized_category = _sanitize_data(category_data)
                logger.warning(f"Отсутствуют обязательные ключи в категории: {sanitized_category}")
                continue

            # Валидация типов данных категории
            if not isinstance(category_data["name"], str):
                logger.warning(f"name категории должен быть строкой, получен {type(category_data['name']).__name__}")
                continue
            if not isinstance(category_data["description"], str):
                logger.warning(
                    f"description категории должен быть строкой, получен {type(category_data['description']).__name__}"
                )
                continue

            # Создание продуктов для категории
            products: List[Any] = []

            for product_data in category_data.get("products", []):
                if not isinstance(product_data, dict):
                    logger.warning(f"Элемент продукта должен быть словарем, получен {type(product_data).__name__}")
                    continue

                try:
                    # Используем new_product для валидации и создания продукта (если метод существует)
                    if hasattr(ProductClass, "new_product"):
                        product = ProductClass.new_product(product_data)
                    else:
                        # Создание продукта напрямую
                        product = ProductClass(
                            name=product_data["name"],
                            description=product_data["description"],
                            price=float(product_data["price"]),
                            quantity=int(product_data["quantity"]),
                        )
                    products.append(product)
                except (KeyError, TypeError, ValueError) as e:
                    sanitized_product = _sanitize_data(product_data)
                    logger.warning(
                        f"Ошибка при создании продукта: {type(e).__name__} - {e}, структура данных: {sanitized_product}"
                    )
                    continue

            # Создание категории
            try:
                category = CategoryClass(
                    name=category_data["name"],
                    description=category_data["description"],
                    products=products,
                )
                categories.append(category)
            except (TypeError, ValueError) as e:
                logger.warning(f"Ошибка при создании категории: {type(e).__name__} - {e}")
                continue

        logger.info(f"Успешно загружено {len(categories)} категорий")
        return categories

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {type(e).__name__} - {e}")
        return []
    except KeyError as e:
        logger.error(f"Отсутствует обязательное поле в JSON: {type(e).__name__} - {e}")
        return []
    except (OSError, IOError) as e:
        sanitized_path = _sanitize_path(file_path)
        # Логируем только тип ошибки, без полного пути
        error_msg = str(e).replace(file_path, sanitized_path) if file_path in str(e) else str(e)
        logger.error(f"Ошибка ввода-вывода при работе с файлом {sanitized_path}: {type(e).__name__} - {error_msg}")
        return []
    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка типа данных или значения: {type(e).__name__} - {e}")
        return []
    # Не перехватываем все остальные исключения - они должны быть видны
    # согласно принципу "Errors should never pass silently"


# Пример использования
if __name__ == "__main__":
    # Загрузка данных из JSON
    categories_data = load_categories_from_json("data/products.json")

    if categories_data:
        print(f"Загружено категорий: {len(categories_data)}")

        for category in categories_data:
            print(f"\nКатегория: {category['name']}")
            print(f"Описание: {category['description']}")
            print(f"Количество продуктов: {len(category.get('products', []))}")

            for product in category.get("products", []):
                print(f"  - {product['name']}: {product['price']} руб. (в наличии: {product['quantity']})")
    else:
        print("Не удалось загрузить данные")

