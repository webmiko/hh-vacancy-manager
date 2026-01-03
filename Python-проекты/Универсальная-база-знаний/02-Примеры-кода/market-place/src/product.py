"""Модуль для работы с продуктами.

Этот модуль содержит классы для представления товаров в интернет-магазине:
- Product - базовый класс для представления товара
- Smartphone - класс для представления смартфона (наследник Product)
- LawnGrass - класс для представления травы газонной (наследник Product)
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    pass

# Константы модуля
DEFAULT_PRICE = 0.0
DEFAULT_QUANTITY = 0
ENCODING = "utf-8"
FILE_APPEND_MODE = "a"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


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

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "product.log"
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

        # Дополнительные атрибуты для Smartphone
        if hasattr(self, "efficiency"):
            attrs.append(f"efficiency={getattr(self, 'efficiency')}")
            attrs.append(f"model='{getattr(self, 'model')}'")
            attrs.append(f"memory={getattr(self, 'memory')}")
            attrs.append(f"color='{getattr(self, 'color')}'")

        # Дополнительные атрибуты для LawnGrass
        if hasattr(self, "country"):
            attrs.append(f"country='{getattr(self, 'country')}'")
            attrs.append(f"germination_period='{getattr(self, 'germination_period')}'")
            attrs.append(f"color='{getattr(self, 'color')}'")

        return f"{self.__class__.__name__}({', '.join(attrs)})"


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
            quantity: Количество в наличии (в штуках). Должно быть >= 0

        Raises:
            ValueError: Если price < 0 или quantity < 0
        """
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        self.name = name
        self.description = description
        self.__price = price
        self.quantity = quantity

    @property
    def price(self) -> float:
        """Возвращает цену продукта.

        Returns:
            Цена продукта

        Raises:
            ValueError: Если цена была изменена на отрицательную через прямое обращение к приватному атрибуту
        """
        # Проверка на случай обхода валидации через прямое обращение к приватному атрибуту
        if self.__price < 0:
            logger.warning(f"Обнаружена отрицательная цена для {self.name}: {self.__price}")
            raise ValueError("Цена не может быть отрицательной")
        return self.__price

    @price.setter
    def price(self, value: float) -> None:
        """Устанавливает цену продукта с валидацией.

        Если цена <= 0, выбрасывает ValueError.
        Если цена понижается, запрашивает подтверждение у пользователя.

        Args:
            value: Новая цена продукта

        Raises:
            ValueError: Если цена <= 0
        """
        if value <= 0:
            error_msg = f"Цена не должна быть нулевая или отрицательная (получено: {value})"
            logger.warning(f"Попытка установить невалидную цену для продукта: {self.name}")
            raise ValueError(error_msg)

        # Проверка на понижение цены
        if value < self.__price:
            logger.info(f"Попытка понизить цену для продукта: {self.name}")
            try:
                response = input(f"Цена понижается с {self.__price} до {value}. Подтвердите действие (y/n): ")
                if response.lower() != "y":
                    logger.info(f"Пользователь отменил понижение цены для {self.name}")
                    return
            except EOFError:
                # В неинтерактивном режиме (например, при тестировании) не подтверждаем понижение
                logger.debug(f"EOFError при попытке понизить цену для {self.name} (неинтерактивный режим)")
                return

        logger.info(f"Изменение цены для продукта: {self.name}")
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


class Product(LogCreationMixin, BaseProduct):
    """Класс для представления продукта в интернет-магазине.

    Класс Product наследуется от BaseProduct и реализует все абстрактные методы.
    Содержит информацию о товаре: название, описание, цену и количество в наличии.

    Attributes:
        name: Название продукта (наследуется от BaseProduct)
        description: Описание продукта (наследуется от BaseProduct)
        price: Цена продукта (может быть с копейками). Property с геттером и сеттером (наследуется от BaseProduct)
        quantity: Количество в наличии (в штуках) (наследуется от BaseProduct)

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
            quantity: Количество в наличии (в штуках). Должно быть >= 0

        Raises:
            ValueError: Если price < 0 или quantity < 0

        Example:
            >>> product = Product("Test", "Description", 100.0, 10)
            >>> assert product.name == "Test"
            >>> assert product.quantity == 10

            >>> Product("Test", "Desc", -100.0, 5)  # doctest: +SKIP
            Traceback (most recent call last):
            ...
            ValueError: Цена не может быть отрицательной

            >>> Product("Test", "Desc", 100.0, -5)  # doctest: +SKIP
            Traceback (most recent call last):
            ...
            ValueError: Количество не может быть отрицательным
        """
        super().__init__(name, description, price, quantity)
        # Логируем создание объекта после установки всех атрибутов
        print(f"Создан объект {self.__class__.__name__}: {self!r}")

    @classmethod
    def new_product(
        cls, product_data: dict[str, object], existing_products: Optional[List["Product"]] = None
    ) -> "Product":
        """Создает новый продукт из словаря с данными.

        Если передан список существующих продуктов, проверяет наличие дубликатов по имени.
        При обнаружении дубликата:
        - Складывает количества товаров
        - Выбирает максимальную цену
        - Обновляет описание

        Args:
            product_data: Словарь с данными продукта:
                - name: Название продукта
                - description: Описание продукта
                - price: Цена продукта
                - quantity: Количество в наличии
            existing_products: Опциональный список существующих продуктов для проверки дубликатов

        Returns:
            Созданный объект класса Product

        Raises:
            KeyError: Если отсутствуют обязательные ключи в product_data
            TypeError: Если типы данных не соответствуют ожидаемым
            ValueError: Если значения невалидны (отрицательные числа)

        Example:
            >>> data = {"name": "Test", "description": "Desc", "price": 100.0, "quantity": 5}
            >>> product = Product.new_product(data)
            >>> assert product.name == "Test"
            >>> assert product.price == 100.0
        """
        # Проверка наличия обязательных ключей
        required_keys = ["name", "description", "price", "quantity"]
        missing_keys = [key for key in required_keys if key not in product_data]
        if missing_keys:
            raise KeyError(f"Отсутствуют обязательные ключи в product_data: {missing_keys}")

        # Валидация и преобразование типов
        name = product_data["name"]
        description = product_data["description"]
        price = product_data["price"]
        quantity = product_data["quantity"]

        # Проверка типов
        if not isinstance(name, str):
            raise TypeError(f"name должен быть строкой, получен {type(name).__name__}")
        if not isinstance(description, str):
            raise TypeError(f"description должен быть строкой, получен {type(description).__name__}")

        # Преобразование и проверка price
        try:
            price = float(price)  # type: ignore[arg-type]
        except (ValueError, TypeError) as e:
            raise TypeError(f"price должен быть числом, получен {type(product_data['price']).__name__}") from e

        # Преобразование и проверка quantity
        try:
            quantity = int(quantity)  # type: ignore[call-overload]
        except (ValueError, TypeError) as e:
            raise TypeError(
                f"quantity должен быть целым числом, получен {type(product_data['quantity']).__name__}"
            ) from e

        # Валидация значений
        if price < 0:
            raise ValueError(f"price не может быть отрицательным, получено: {price}")
        if quantity < 0:
            raise ValueError(f"quantity не может быть отрицательным, получено: {quantity}")

        if existing_products:
            for existing in existing_products:
                if existing.name == name:
                    # Найден дубликат - складываем количества и выбираем максимальную цену
                    new_quantity = existing.quantity + quantity
                    new_price = max(existing.price, price)
                    existing.quantity = new_quantity
                    existing.price = new_price  # Используем property setter для валидации
                    existing.description = description
                    return existing

        # Создаем новый продукт
        return cls(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
        )

    def __str__(self) -> str:
        """Возвращает строковое представление продукта.

        Returns:
            Строка в формате: "Название продукта, X руб. Остаток: X шт."

        Example:
            >>> product = Product("Test", "Description", 100.0, 5)
            >>> str(product)
            'Test, 100 руб. Остаток: 5 шт.'
        """
        return f"{self.name}, {int(self.price)} руб. Остаток: {self.quantity} шт."

    def __add__(self, other: "BaseProduct") -> float:
        """Возвращает сумму произведений цены на количество для двух продуктов.

        Метод позволяет складывать только товары из одинаковых классов продуктов.
        Например, можно сложить Product + Product, Smartphone + Smartphone,
        LawnGrass + LawnGrass, но нельзя сложить Smartphone + LawnGrass.

        Args:
            other: Второй объект того же класса, что и self

        Returns:
            Сумма произведений цены на количество: self.price * self.quantity + other.price * other.quantity

        Raises:
            TypeError: Если other не является объектом того же класса, что и self

        Example:
            >>> product1 = Product("Test1", "Desc1", 100.0, 10)
            >>> product2 = Product("Test2", "Desc2", 200.0, 2)
            >>> product1 + product2
            1400.0

            >>> smartphone1 = Smartphone("Phone1", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
            >>> smartphone2 = Smartphone("Phone2", "Desc", 200.0, 2, 98.0, "Model2", 512, "White")
            >>> smartphone1 + smartphone2
            900.0

            >>> grass = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
            >>> smartphone1 + grass  # doctest: +SKIP
            Traceback (most recent call last):
            ...
            TypeError: Можно складывать только товары из одинаковых классов продуктов
        """
        if type(self) is not type(other):
            raise TypeError("Можно складывать только товары из одинаковых классов продуктов")
        return self.price * self.quantity + other.price * other.quantity

    def __eq__(self, other: object) -> bool:
        """Проверяет равенство двух продуктов по всем атрибутам.

        Два продукта считаются равными, если все их атрибуты совпадают:
        name, description, price, quantity.

        Args:
            other: Объект для сравнения

        Returns:
            True, если продукты равны по всем атрибутам, False в противном случае

        Example:
            >>> product1 = Product("Test", "Desc", 100.0, 5)
            >>> product2 = Product("Test", "Desc", 100.0, 5)
            >>> product3 = Product("Test", "Desc", 200.0, 5)
            >>> product1 == product2
            True
            >>> product1 == product3
            False
        """
        if not isinstance(other, Product):
            return False
        return (
            self.name == other.name
            and self.description == other.description
            and self.price == other.price
            and self.quantity == other.quantity
        )


# ============================================================================
# Начало разработки нового функционала в рамках работы над проектом homework_16_1
# ============================================================================


class Smartphone(Product):
    """Класс для представления смартфона в интернет-магазине.

    Класс Smartphone наследуется от Product и расширяет его дополнительными
    атрибутами, специфичными для смартфонов.

    Attributes:
        name: Название продукта (наследуется от Product)
        description: Описание продукта (наследуется от Product)
        price: Цена продукта (наследуется от Product)
        quantity: Количество в наличии (наследуется от Product)
        efficiency: Производительность смартфона (float)
        model: Модель смартфона (str)
        memory: Объем встроенной памяти в ГБ (int)
        color: Цвет смартфона (str)

    Example:
        >>> smartphone = Smartphone(
        ...     name="Samsung Galaxy S23 Ultra",
        ...     description="256GB, Серый цвет, 200MP камера",
        ...     price=180000.0,
        ...     quantity=5,
        ...     efficiency=95.5,
        ...     model="S23 Ultra",
        ...     memory=256,
        ...     color="Серый"
        ... )
        >>> print(smartphone.name)
        Samsung Galaxy S23 Ultra
        >>> print(smartphone.efficiency)
        95.5
        >>> print(smartphone.memory)
        256
    """

    efficiency: float
    model: str
    memory: int
    color: str

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
        efficiency: float,
        model: str,
        memory: int,
        color: str,
    ) -> None:
        """Инициализирует экземпляр класса Smartphone.

        Args:
            name: Название продукта
            description: Описание продукта
            price: Цена продукта (может быть с копейками)
            quantity: Количество в наличии (в штуках)
            efficiency: Производительность смартфона
            model: Модель смартфона
            memory: Объем встроенной памяти в ГБ
            color: Цвет смартфона

        Example:
            >>> smartphone = Smartphone(
            ...     "Iphone 15", "512GB, Gray space", 210000.0, 8,
            ...     98.2, "15", 512, "Gray space"
            ... )
            >>> assert smartphone.name == "Iphone 15"
            >>> assert smartphone.efficiency == 98.2
            >>> assert smartphone.memory == 512
        """
        super().__init__(name, description, price, quantity)
        self.efficiency = efficiency
        self.model = model
        self.memory = memory
        self.color = color
        # Вызываем print после установки всех атрибутов
        print(f"Создан объект {self.__class__.__name__}: {self!r}")

    def __eq__(self, other: object) -> bool:
        """Проверяет равенство двух смартфонов по всем атрибутам.

        Два смартфона считаются равными, если все их атрибуты совпадают:
        name, description, price, quantity, efficiency, model, memory, color.

        Args:
            other: Объект для сравнения

        Returns:
            True, если смартфоны равны по всем атрибутам, False в противном случае

        Example:
            >>> smartphone1 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
            >>> smartphone2 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
            >>> smartphone1 == smartphone2
            True
        """
        if not isinstance(other, Smartphone):
            return False
        return (
            super().__eq__(other)
            and self.efficiency == other.efficiency
            and self.model == other.model
            and self.memory == other.memory
            and self.color == other.color
        )


class LawnGrass(Product):
    """Класс для представления травы газонной в интернет-магазине.

    Класс LawnGrass наследуется от Product и расширяет его дополнительными
    атрибутами, специфичными для газонной травы.

    Attributes:
        name: Название продукта (наследуется от Product)
        description: Описание продукта (наследуется от Product)
        price: Цена продукта (наследуется от Product)
        quantity: Количество в наличии (наследуется от Product)
        country: Страна-производитель (str)
        germination_period: Срок прорастания (str)
        color: Цвет травы (str)

    Example:
        >>> grass = LawnGrass(
        ...     name="Газонная трава",
        ...     description="Элитная трава для газона",
        ...     price=500.0,
        ...     quantity=20,
        ...     country="Россия",
        ...     germination_period="7 дней",
        ...     color="Зеленый"
        ... )
        >>> print(grass.name)
        Газонная трава
        >>> print(grass.country)
        Россия
        >>> print(grass.germination_period)
        7 дней
    """

    country: str
    germination_period: str
    color: str

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
        country: str,
        germination_period: str,
        color: str,
    ) -> None:
        """Инициализирует экземпляр класса LawnGrass.

        Args:
            name: Название продукта
            description: Описание продукта
            price: Цена продукта (может быть с копейками)
            quantity: Количество в наличии (в штуках)
            country: Страна-производитель
            germination_period: Срок прорастания
            color: Цвет травы

        Example:
            >>> grass = LawnGrass(
            ...     "Газонная трава 2", "Выносливая трава", 450.0, 15,
            ...     "США", "5 дней", "Темно-зеленый"
            ... )
            >>> assert grass.name == "Газонная трава 2"
            >>> assert grass.country == "США"
            >>> assert grass.germination_period == "5 дней"
        """
        super().__init__(name, description, price, quantity)
        self.country = country
        self.germination_period = germination_period
        self.color = color
        # Вызываем print после установки всех атрибутов
        print(f"Создан объект {self.__class__.__name__}: {self!r}")

    def __eq__(self, other: object) -> bool:
        """Проверяет равенство двух объектов LawnGrass по всем атрибутам.

        Два объекта считаются равными, если все их атрибуты совпадают:
        name, description, price, quantity, country, germination_period, color.

        Args:
            other: Объект для сравнения

        Returns:
            True, если объекты равны по всем атрибутам, False в противном случае

        Example:
            >>> grass1 = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
            >>> grass2 = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
            >>> grass1 == grass2
            True
        """
        if not isinstance(other, LawnGrass):
            return False
        return (
            super().__eq__(other)
            and self.country == other.country
            and self.germination_period == other.germination_period
            and self.color == other.color
        )
