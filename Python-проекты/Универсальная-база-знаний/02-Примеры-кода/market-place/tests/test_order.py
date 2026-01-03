"""Тесты для модуля заказов."""

import pytest

from src.category import BaseEntity
from src.order import MIN_QUANTITY, Order
from src.product import BaseProduct, LawnGrass, Product, Smartphone


class TestOrderInit:
    """Тесты для инициализации класса Order."""

    def test_order_init_with_product(self) -> None:
        """Тест создания заказа с продуктом."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 5)

        assert order.name == "ORD-001"
        assert order.description == "Тестовый заказ"
        assert order.product == product
        assert order.quantity == 5
        assert order.total_price == 500.0  # 100.0 * 5

    def test_order_init_with_smartphone(self) -> None:
        """Тест создания заказа со смартфоном."""
        smartphone = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
        order = Order("ORD-002", "Заказ смартфона", smartphone, 2)

        assert order.name == "ORD-002"
        assert order.description == "Заказ смартфона"
        assert order.product == smartphone
        assert order.quantity == 2
        assert order.total_price == 200.0

    def test_order_init_with_lawn_grass(self) -> None:
        """Тест создания заказа с газонной травой."""
        grass = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
        order = Order("ORD-003", "Заказ травы", grass, 3)

        assert order.name == "ORD-003"
        assert order.description == "Заказ травы"
        assert order.product == grass
        assert order.quantity == 3
        assert order.total_price == 150.0  # 50.0 * 3

    def test_order_init_with_min_quantity(self) -> None:
        """Тест создания заказа с минимальным количеством."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("ORD-001", "Тестовый заказ", product, MIN_QUANTITY)

        assert order.quantity == MIN_QUANTITY
        assert order.total_price == 100.0  # 100.0 * 1

    def test_order_init_with_zero_quantity(self) -> None:
        """Тест создания заказа с нулевым количеством (не допускается)."""
        product = Product("Test", "Desc", 100.0, 10)
        with pytest.raises(ValueError, match=f"Количество товара должно быть не менее {MIN_QUANTITY}"):
            Order("ORD-001", "Тестовый заказ", product, 0)

    def test_order_init_with_negative_quantity(self) -> None:
        """Тест создания заказа с отрицательным количеством (не допускается)."""
        product = Product("Test", "Desc", 100.0, 10)
        with pytest.raises(ValueError, match=f"Количество товара должно быть не менее {MIN_QUANTITY}"):
            Order("ORD-001", "Тестовый заказ", product, -5)

    def test_order_init_with_invalid_product_type(self) -> None:
        """Тест создания заказа с невалидным типом продукта."""
        with pytest.raises(TypeError, match="Товар должен быть объектом класса Product или его наследников"):
            Order("ORD-001", "Тестовый заказ", "not a product", 5)  # type: ignore[arg-type]

    def test_order_init_calculates_total_price(self) -> None:
        """Тест, что итоговая стоимость рассчитывается корректно."""
        product = Product("Test", "Desc", 99.99, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 3)

        # Используем приблизительное сравнение из-за особенностей float
        assert abs(order.total_price - 299.97) < 0.01  # 99.99 * 3


class TestOrderStr:
    """Тесты для метода __str__ класса Order."""

    def test_order_str_representation(self) -> None:
        """Тест строкового представления заказа."""
        product = Product("Test Product", "Description", 100.0, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 5)
        result = str(order)

        assert "Заказ ORD-001" in result
        assert "Test Product" in result
        assert "количество: 5" in result
        assert "итого: 500.0 руб." in result

    def test_order_str_with_smartphone(self) -> None:
        """Тест строкового представления заказа со смартфоном."""
        smartphone = Smartphone("Phone", "Desc", 200.0, 5, 95.5, "Model", 256, "Black")
        order = Order("ORD-002", "Заказ смартфона", smartphone, 2)
        result = str(order)

        assert "Заказ ORD-002" in result
        assert "Phone" in result
        assert "количество: 2" in result
        assert "итого: 400.0 руб." in result

    def test_order_str_with_lawn_grass(self) -> None:
        """Тест строкового представления заказа с газонной травой."""
        grass = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
        order = Order("ORD-003", "Заказ травы", grass, 1)
        result = str(order)

        assert "Заказ ORD-003" in result
        assert "Grass" in result
        assert "количество: 1" in result
        assert "итого: 50.0 руб." in result


class TestOrderInheritance:
    """Тесты для проверки наследования Order от BaseEntity."""

    def test_order_inherits_from_base_entity(self) -> None:
        """Тест, что Order наследуется от BaseEntity."""
        assert issubclass(Order, BaseEntity)

    def test_order_implements_base_entity_methods(self) -> None:
        """Тест, что Order реализует все методы BaseEntity."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 5)

        # Проверяем, что методы BaseEntity работают
        assert hasattr(order, "name")
        assert hasattr(order, "description")
        assert hasattr(order, "__str__")
        assert order.name == "ORD-001"
        assert order.description == "Тестовый заказ"
        assert isinstance(str(order), str)

    def test_base_entity_is_abstract(self) -> None:
        """Тест, что BaseEntity нельзя создать напрямую."""
        from abc import ABC

        assert issubclass(BaseEntity, ABC)

        # Попытка создать экземпляр должна вызвать TypeError
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseEntity("Test", "Description")  # type: ignore[abstract]


class TestOrderAttributes:
    """Тесты для атрибутов класса Order."""

    def test_order_has_all_required_attributes(self) -> None:
        """Тест, что Order имеет все необходимые атрибуты."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 5)

        assert hasattr(order, "name")
        assert hasattr(order, "description")
        assert hasattr(order, "product")
        assert hasattr(order, "quantity")
        assert hasattr(order, "total_price")

    def test_order_product_is_base_product(self) -> None:
        """Тест, что product является экземпляром BaseProduct."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 5)

        assert isinstance(order.product, BaseProduct)
        assert isinstance(order.product, Product)

    def test_order_total_price_is_float(self) -> None:
        """Тест, что total_price является float."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 5)

        assert isinstance(order.total_price, float)
        assert order.total_price == 500.0

    def test_order_quantity_is_int(self) -> None:
        """Тест, что quantity является int."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 5)

        assert isinstance(order.quantity, int)
        assert order.quantity == 5


class TestOrderEdgeCases:
    """Тесты для граничных случаев класса Order."""

    def test_order_with_float_price_product(self) -> None:
        """Тест заказа с продуктом с ценой с копейками."""
        product = Product("Test", "Desc", 99.99, 10)
        order = Order("ORD-001", "Тестовый заказ", product, 2)

        assert order.total_price == 199.98

    def test_order_with_large_quantity(self) -> None:
        """Тест заказа с большим количеством товара."""
        product = Product("Test", "Desc", 100.0, 1000)
        order = Order("ORD-001", "Тестовый заказ", product, 100)

        assert order.quantity == 100
        assert order.total_price == 10000.0

    def test_order_with_empty_string_name(self) -> None:
        """Тест заказа с пустым именем."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("", "Тестовый заказ", product, 5)

        assert order.name == ""
        assert "Заказ " in str(order)

    def test_order_with_empty_string_description(self) -> None:
        """Тест заказа с пустым описанием."""
        product = Product("Test", "Desc", 100.0, 10)
        order = Order("ORD-001", "", product, 5)

        assert order.description == ""
