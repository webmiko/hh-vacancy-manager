"""Общие фикстуры для тестов проекта Market Place."""

import pytest

from src.category import Category
from src.product import Product


@pytest.fixture
def sample_product() -> Product:
    """Создает тестовый продукт для использования в тестах.

    Returns:
        Экземпляр класса Product с тестовыми данными

    Example:
        >>> product = sample_product()
        >>> assert product.name == "Test Product"
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
        >>> products = sample_products()
        >>> assert len(products) == 3
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
        >>> category = sample_category()
        >>> assert category.name == "Test Category"
    """
    return Category(
        name="Test Category",
        description="Test category description",
        products=sample_products,
    )
