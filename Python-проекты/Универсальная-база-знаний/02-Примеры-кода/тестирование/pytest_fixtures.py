"""Примеры фикстур для pytest и тестирования исключений.

> **Дата добавления/обновления:** 2026-01-02
> **Категория:** Тестирование
> **Связанные модули:**
>   - `ооп/oop_classes.py` - классы для тестирования
>   - `ооп/advanced_oop.py` - продвинутые примеры ООП с исключениями
>   - `market-place/` - полный пример проекта с тестами
> **Учебные материалы:**
>   - [01-Учебные-материалы/08-Тестирование/Pytest.md](../../01-Учебные-материалы/08-Тестирование/Pytest.md)
>   - [01-Учебные-материалы/08-Тестирование/Тестирование-исключений.md](../../01-Учебные-материалы/08-Тестирование/Тестирование-исключений.md)
>   - [01-Учебные-материалы/10-ООП/Классы-и-объекты.md](../../01-Учебные-материалы/10-ООП/Классы-и-объекты.md)
>   - [01-Учебные-материалы/12-Исключения/Пользовательские-исключения-и-raise.md](../../01-Учебные-материалы/12-Исключения/Пользовательские-исключения-и-raise.md)

Этот модуль демонстрирует:
- Создание фикстур для тестирования классов
- Тестирование исключений с использованием pytest.raises()
- Тестирование пользовательских исключений
- Тестирование методов с обработкой исключений

Когда использовать:
- При создании тестов для классов
- Когда нужно подготовить тестовые данные
- Когда одни и те же данные используются в нескольких тестах
- При тестировании обработки исключений

Особенности:
- Фикстуры для создания объектов классов
- Фикстуры для списков объектов
- Переиспользование фикстур через параметры
- Тестирование исключений с проверкой сообщений
"""

import pytest


# Пример класса для тестирования
class Product:
    """Простой класс Product для демонстрации."""

    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity


class Category:
    """Простой класс Category для демонстрации."""

    def __init__(self, name: str, description: str, products: list[Product]) -> None:
        self.name = name
        self.description = description
        self.products = products


# Фикстуры для тестирования
@pytest.fixture
def sample_product() -> Product:
    """Создает тестовый продукт для использования в тестах.

    Returns:
        Экземпляр класса Product с тестовыми данными

    Example:
        >>> def test_product_name(sample_product):
        ...     assert sample_product.name == "Test Product"
    """
    return Product(
        name="Test Product",
        description="Test description",
        price=1000.0,
        quantity=10,
    )


@pytest.fixture
def sample_products() -> list[Product]:
    """Создает список тестовых продуктов.

    Returns:
        Список экземпляров класса Product

    Example:
        >>> def test_products_count(sample_products):
        ...     assert len(sample_products) == 3
    """
    return [
        Product("Product 1", "Description 1", 100.0, 5),
        Product("Product 2", "Description 2", 200.0, 10),
        Product("Product 3", "Description 3", 300.0, 15),
    ]


@pytest.fixture
def sample_category(sample_products: list[Product]) -> Category:
    """Создает тестовую категорию с продуктами.

    Args:
        sample_products: Фикстура со списком продуктов

    Returns:
        Экземпляр класса Category с тестовыми данными

    Example:
        >>> def test_category_products(sample_category):
        ...     assert len(sample_category.products) == 3
        ...     assert sample_category.name == "Test Category"
    """
    return Category(
        name="Test Category",
        description="Test category description",
        products=sample_products,
    )


# Примеры тестов с использованием фикстур
class TestProductWithFixtures:
    """Примеры тестов с использованием фикстур."""

    def test_product_init_with_fixture(self, sample_product: Product) -> None:
        """Тест создания продукта с использованием фикстуры."""
        assert sample_product.name == "Test Product"
        assert sample_product.description == "Test description"
        assert sample_product.price == 1000.0
        assert sample_product.quantity == 10

    def test_product_type_with_fixture(self, sample_product: Product) -> None:
        """Тест типов атрибутов продукта."""
        assert isinstance(sample_product.name, str)
        assert isinstance(sample_product.price, float)
        assert isinstance(sample_product.quantity, int)


class TestCategoryWithFixtures:
    """Примеры тестов категории с использованием фикстур."""

    def test_category_with_products(
        self, sample_category: Category, sample_products: list[Product]
    ) -> None:
        """Тест категории с продуктами из фикстур."""
        assert sample_category.name == "Test Category"
        assert len(sample_category.products) == len(sample_products)
        assert sample_category.products[0] == sample_products[0]

    def test_category_products_are_objects(self, sample_category: Category) -> None:
        """Тест, что products содержит объекты класса Product."""
        assert all(isinstance(p, Product) for p in sample_category.products)


# Пример использования параметризации с фикстурами
@pytest.mark.parametrize(
    "name,price,quantity",
    [
        ("Product A", 100.0, 5),
        ("Product B", 200.0, 10),
        ("Product C", 300.0, 15),
    ],
)
def test_product_creation_with_params(name: str, price: float, quantity: int) -> None:
    """Параметризованный тест создания продуктов."""
    product = Product(name, "Description", price, quantity)
    assert product.name == name
    assert product.price == price
    assert product.quantity == quantity


# ============================================================================
# Тестирование исключений
# ============================================================================


class ZeroQuantityError(ValueError):
    """Пользовательское исключение для демонстрации тестирования."""

    pass


class ProductWithValidation:
    """Класс Product с валидацией для демонстрации тестирования исключений."""

    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        """Инициализирует продукт с валидацией.

        Raises:
            ValueError: Если price < 0 или quantity < 0
            ZeroQuantityError: Если quantity == 0
        """
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        if quantity == 0:
            raise ZeroQuantityError("Товар с нулевым количеством не может быть добавлен")
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity


class TestExceptions:
    """Примеры тестирования исключений."""

    def test_product_init_with_zero_quantity(self) -> None:
        """Тест создания продукта с нулевым количеством (не допускается).

        Демонстрирует использование pytest.raises() для проверки исключений.
        """
        with pytest.raises(ZeroQuantityError, match="Товар с нулевым количеством не может быть добавлен"):
            ProductWithValidation(
                name="Out of stock",
                description="No items available",
                price=100.0,
                quantity=0,
            )

    def test_product_init_with_negative_price(self) -> None:
        """Тест создания продукта с отрицательной ценой (не допускается).

        Демонстрирует тестирование стандартных исключений ValueError.
        """
        with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
            ProductWithValidation("Product", "Description", -10.0, 5)

    def test_product_init_with_negative_quantity(self) -> None:
        """Тест создания продукта с отрицательным количеством (не допускается)."""
        with pytest.raises(ValueError, match="Количество не может быть отрицательным"):
            ProductWithValidation("Product", "Description", 100.0, -5)

    def test_product_init_with_valid_data(self) -> None:
        """Тест создания продукта с валидными данными (исключений быть не должно)."""
        product = ProductWithValidation("Product", "Description", 100.0, 5)
        assert product.name == "Product"
        assert product.price == 100.0
        assert product.quantity == 5

    def test_exception_type_check(self) -> None:
        """Тест проверки типа исключения.

        Демонстрирует проверку, что выбрасывается именно нужный тип исключения.
        """
        with pytest.raises(ZeroQuantityError) as exc_info:
            ProductWithValidation("Product", "Description", 100.0, 0)

        # Проверка типа исключения
        assert isinstance(exc_info.value, ZeroQuantityError)
        assert isinstance(exc_info.value, ValueError)  # ZeroQuantityError наследуется от ValueError
        assert "нулевым количеством" in str(exc_info.value)


class TestExceptionMessages:
    """Примеры тестирования сообщений исключений."""

    def test_exception_message_contains_keyword(self) -> None:
        """Тест, что сообщение исключения содержит ключевое слово."""
        with pytest.raises(ZeroQuantityError) as exc_info:
            ProductWithValidation("Product", "Description", 100.0, 0)

        error_message = str(exc_info.value)
        assert "нулевым количеством" in error_message
        assert "не может быть добавлен" in error_message

    def test_exception_message_exact_match(self) -> None:
        """Тест точного совпадения сообщения исключения."""
        with pytest.raises(ZeroQuantityError, match=r"Товар с нулевым количеством не может быть добавлен"):
            ProductWithValidation("Product", "Description", 100.0, 0)


# ============================================================================
# Пример использования фикстур в conftest.py
# ============================================================================
"""
Для использования этих фикстур в других тестах, создайте файл conftest.py
в папке tests/ и скопируйте туда фикстуры:

# tests/conftest.py
import pytest
from src.product import Product, ZeroQuantityError
from src.category import Category

@pytest.fixture
def sample_product() -> Product:
    return Product("Test Product", "Test description", 1000.0, 10)

@pytest.fixture
def sample_products() -> list[Product]:
    return [
        Product("Product 1", "Description 1", 100.0, 5),
        Product("Product 2", "Description 2", 200.0, 10),
        Product("Product 3", "Description 3", 300.0, 15),
    ]

@pytest.fixture
def sample_category(sample_products: list[Product]) -> Category:
    return Category(
        name="Test Category",
        description="Test category description",
        products=sample_products,
    )

# Примеры тестирования исключений в conftest.py:
def test_zero_quantity_error(sample_product: Product) -> None:
    with pytest.raises(ZeroQuantityError):
        Product("Test", "Desc", 100.0, 0)
"""

