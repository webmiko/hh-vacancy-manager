"""Примеры классов для работы с продуктами и категориями.

> **Дата добавления/обновления:** 2024-12-19
> **Категория:** Объектно-ориентированное программирование (ООП)
> **Связанные модули:**
>   - `работа-с-файлами/json_loader.py` - загрузка данных для создания объектов
>   - `тестирование/pytest_fixtures.py` - примеры тестирования классов
> **Учебные материалы:**
>   - [01-Учебные-материалы/10-ООП/Классы-и-объекты.md](../../01-Учебные-материалы/10-ООП/Классы-и-объекты.md)
>   - [01-Учебные-материалы/10-ООП/Property-декоратор.md](../../01-Учебные-материалы/10-ООП/Property-декоратор.md)
>   - [01-Учебные-материалы/10-ООП/Методы-классов.md](../../01-Учебные-материалы/10-ООП/Методы-классов.md)
>   - [01-Учебные-материалы/10-ООП/Наследование.md](../../01-Учебные-материалы/10-ООП/Наследование.md)

Этот модуль демонстрирует создание классов Product и Category
с использованием принципов ООП: инкапсуляция, атрибуты класса, property.

Когда использовать:
- При создании классов для представления сущностей (товары, категории, пользователи)
- Когда нужно отслеживать количество созданных объектов
- Когда нужно защитить внутренние данные от изменений извне
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Константы модуля
DEFAULT_PRICE = 0.0
DEFAULT_QUANTITY = 0
DEFAULT_PRODUCTS_LIST: list["Product"] = []


class Product:
    """Класс для представления продукта в интернет-магазине.

    Класс Product содержит информацию о товаре: название, описание, цену
    и количество в наличии.

    Attributes:
        name: Название продукта
        description: Описание продукта
        price: Цена продукта (может быть с копейками)
        quantity: Количество в наличии (в штуках)

    Example:
        >>> product = Product(
        ...     name="Samsung Galaxy S23 Ultra",
        ...     description="256GB, Серый цвет, 200MP камера",
        ...     price=180000.0,
        ...     quantity=5
        ... )
        >>> print(product.name)
        Samsung Galaxy S23 Ultra
        >>> print(product.price)
        180000.0
    """

    name: str
    description: str
    price: float
    quantity: int

    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        """Инициализирует экземпляр класса Product.

        Args:
            name: Название продукта
            description: Описание продукта
            price: Цена продукта (может быть с копейками)
            quantity: Количество в наличии (в штуках)

        Example:
            >>> product = Product("Test", "Description", 100.0, 10)
            >>> assert product.name == "Test"
            >>> assert product.quantity == 10
        """
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity


class Category:
    """Класс для представления категории товаров в интернет-магазине.

    Класс Category содержит информацию о категории: название, описание
    и список товаров, принадлежащих этой категории.

    Attributes:
        name: Название категории
        description: Описание категории
        products: Список товаров категории (объекты класса Product).
                  Property, возвращает копию списка для защиты от изменений.

    Class Attributes:
        category_count: Количество созданных категорий
        product_count: Общее количество продуктов во всех категориях

    Example:
        >>> product1 = Product("Product 1", "Description 1", 100.0, 5)
        >>> product2 = Product("Product 2", "Description 2", 200.0, 10)
        >>> category = Category(
        ...     name="Смартфоны",
        ...     description="Смартфоны для коммуникации",
        ...     products=[product1, product2]
        ... )
        >>> print(category.name)
        Смартфоны
        >>> print(len(category.products))
        2
        >>> print(Category.category_count)
        1
    """

    # Атрибуты класса
    category_count: int = 0
    product_count: int = 0

    name: str
    description: str
    _products: list["Product"]

    def __init__(
        self, name: str, description: str, products: list["Product"]
    ) -> None:
        """Инициализирует экземпляр класса Category.

        При создании категории автоматически увеличиваются счетчики:
        - category_count - количество категорий
        - product_count - общее количество продуктов во всех категориях

        Args:
            name: Название категории
            description: Описание категории
            products: Список товаров категории (объекты класса Product)

        Example:
            >>> product = Product("Test", "Description", 100.0, 5)
            >>> category = Category("Test Category", "Description", [product])
            >>> assert category.name == "Test Category"
            >>> assert Category.category_count > 0
            >>> assert Category.product_count > 0
        """
        self.name = name
        self.description = description
        # Создаем копию списка, чтобы изменения исходного списка не влияли на категорию
        self._products = products[:] if products else []

        # Увеличиваем счетчик категорий
        Category.category_count += 1

        # Увеличиваем счетчик продуктов на длину списка продуктов
        Category.product_count += len(self._products)

    @property
    def products(self) -> list["Product"]:
        """Возвращает список продуктов категории.

        Returns:
            Список продуктов категории (копия для защиты от изменений)
        """
        return self._products[:]


# Пример использования
if __name__ == "__main__":
    # Создание продуктов
    product1 = Product(
        name="Samsung Galaxy S23 Ultra",
        description="256GB, Серый цвет, 200MP камера",
        price=180000.0,
        quantity=5,
    )

    product2 = Product(
        name="Iphone 15",
        description="512GB, Gray space",
        price=210000.0,
        quantity=8,
    )

    # Создание категории
    category = Category(
        name="Смартфоны",
        description="Смартфоны для коммуникации",
        products=[product1, product2],
    )

    # Доступ к атрибутам
    print(f"Категория: {category.name}")
    print(f"Описание: {category.description}")
    print(f"Количество продуктов: {len(category.products)}")
    print(f"Всего категорий: {Category.category_count}")
    print(f"Всего продуктов: {Category.product_count}")

    # Доступ к продуктам через property
    for product in category.products:
        print(f"  - {product.name}: {product.price} руб. (в наличии: {product.quantity})")

