"""Тесты для модуля загрузки данных из JSON."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from src.category import Category

if TYPE_CHECKING:
    from pytest import LogCaptureFixture
from src.data_loader import (
    DEFAULT_RETURN_VALUE,
    ENCODING,
    FILE_APPEND_MODE,
    FILE_READ_MODE,
    TIMESTAMP_FORMAT,
    load_categories_from_json,
)
from src.product import Product


class TestLoadCategoriesFromJson:
    """Тесты для функции load_categories_from_json."""

    def test_load_categories_from_json_success(self, tmp_path: Path) -> None:
        """Тест успешной загрузки категорий из JSON."""
        # Arrange
        json_data = [
            {
                "name": "Смартфоны",
                "description": "Смартфоны для коммуникации",
                "products": [
                    {
                        "name": "Samsung Galaxy C23 Ultra",
                        "description": "256GB, Серый цвет, 200MP камера",
                        "price": 180000.0,
                        "quantity": 5,
                    },
                    {
                        "name": "Iphone 15",
                        "description": "512GB, Gray space",
                        "price": 210000.0,
                        "quantity": 8,
                    },
                ],
            },
            {
                "name": "Телевизоры",
                "description": "Современные телевизоры",
                "products": [
                    {
                        "name": '55" QLED 4K',
                        "description": "Фоновая подсветка",
                        "price": 123000.0,
                        "quantity": 7,
                    },
                ],
            },
        ]

        json_file = tmp_path / "products.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert len(categories) == 2
        assert isinstance(categories[0], Category)
        assert isinstance(categories[1], Category)
        assert categories[0].name == "Смартфоны"
        assert categories[1].name == "Телевизоры"
        assert len(categories[0]._Category__products) == 2  # type: ignore[attr-defined]
        assert len(categories[1]._Category__products) == 1  # type: ignore[attr-defined]

    def test_load_categories_from_json_products_are_objects(self, tmp_path: Path) -> None:
        """Тест, что продукты создаются как объекты Product."""
        # Arrange
        json_data = [
            {
                "name": "Смартфоны",
                "description": "Смартфоны для коммуникации",
                "products": [
                    {
                        "name": "Samsung Galaxy C23 Ultra",
                        "description": "256GB, Серый цвет, 200MP камера",
                        "price": 180000.0,
                        "quantity": 5,
                    },
                ],
            },
        ]

        json_file = tmp_path / "products.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert len(categories) == 1
        assert len(categories[0]._Category__products) == 1  # type: ignore[attr-defined]
        assert isinstance(categories[0]._Category__products[0], Product)  # type: ignore[attr-defined]
        assert categories[0]._Category__products[0].name == "Samsung Galaxy C23 Ultra"  # type: ignore[attr-defined]
        assert categories[0]._Category__products[0].price == 180000.0  # type: ignore[attr-defined]
        assert categories[0]._Category__products[0].quantity == 5  # type: ignore[attr-defined]
        assert "Samsung Galaxy C23 Ultra" in categories[0].products

    def test_load_categories_from_json_empty_products_list(self, tmp_path: Path) -> None:
        """Тест загрузки категории с пустым списком продуктов."""
        # Arrange
        json_data = [
            {
                "name": "Пустая категория",
                "description": "Категория без продуктов",
                "products": [],
            },
        ]

        json_file = tmp_path / "products.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert len(categories) == 1
        assert categories[0].name == "Пустая категория"
        assert len(categories[0]._Category__products) == 0  # type: ignore[attr-defined]
        assert categories[0].products == ""

    def test_load_categories_from_json_file_not_found(self) -> None:
        """Тест обработки ошибки FileNotFoundError."""
        # Arrange
        non_existent_file = "non_existent_file.json"

        # Act
        categories = load_categories_from_json(non_existent_file)

        # Assert
        assert categories == []

    def test_load_categories_from_json_invalid_json(self, tmp_path: Path) -> None:
        """Тест обработки ошибки JSONDecodeError."""
        # Arrange
        json_file = tmp_path / "invalid.json"
        with open(json_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert categories == []

    def test_load_categories_from_json_empty_file(self, tmp_path: Path) -> None:
        """Тест обработки пустого файла."""
        # Arrange
        json_file = tmp_path / "empty.json"
        json_file.touch()

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert categories == []

    def test_load_categories_from_json_not_list(self, tmp_path: Path) -> None:
        """Тест обработки случая, когда JSON содержит не список."""
        # Arrange
        json_data = {"name": "Not a list"}

        json_file = tmp_path / "not_list.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert categories == []

    def test_load_categories_from_json_real_file(self) -> None:
        """Тест загрузки из реального файла data/products.json."""
        # Arrange
        json_file = Path(__file__).parent.parent / "data" / "products.json"

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert len(categories) > 0
        assert all(isinstance(cat, Category) for cat in categories)
        assert all(isinstance(prod, Product) for cat in categories for prod in cat._Category__products)  # type: ignore[attr-defined]

    def test_load_categories_from_json_missing_key(self, tmp_path: Path) -> None:
        """Тест обработки ошибки KeyError при отсутствии обязательного поля."""
        # Arrange
        json_data = [
            {
                "name": "Категория без описания",
                # Отсутствует поле "description"
                "products": [
                    {
                        "name": "Продукт",
                        "description": "Описание",
                        "price": 100.0,
                        "quantity": 1,
                    },
                ],
            },
        ]

        json_file = tmp_path / "missing_key.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert categories == []

    def test_load_categories_from_json_missing_product_key(self, tmp_path: Path) -> None:
        """Тест обработки ошибки KeyError при отсутствии поля в продукте."""
        # Arrange
        json_data = [
            {
                "name": "Категория",
                "description": "Описание",
                "products": [
                    {
                        "name": "Продукт",
                        # Отсутствует поле "price"
                        "description": "Описание",
                        "quantity": 1,
                    },
                ],
            },
        ]

        json_file = tmp_path / "missing_product_key.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        # Категория создается, но без продуктов (продукт с ошибкой пропускается)
        assert len(categories) == 1
        assert len(categories[0].get_products()) == 0

    def test_load_categories_from_json_missing_products_key(self, tmp_path: Path) -> None:
        """Тест загрузки категории без ключа products (используется .get())."""
        # Arrange
        json_data = [
            {
                "name": "Категория без продуктов",
                "description": "Описание",
                # Отсутствует ключ "products"
            },
        ]

        json_file = tmp_path / "no_products_key.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        categories = load_categories_from_json(str(json_file))

        # Assert
        assert len(categories) == 1
        assert categories[0].name == "Категория без продуктов"
        assert len(categories[0]._Category__products) == 0  # type: ignore[attr-defined]
        assert categories[0].products == ""

    def test_load_categories_from_json_general_exception(self, tmp_path: Path) -> None:
        """Тест обработки общего исключения."""
        # Arrange
        json_file = tmp_path / "test.json"

        # Создаем файл, который вызовет ошибку при чтении
        with open(json_file, "w", encoding="utf-8") as f:
            f.write('{"valid": "json"}')

        # Мокаем open чтобы вызвать общее исключение
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            # Act
            categories = load_categories_from_json(str(json_file))

            # Assert
            assert categories == []

    def test_load_categories_from_json_os_error(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест обработки OSError."""
        # Arrange
        json_file = tmp_path / "test.json"
        json_file.touch()

        # Мокаем open чтобы вызвать OSError
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            # Act
            with caplog.at_level(logging.ERROR):
                categories = load_categories_from_json(str(json_file))

            # Assert
            assert categories == []
            assert "Ошибка ввода-вывода при работе с файлом" in caplog.text

    def test_load_categories_from_json_io_error(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест обработки IOError."""
        # Arrange
        json_file = tmp_path / "test.json"
        json_file.touch()

        # Мокаем open чтобы вызвать IOError
        with patch("builtins.open", side_effect=IOError("Disk full")):
            # Act
            with caplog.at_level(logging.ERROR):
                categories = load_categories_from_json(str(json_file))

            # Assert
            assert categories == []
            assert "Ошибка ввода-вывода при работе с файлом" in caplog.text

    def test_load_categories_from_json_value_error(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест обработки ValueError."""
        # Arrange
        json_file = tmp_path / "test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "name": "Test",
                        "description": "Desc",
                        "products": [{"name": "Prod", "description": "Desc", "price": 100.0, "quantity": 1}],
                    }
                ],
                f,
            )

        # Мокаем Product.new_product чтобы вызвать ValueError при создании продукта
        with patch("src.data_loader.Product.new_product", side_effect=ValueError("Invalid value")):
            # Act
            with caplog.at_level(logging.WARNING):
                categories = load_categories_from_json(str(json_file))

            # Assert
            # Категория создается, но без продуктов (продукт с ошибкой пропускается)
            assert len(categories) == 1
            assert len(categories[0].get_products()) == 0
            assert "Ошибка при создании продукта" in caplog.text

    def test_load_categories_from_json_type_error(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест обработки TypeError."""
        # Arrange
        json_file = tmp_path / "test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([{"name": "Test", "description": "Desc", "products": []}], f)

        # Мокаем Category.__init__ чтобы вызвать TypeError
        with patch("src.data_loader.Category", side_effect=TypeError("Invalid type")):
            # Act
            with caplog.at_level(logging.WARNING):
                load_categories_from_json(str(json_file))

            # Assert
            # Категория с ошибкой пропускается, но другие категории могут быть созданы
            assert "Ошибка при создании категории" in caplog.text

    def test_load_categories_from_json_logging_info(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест логирования при успешной загрузке."""
        # Arrange
        json_data = [
            {
                "name": "Тест",
                "description": "Описание",
                "products": [],
            },
        ]

        json_file = tmp_path / "test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.INFO):
            categories = load_categories_from_json(str(json_file))

        # Assert
        assert len(categories) == 1
        assert "Загрузка категорий из файла" in caplog.text
        assert "Успешно загружено" in caplog.text

    def test_load_categories_from_json_logging_warning_file_not_found(self, caplog: "LogCaptureFixture") -> None:
        """Тест логирования при отсутствии файла."""
        # Arrange
        non_existent_file = "non_existent_file.json"

        # Act
        with caplog.at_level(logging.WARNING):
            categories = load_categories_from_json(non_existent_file)

        # Assert
        assert categories == []
        assert "Файл не найден" in caplog.text

    def test_load_categories_from_json_logging_warning_not_list(
        self, tmp_path: Path, caplog: "LogCaptureFixture"
    ) -> None:
        """Тест логирования при неверном типе данных."""
        # Arrange
        json_data = {"name": "Not a list"}

        json_file = tmp_path / "not_list.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.WARNING):
            categories = load_categories_from_json(str(json_file))

        # Assert
        assert categories == []
        assert "Файл содержит не список" in caplog.text

    def test_load_categories_from_json_logging_warning_empty_list(
        self, tmp_path: Path, caplog: "LogCaptureFixture"
    ) -> None:
        """Тест логирования при пустом списке."""
        # Arrange
        json_data: list[dict[str, object]] = []

        json_file = tmp_path / "empty_list.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.WARNING):
            categories = load_categories_from_json(str(json_file))

        # Assert
        assert categories == []
        assert "Файл содержит пустой список" in caplog.text

    def test_load_categories_from_json_logging_error_json_decode(
        self, tmp_path: Path, caplog: "LogCaptureFixture"
    ) -> None:
        """Тест логирования при ошибке парсинга JSON."""
        # Arrange
        json_file = tmp_path / "invalid.json"
        with open(json_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        # Act
        with caplog.at_level(logging.ERROR):
            categories = load_categories_from_json(str(json_file))

        # Assert
        assert categories == []
        assert "Ошибка парсинга JSON" in caplog.text

    def test_load_categories_from_json_logging_error_key_error(
        self, tmp_path: Path, caplog: "LogCaptureFixture"
    ) -> None:
        """Тест логирования при отсутствии обязательного поля."""
        # Arrange
        json_data = [
            {
                "name": "Категория",
                # Отсутствует поле "description"
                "products": [],
            },
        ]

        json_file = tmp_path / "missing_key.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.WARNING):
            categories = load_categories_from_json(str(json_file))

        # Assert
        # Категория без обязательных ключей пропускается
        assert categories == []
        assert "Отсутствуют обязательные ключи в категории" in caplog.text or "name категории" in caplog.text

    def test_load_categories_from_json_category_not_dict(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест обработки случая, когда элемент категории не является словарем."""
        # Arrange
        json_data = [
            "not a dict",  # Элемент категории не словарь
            {
                "name": "Валидная категория",
                "description": "Описание",
                "products": [],
            },
        ]

        json_file = tmp_path / "category_not_dict.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.WARNING):
            categories = load_categories_from_json(str(json_file))

        # Assert
        # Невалидная категория пропускается, валидная создается
        assert len(categories) == 1
        assert categories[0].name == "Валидная категория"
        assert "Элемент категории должен быть словарем" in caplog.text

    def test_load_categories_from_json_category_name_not_string(
        self, tmp_path: Path, caplog: "LogCaptureFixture"
    ) -> None:
        """Тест обработки случая, когда name категории не является строкой."""
        # Arrange
        json_data = [
            {
                "name": 123,  # name не строка
                "description": "Описание",
                "products": [],
            },
            {
                "name": "Валидная категория",
                "description": "Описание",
                "products": [],
            },
        ]

        json_file = tmp_path / "name_not_string.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.WARNING):
            categories = load_categories_from_json(str(json_file))

        # Assert
        # Невалидная категория пропускается, валидная создается
        assert len(categories) == 1
        assert categories[0].name == "Валидная категория"
        assert "name категории должен быть строкой" in caplog.text

    def test_load_categories_from_json_category_description_not_string(
        self, tmp_path: Path, caplog: "LogCaptureFixture"
    ) -> None:
        """Тест обработки случая, когда description категории не является строкой."""
        # Arrange
        json_data = [
            {
                "name": "Категория",
                "description": 456,  # description не строка
                "products": [],
            },
            {
                "name": "Валидная категория",
                "description": "Описание",
                "products": [],
            },
        ]

        json_file = tmp_path / "description_not_string.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.WARNING):
            categories = load_categories_from_json(str(json_file))

        # Assert
        # Невалидная категория пропускается, валидная создается
        assert len(categories) == 1
        assert categories[0].name == "Валидная категория"
        assert "description категории должен быть строкой" in caplog.text

    def test_load_categories_from_json_product_not_dict(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест обработки случая, когда элемент продукта не является словарем."""
        # Arrange
        json_data = [
            {
                "name": "Категория",
                "description": "Описание",
                "products": [
                    "not a dict",  # Элемент продукта не словарь
                    {
                        "name": "Валидный продукт",
                        "description": "Описание",
                        "price": 100.0,
                        "quantity": 1,
                    },
                ],
            },
        ]

        json_file = tmp_path / "product_not_dict.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.WARNING):
            categories = load_categories_from_json(str(json_file))

        # Assert
        # Невалидный продукт пропускается, валидный создается
        assert len(categories) == 1
        assert len(categories[0].get_products()) == 1
        assert categories[0].get_products()[0].name == "Валидный продукт"
        assert "Элемент продукта должен быть словарем" in caplog.text

    def test_load_categories_from_json_nested_dict_sanitization(
        self, tmp_path: Path, caplog: "LogCaptureFixture"
    ) -> None:
        """Тест обработки вложенных словарей в _sanitize_data (рекурсивный вызов)."""
        # Arrange
        json_data = [
            {
                "name": "Категория",
                "description": "Описание",
                "nested_data": {  # Вложенный словарь для тестирования рекурсии
                    "key1": "value1",
                    "key2": {"nested_key": "nested_value"},
                },
                "products": [],
            },
        ]

        json_file = tmp_path / "nested_dict.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Act
        with caplog.at_level(logging.WARNING):
            # Удаляем обязательные ключи, чтобы вызвать _sanitize_data с вложенными словарями
            json_data_missing_key = [
                {
                    "nested_data": {
                        "key1": "value1",
                        "key2": {"nested_key": "nested_value"},
                    },
                    # Отсутствуют name и description
                },
            ]
            json_file_missing = tmp_path / "nested_dict_missing.json"
            with open(json_file_missing, "w", encoding="utf-8") as f:
                json.dump(json_data_missing_key, f, ensure_ascii=False, indent=2)

            categories = load_categories_from_json(str(json_file_missing))

        # Assert
        # Категория без обязательных ключей пропускается, но _sanitize_data вызывается с вложенными словарями
        assert categories == []
        assert "Отсутствуют обязательные ключи в категории" in caplog.text

    def test_load_categories_from_json_keyerror_exception(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест обработки KeyError при отсутствии обязательных полей в JSON."""
        # Arrange
        json_file = tmp_path / "keyerror.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([{"name": "Test", "description": "Desc", "products": []}], f)

        # Мокаем json.load чтобы вызвать KeyError на уровне парсинга
        # Это может произойти, если json.load вызовет KeyError при доступе к полям
        with patch("src.data_loader.json.load", side_effect=KeyError("missing_key")):
            # Act
            with caplog.at_level(logging.ERROR):
                categories = load_categories_from_json(str(json_file))

            # Assert
            assert categories == []
            assert "Отсутствует обязательное поле в JSON" in caplog.text

    def test_load_categories_from_json_valueerror_typeerror(self, tmp_path: Path, caplog: "LogCaptureFixture") -> None:
        """Тест обработки ValueError и TypeError при загрузке данных."""
        # Arrange
        json_file = tmp_path / "value_type_error.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([{"name": "Test", "description": "Desc", "products": []}], f)

        # Мокаем json.load чтобы вызвать ValueError или TypeError
        with patch("src.data_loader.json.load", side_effect=ValueError("Invalid value")):
            # Act
            with caplog.at_level(logging.ERROR):
                categories = load_categories_from_json(str(json_file))

            # Assert
            assert categories == []
            assert "Ошибка типа данных или значения" in caplog.text

        # Тест для TypeError
        with patch("src.data_loader.json.load", side_effect=TypeError("Invalid type")):
            # Act
            with caplog.at_level(logging.ERROR):
                categories = load_categories_from_json(str(json_file))

            # Assert
            assert categories == []
            assert "Ошибка типа данных или значения" in caplog.text


class TestDataLoaderConstants:
    """Тесты для констант модуля data_loader."""

    def test_encoding_constant(self) -> None:
        """Тест константы ENCODING."""
        assert ENCODING == "utf-8"
        assert isinstance(ENCODING, str)

    def test_file_read_mode_constant(self) -> None:
        """Тест константы FILE_READ_MODE."""
        assert FILE_READ_MODE == "r"
        assert isinstance(FILE_READ_MODE, str)

    def test_file_append_mode_constant(self) -> None:
        """Тест константы FILE_APPEND_MODE."""
        assert FILE_APPEND_MODE == "a"
        assert isinstance(FILE_APPEND_MODE, str)

    def test_timestamp_format_constant(self) -> None:
        """Тест константы TIMESTAMP_FORMAT."""
        assert TIMESTAMP_FORMAT == "%Y-%m-%d %H:%M:%S"
        assert isinstance(TIMESTAMP_FORMAT, str)

    def test_default_return_value_constant(self) -> None:
        """Тест константы DEFAULT_RETURN_VALUE."""
        assert DEFAULT_RETURN_VALUE == []
        assert isinstance(DEFAULT_RETURN_VALUE, list)


class TestDataLoaderLogger:
    """Тесты для функции _setup_logger."""

    def test_logger_setup_creates_logger(self) -> None:
        """Тест, что логгер создается корректно."""
        # Импортируем модуль, чтобы логгер был создан
        from src import data_loader

        # Проверяем, что логгер существует
        assert hasattr(data_loader, "logger")
        assert isinstance(data_loader.logger, logging.Logger)

    def test_logger_has_file_handler(self) -> None:
        """Тест, что логгер имеет file handler."""
        from src import data_loader

        logger = data_loader.logger
        assert len(logger.handlers) > 0
        assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    def test_logger_level_is_debug(self) -> None:
        """Тест, что уровень логирования установлен в DEBUG."""
        from src import data_loader

        logger = data_loader.logger
        assert logger.level == logging.DEBUG

    def test_logger_handlers_check(self) -> None:
        """Тест, что _setup_logger возвращает существующий logger если handlers уже есть."""
        from src import data_loader

        # Получаем текущий logger
        logger1 = data_loader.logger

        # Вызываем _setup_logger еще раз - должен вернуть тот же logger
        logger2 = data_loader._setup_logger()

        # Проверяем, что это тот же объект
        assert logger1 is logger2

    def test_load_categories_from_json_unexpected_exception_propagates(self, tmp_path: Path) -> None:
        """Тест, что неожиданные исключения пробрасываются дальше (Errors should never pass silently)."""
        # Arrange
        json_file = tmp_path / "test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([{"name": "Test", "description": "Desc", "products": []}], f)

        # Мокаем Category.__init__ чтобы вызвать неожиданное исключение
        with patch("src.data_loader.Category.__init__", side_effect=RuntimeError("Unexpected error")):
            # Act & Assert
            # Неожиданные исключения должны пробрасываться дальше
            # согласно принципу "Errors should never pass silently"
            with pytest.raises(RuntimeError, match="Unexpected error"):
                load_categories_from_json(str(json_file))
