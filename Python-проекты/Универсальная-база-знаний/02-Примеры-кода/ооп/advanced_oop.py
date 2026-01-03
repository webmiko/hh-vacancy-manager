"""Продвинутые примеры ООП: абстрактные классы, миксины, пользовательские исключения.

> **Дата добавления/обновления:** 2026-01-02
> **Категория:** Объектно-ориентированное программирование (ООП)
> **Связанные модули:**
>   - `ооп/oop_classes.py` - базовые примеры классов
>   - `тестирование/pytest_fixtures.py` - примеры тестирования классов
>   - `работа-с-файлами/json_loader.py` - загрузка данных для создания объектов
> **Учебные материалы:**
>   - [01-Учебные-материалы/10-ООП/Абстрактные-классы.md](../../01-Учебные-материалы/10-ООП/Абстрактные-классы.md)
>   - [01-Учебные-материалы/10-ООП/Множественное-наследование.md](../../01-Учебные-материалы/10-ООП/Множественное-наследование.md)
>   - [01-Учебные-материалы/12-Исключения/Пользовательские-исключения-и-raise.md](../../01-Учебные-материалы/12-Исключения/Пользовательские-исключения-и-raise.md)
>   - [01-Учебные-материалы/12-Исключения/Блоки-try-except.md](../../01-Учебные-материалы/12-Исключения/Блоки-try-except.md)

Этот модуль демонстрирует продвинутые техники ООП:
- Абстрактные классы (ABC) для определения интерфейсов
- Миксины для добавления функциональности через множественное наследование
- Пользовательские исключения для явной обработки ошибок
- Обработка исключений с использованием try/except/finally/else

Когда использовать:
- При создании иерархии классов с общим интерфейсом
- Когда нужно добавить функциональность через миксины
- При необходимости явной обработки специфических ошибок
- Когда нужно гарантировать реализацию методов в подклассах
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Константы модуля
DEFAULT_PRICE = 0.0
DEFAULT_QUANTITY = 0


# ============================================================================
# Пользовательские исключения
# ============================================================================


class ZeroQuantityError(ValueError):
    """Пользовательский класс исключения для обработки добавления товара с нулевым количеством.

    Наследуется от ValueError и используется для явного указания на ошибку
    при попытке создать товар с нулевым количеством.

    Example:
        >>> raise ZeroQuantityError("Товар с нулевым количеством не может быть добавлен")
        Traceback (most recent call last):
        ...
        ZeroQuantityError: Товар с нулевым количеством не может быть добавлен
    """

    pass


# ============================================================================
# Миксины
# ============================================================================


class LogCreationMixin:
    """Миксин для логирования создания объектов.

    При создании объекта выводит в консоль информацию о классе
    и параметрах, с которыми был создан объект.

    Примечание: Использует print() согласно требованию задания.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Инициализирует объект и логирует его создание.

        Args:
            *args: Позиционные аргументы конструктора
            **kwargs: Именованные аргументы конструктора
        """
        super().__init__(*args, **kwargs)  # type: ignore[call-arg]
        # Логирование будет вызвано в конце __init__ каждого класса
        # после установки всех атрибутов

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта для логирования.

        Returns:
            Строка с параметрами объекта для логирования
        """
        # Базовое представление
        attrs: list[str] = []
        if hasattr(self, "name"):
            attrs.append(f"name='{getattr(self, 'name')}'")
        if hasattr(self, "description"):
            attrs.append(f"description='{getattr(self, 'description')}'")
        if hasattr(self, "price"):
            attrs.append(f"price={getattr(self, 'price')}")
        if hasattr(self, "quantity"):
            attrs.append(f"quantity={getattr(self, 'quantity')}")

        return f"{self.__class__.__name__}({', '.join(attrs)})"


# ============================================================================
# Абстрактные классы
# ============================================================================


class BaseProduct(ABC):
    """Абстрактный базовый класс для всех продуктов.

    Определяет общий интерфейс и функциональность для всех продуктов
    в интернет-магазине. Не может быть создан напрямую.

    Attributes:
        name: Название продукта
        description: Описание продукта
        price: Цена продукта (может быть с копейками). Property с геттером и сеттером.
        quantity: Количество в наличии (в штуках)
    """

    name: str
    description: str
    __price: float
    quantity: int

    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        """Инициализирует экземпляр продукта.

        Args:
            name: Название продукта
            description: Описание продукта
            price: Цена продукта (может быть с копейками). Должна быть >= 0
            quantity: Количество в наличии (в штуках). Должно быть > 0

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
        self.__price = price
        self.quantity = quantity

    @property
    def price(self) -> float:
        """Возвращает цену продукта.

        Returns:
            Цена продукта
        """
        return self.__price

    @price.setter
    def price(self, value: float) -> None:
        """Устанавливает цену продукта с валидацией.

        Args:
            value: Новая цена продукта

        Raises:
            ValueError: Если цена <= 0
        """
        if value <= 0:
            raise ValueError("Цена не должна быть нулевая или отрицательная")
        self.__price = value

    @abstractmethod
    def __str__(self) -> str:
        """Возвращает строковое представление продукта.

        Returns:
            Строка с представлением продукта
        """
        pass

    @abstractmethod
    def __add__(self, other: "BaseProduct") -> float:
        """Возвращает сумму произведений цены на количество для двух продуктов.

        Args:
            other: Второй объект продукта

        Returns:
            Сумма произведений цены на количество
        """
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Проверяет равенство двух продуктов по всем атрибутам.

        Args:
            other: Объект для сравнения

        Returns:
            True, если продукты равны по всем атрибутам, False в противном случае
        """
        pass


class BaseEntity(ABC):
    """Абстрактный базовый класс для сущностей с названием и описанием.

    Используется для Category и Order. Определяет общий интерфейс
    для сущностей, имеющих название и описание.

    Attributes:
        name: Название сущности
        description: Описание сущности
    """

    name: str
    description: str

    def __init__(self, name: str, description: str) -> None:
        """Инициализирует сущность с названием и описанием.

        Args:
            name: Название сущности
            description: Описание сущности
        """
        self.name = name
        self.description = description

    @abstractmethod
    def __str__(self) -> str:
        """Возвращает строковое представление сущности.

        Returns:
            Строковое представление сущности
        """
        pass


# ============================================================================
# Конкретные классы
# ============================================================================


class Product(LogCreationMixin, BaseProduct):
    """Класс для представления продукта в интернет-магазине.

    Класс Product наследуется от BaseProduct и реализует все абстрактные методы.
    Использует миксин LogCreationMixin для логирования создания объектов.

    Attributes:
        name: Название продукта (наследуется от BaseProduct)
        description: Описание продукта (наследуется от BaseProduct)
        price: Цена продукта (наследуется от BaseProduct)
        quantity: Количество в наличии (наследуется от BaseProduct)

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

    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        """Инициализирует экземпляр класса Product.

        Args:
            name: Название продукта
            description: Описание продукта
            price: Цена продукта (может быть с копейками). Должна быть >= 0
            quantity: Количество в наличии (в штуках). Должно быть > 0

        Raises:
            ValueError: Если price < 0 или quantity < 0
            ZeroQuantityError: Если quantity == 0
        """
        super().__init__(name, description, price, quantity)
        # Логируем создание объекта после установки всех атрибутов
        print(f"Создан объект {self.__class__.__name__}: {self!r}")

    def __str__(self) -> str:
        """Возвращает строковое представление продукта.

        Returns:
            Строка в формате: "Название продукта, X руб. Остаток: X шт."
        """
        return f"{self.name}, {int(self.price)} руб. Остаток: {self.quantity} шт."

    def __add__(self, other: "BaseProduct") -> float:
        """Возвращает сумму произведений цены на количество для двух продуктов.

        Args:
            other: Второй объект того же класса, что и self

        Returns:
            Сумма произведений цены на количество

        Raises:
            TypeError: Если other не является объектом того же класса, что и self
        """
        if type(self) is not type(other):
            raise TypeError("Можно складывать только товары из одинаковых классов продуктов")
        return round(self.price * self.quantity + other.price * other.quantity, 2)

    def __eq__(self, other: object) -> bool:
        """Проверяет равенство двух продуктов по всем атрибутам.

        Args:
            other: Объект для сравнения

        Returns:
            True, если продукты равны по всем атрибутам, False в противном случае
        """
        if not isinstance(other, Product):
            return False
        return (
            self.name == other.name
            and self.description == other.description
            and self.price == other.price
            and self.quantity == other.quantity
        )


class Category(BaseEntity):
    """Класс для представления категории товаров в интернет-магазине.

    Класс Category содержит информацию о категории: название, описание
    и список товаров, принадлежащих этой категории.

    Attributes:
        name: Название категории
        description: Описание категории
        products: Список товаров категории (объекты класса Product)

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
    """

    name: str
    description: str
    __products: list["Product"]

    def __init__(self, name: str, description: str, products: list["Product"]) -> None:
        """Инициализирует экземпляр класса Category.

        Args:
            name: Название категории
            description: Описание категории
            products: Список товаров категории (объекты класса Product)
        """
        super().__init__(name, description)
        self.__products = products[:] if products else []

    def add_product(self, product: "Product") -> None:
        """Добавляет продукт в категорию с обработкой исключений.

        Демонстрирует использование try/except/finally/else для обработки исключений.

        Args:
            product: Объект класса Product для добавления в категорию

        Raises:
            TypeError: Если product не является экземпляром класса Product
            ValueError: Если продукт с такими же атрибутами уже существует
            ZeroQuantityError: Если продукт имеет нулевое количество
        """
        product_name = getattr(product, "name", "неизвестный товар")
        try:
            if not isinstance(product, Product):
                raise TypeError("Можно добавлять только объекты класса Product и его наследников")
            # Проверка на дубликаты
            if product in self.__products:
                raise ValueError("Продукт с такими же атрибутами уже существует в категории")
            # Проверка на нулевое количество товара
            if product.quantity == 0:
                raise ZeroQuantityError("Товар с нулевым количеством не может быть добавлен")
        except ZeroQuantityError as e:
            print(f"Ошибка при добавлении товара: {e}")
            raise
        else:
            # Блок выполняется только если исключений не было
            self.__products.append(product)
            print(f"Товар '{product.name}' успешно добавлен в категорию '{self.name}'")
        finally:
            # Блок выполняется всегда, независимо от наличия исключений
            print(f"Обработка добавления товара '{product_name}' завершена")

    def middle_price(self) -> float:
        """Подсчитывает средний ценник товаров в категории.

        Метод вычисляет среднее арифметическое цен всех товаров в категории.
        Если в категории нет товаров (деление на ноль), возвращает 0.

        Returns:
            Средний ценник товаров в категории. Если товаров нет, возвращает 0.

        Example:
            >>> product1 = Product("Test1", "Desc1", 100.0, 5)
            >>> product2 = Product("Test2", "Desc2", 200.0, 10)
            >>> category = Category("Test", "Description", [product1, product2])
            >>> category.middle_price()
            150.0

            >>> category_empty = Category("Empty", "Description", [])
            >>> category_empty.middle_price()
            0
        """
        try:
            if not self.__products:
                return 0.0
            total_price = sum(product.price for product in self.__products)
            return round(total_price / len(self.__products), 2)
        except ZeroDivisionError:
            return 0.0

    def __str__(self) -> str:
        """Возвращает строковое представление категории.

        Returns:
            Строка в формате: "Название категории, количество продуктов: X шт."
        """
        total_quantity = sum(product.quantity for product in self.__products)
        return f"{self.name}, количество продуктов: {total_quantity} шт."


# ============================================================================
# Пример использования
# ============================================================================

if __name__ == "__main__":
    # Пример создания продукта
    try:
        product_invalid = Product("Бракованный товар", "Неверное количество", 1000.0, 0)
    except ZeroQuantityError as e:
        print(f"Возникла ошибка ZeroQuantityError: {e}")

    # Создание валидных продуктов
    product1 = Product("Samsung Galaxy S23 Ultra", "256GB, Серый цвет, 200MP камера", 180000.0, 5)
    product2 = Product("Iphone 15", "512GB, Gray space", 210000.0, 8)

    # Создание категории
    category = Category("Смартфоны", "Категория смартфонов", [product1, product2])

    # Использование метода подсчета среднего ценника
    print(f"Средний ценник товаров в категории: {category.middle_price()}")

    # Пример обработки исключений при добавлении товара
    product3 = Product("Xiaomi Redmi Note 11", "1024GB, Синий", 31000.0, 14)
    category.add_product(product3)

    # Пример с пустой категорией
    category_empty = Category("Пустая категория", "Категория без продуктов", [])
    print(f"Средний ценник пустой категории: {category_empty.middle_price()}")

