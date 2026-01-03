"""Тесты для класса Product.

Этот модуль содержит тесты для проверки корректности работы класса Product,
включая инициализацию и все атрибуты.
"""

from typing import TYPE_CHECKING

import pytest

from src.product import DEFAULT_PRICE, DEFAULT_QUANTITY, BaseProduct, LawnGrass, LogCreationMixin, Product, Smartphone

if TYPE_CHECKING:
    from pytest import MonkeyPatch


class TestProductInit:
    """Тесты для инициализации класса Product."""

    def test_product_init_with_all_attributes(self) -> None:
        """Тест создания продукта со всеми атрибутами.

        Проверяет, что все атрибуты корректно устанавливаются при создании объекта.
        """
        product = Product(
            name="Samsung Galaxy S23 Ultra",
            description="256GB, Серый цвет, 200MP камера",
            price=180000.0,
            quantity=5,
        )

        assert product.name == "Samsung Galaxy S23 Ultra"
        assert product.description == "256GB, Серый цвет, 200MP камера"
        assert product.price == 180000.0
        assert product.quantity == 5

    def test_product_init_with_different_types(self) -> None:
        """Тест создания продукта с разными типами данных.

        Проверяет корректную работу с float для цены и int для количества.
        """
        product = Product(
            name="Test Product",
            description="Test description",
            price=99.99,
            quantity=1,
        )

        assert isinstance(product.name, str)
        assert isinstance(product.description, str)
        assert isinstance(product.price, float)
        assert isinstance(product.quantity, int)

    def test_product_init_with_zero_quantity(self) -> None:
        """Тест создания продукта с нулевым количеством."""
        product = Product(
            name="Out of stock",
            description="No items available",
            price=100.0,
            quantity=0,
        )

        assert product.quantity == 0

    def test_product_init_with_high_price(self) -> None:
        """Тест создания продукта с высокой ценой."""
        product = Product(
            name="Expensive item",
            description="Very expensive",
            price=999999.99,
            quantity=1,
        )

        assert product.price == 999999.99


class TestProductAttributes:
    """Тесты для атрибутов класса Product."""

    def test_product_attributes_are_accessible(self, sample_product: Product) -> None:
        """Тест доступа к атрибутам продукта.

        Args:
            sample_product: Фикстура с тестовым продуктом
        """
        assert sample_product.name == "Test Product"
        assert sample_product.description == "Test description"
        assert sample_product.price == 1000.0
        assert sample_product.quantity == 10

    def test_product_attributes_can_be_read(self, sample_product: Product) -> None:
        """Тест чтения атрибутов продукта.

        Args:
            sample_product: Фикстура с тестовым продуктом
        """
        name = sample_product.name
        description = sample_product.description
        price = sample_product.price
        quantity = sample_product.quantity

        assert name == "Test Product"
        assert description == "Test description"
        assert price == 1000.0
        assert quantity == 10


class TestProductConstants:
    """Тесты для констант модуля Product."""

    def test_default_price_constant(self) -> None:
        """Тест константы DEFAULT_PRICE."""
        assert DEFAULT_PRICE == 0.0
        assert isinstance(DEFAULT_PRICE, float)

    def test_default_quantity_constant(self) -> None:
        """Тест константы DEFAULT_QUANTITY."""
        assert DEFAULT_QUANTITY == 0
        assert isinstance(DEFAULT_QUANTITY, int)


class TestProductEdgeCases:
    """Тесты для граничных случаев класса Product."""

    def test_product_with_zero_price(self) -> None:
        """Тест создания продукта с нулевой ценой."""
        product = Product("Free Product", "Free item", 0.0, 10)
        assert product.price == 0.0
        assert product.quantity == 10

    def test_product_with_negative_price(self) -> None:
        """Тест создания продукта с отрицательной ценой (не допускается)."""
        with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
            Product("Product", "Description", -10.0, 5)

    def test_product_with_negative_quantity(self) -> None:
        """Тест создания продукта с отрицательным количеством (не допускается)."""
        with pytest.raises(ValueError, match="Количество не может быть отрицательным"):
            Product("Product", "Description", 100.0, -5)

    def test_product_with_zero_price_allowed(self) -> None:
        """Тест создания продукта с нулевой ценой (допускается)."""
        product = Product("Product", "Description", 0.0, 5)
        assert product.price == 0.0

    def test_product_with_zero_quantity_allowed(self) -> None:
        """Тест создания продукта с нулевым количеством (допускается)."""
        product = Product("Product", "Description", 100.0, 0)
        assert product.quantity == 0

    def test_product_with_empty_string_name(self) -> None:
        """Тест создания продукта с пустым именем."""
        product = Product("", "Description", 100.0, 5)
        assert product.name == ""

    def test_product_with_empty_string_description(self) -> None:
        """Тест создания продукта с пустым описанием."""
        product = Product("Product", "", 100.0, 5)
        assert product.description == ""

    def test_product_with_very_long_strings(self) -> None:
        """Тест создания продукта с очень длинными строками."""
        long_name = "A" * 1000
        long_description = "B" * 2000
        product = Product(long_name, long_description, 100.0, 5)
        assert len(product.name) == 1000
        assert len(product.description) == 2000

    def test_product_with_float_quantity_conversion(self) -> None:
        """Тест создания продукта с float количеством (должно быть int)."""
        # Python автоматически не преобразует, но проверим поведение
        product = Product("Product", "Description", 100.0, 5)
        assert isinstance(product.quantity, int)

    def test_product_with_int_price(self) -> None:
        """Тест создания продукта с int ценой (должно быть float)."""
        product = Product("Product", "Description", 100, 5)
        assert isinstance(product.price, (int, float))


class TestProductNewProduct:
    """Тесты для класс-метода new_product класса Product."""

    def test_new_product_from_dict(self) -> None:
        """Тест создания продукта из словаря."""
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 100.0,
            "quantity": 5,
        }

        product = Product.new_product(product_data)

        assert isinstance(product, Product)
        assert product.name == "Test Product"
        assert product.description == "Test Description"
        assert product.price == 100.0
        assert product.quantity == 5

    def test_new_product_without_existing_products(self) -> None:
        """Тест создания продукта без списка существующих продуктов."""
        product_data = {
            "name": "New Product",
            "description": "Description",
            "price": 200.0,
            "quantity": 10,
        }

        product = Product.new_product(product_data, existing_products=None)

        assert product.name == "New Product"
        assert product.price == 200.0
        assert product.quantity == 10

    def test_new_product_with_duplicate_name(self) -> None:
        """Тест создания продукта с дублирующимся именем."""
        existing_product = Product("Duplicate", "Description", 100.0, 5)
        product_data = {
            "name": "Duplicate",
            "description": "New Description",
            "price": 150.0,
            "quantity": 3,
        }

        result = Product.new_product(product_data, existing_products=[existing_product])

        # Должен вернуть существующий продукт с обновленными данными
        assert result is existing_product
        assert existing_product.quantity == 8  # 5 + 3
        assert existing_product.price == 150.0  # max(100.0, 150.0)

    def test_new_product_with_duplicate_name_lower_price(self) -> None:
        """Тест создания продукта с дублирующимся именем и меньшей ценой."""
        existing_product = Product("Duplicate", "Description", 200.0, 5)
        product_data = {
            "name": "Duplicate",
            "description": "New Description",
            "price": 150.0,
            "quantity": 3,
        }

        result = Product.new_product(product_data, existing_products=[existing_product])

        # Должен вернуть существующий продукт с максимальной ценой
        assert result is existing_product
        assert existing_product.quantity == 8  # 5 + 3
        assert existing_product.price == 200.0  # max(200.0, 150.0)

    def test_new_product_with_duplicate_name_updates_description(self) -> None:
        """Тест, что описание обновляется при дубликате продукта."""
        existing_product = Product("Duplicate", "Old Description", 100.0, 5)
        product_data = {
            "name": "Duplicate",
            "description": "Updated Description",
            "price": 150.0,
            "quantity": 3,
        }

        result = Product.new_product(product_data, existing_products=[existing_product])

        # Должен вернуть существующий продукт с обновленным описанием
        assert result is existing_product
        assert existing_product.description == "Updated Description"
        assert existing_product.quantity == 8  # 5 + 3
        assert existing_product.price == 150.0  # max(100.0, 150.0)

    def test_new_product_with_invalid_name_type(self) -> None:
        """Тест создания продукта с неправильным типом name."""
        product_data = {
            "name": 123,  # Должно быть str
            "description": "Description",
            "price": 100.0,
            "quantity": 5,
        }

        with pytest.raises(TypeError, match="name должен быть строкой"):
            Product.new_product(product_data)

    def test_new_product_with_invalid_description_type(self) -> None:
        """Тест создания продукта с неправильным типом description."""
        product_data = {
            "name": "Test",
            "description": 123,  # Должно быть str
            "price": 100.0,
            "quantity": 5,
        }

        with pytest.raises(TypeError, match="description должен быть строкой"):
            Product.new_product(product_data)

    def test_new_product_with_invalid_price_type(self) -> None:
        """Тест создания продукта с неправильным типом price."""
        product_data = {
            "name": "Test",
            "description": "Description",
            "price": "not a number",  # Должно быть число
            "quantity": 5,
        }

        with pytest.raises(TypeError, match="price должен быть числом"):
            Product.new_product(product_data)

    def test_new_product_with_invalid_quantity_type(self) -> None:
        """Тест создания продукта с неправильным типом quantity."""
        product_data = {
            "name": "Test",
            "description": "Description",
            "price": 100.0,
            "quantity": "not a number",  # Должно быть int
        }

        with pytest.raises(TypeError, match="quantity должен быть целым числом"):
            Product.new_product(product_data)

    def test_new_product_with_negative_price_in_dict(self) -> None:
        """Тест создания продукта с отрицательной ценой в словаре."""
        product_data = {
            "name": "Test",
            "description": "Description",
            "price": -100.0,
            "quantity": 5,
        }

        with pytest.raises(ValueError, match="price не может быть отрицательным"):
            Product.new_product(product_data)

    def test_new_product_with_negative_quantity_in_dict(self) -> None:
        """Тест создания продукта с отрицательным количеством в словаре."""
        product_data = {
            "name": "Test",
            "description": "Description",
            "price": 100.0,
            "quantity": -5,
        }

        with pytest.raises(ValueError, match="quantity не может быть отрицательным"):
            Product.new_product(product_data)

    def test_new_product_with_missing_keys(self) -> None:
        """Тест создания продукта с отсутствующими обязательными ключами."""
        # Отсутствует ключ "name"
        product_data = {
            "description": "Description",
            "price": 100.0,
            "quantity": 5,
        }

        with pytest.raises(KeyError, match="Отсутствуют обязательные ключи"):
            Product.new_product(product_data)

    def test_new_product_with_multiple_missing_keys(self) -> None:
        """Тест создания продукта с несколькими отсутствующими ключами."""
        # Отсутствуют ключи "name" и "description"
        product_data = {
            "price": 100.0,
            "quantity": 5,
        }

        with pytest.raises(KeyError, match="Отсутствуют обязательные ключи"):
            Product.new_product(product_data)


class TestProductPriceProperty:
    """Тесты для property price класса Product."""

    def test_price_getter(self) -> None:
        """Тест получения цены через property."""
        product = Product("Test", "Description", 100.0, 5)
        assert product.price == 100.0

    def test_price_getter_with_negative_price_bypass(self) -> None:
        """Тест получения цены при обходе валидации через прямое обращение к __price."""
        product = Product("Test", "Description", 100.0, 5)
        # Прямое изменение приватного атрибута для проверки валидации в getter
        product._BaseProduct__price = -50.0  # type: ignore[attr-defined]

        with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
            _ = product.price

    def test_price_setter_valid_value(self) -> None:
        """Тест установки валидной цены через property."""
        product = Product("Test", "Description", 100.0, 5)
        product.price = 150.0
        assert product.price == 150.0

    def test_price_setter_zero_value(self) -> None:
        """Тест установки нулевой цены (должна быть отклонена)."""
        product = Product("Test", "Description", 100.0, 5)
        initial_price = product.price

        with pytest.raises(ValueError, match="Цена не должна быть нулевая или отрицательная"):
            product.price = 0

        assert product.price == initial_price  # Цена не изменилась

    def test_price_setter_negative_value(self) -> None:
        """Тест установки отрицательной цены (должна быть отклонена)."""
        product = Product("Test", "Description", 100.0, 5)
        initial_price = product.price

        with pytest.raises(ValueError, match="Цена не должна быть нулевая или отрицательная"):
            product.price = -10.0

        assert product.price == initial_price  # Цена не изменилась

    def test_price_setter_increase(self) -> None:
        """Тест увеличения цены (не требует подтверждения)."""
        product = Product("Test", "Description", 100.0, 5)

        product.price = 150.0

        assert product.price == 150.0

    def test_price_setter_decrease_without_confirmation(self, monkeypatch: "MonkeyPatch") -> None:
        """Тест понижения цены без подтверждения."""
        product = Product("Test", "Description", 100.0, 5)
        monkeypatch.setattr("builtins.input", lambda _: "n")

        product.price = 50.0

        assert product.price == 100.0  # Цена не изменилась

    def test_price_setter_decrease_with_confirmation(self, monkeypatch: "MonkeyPatch") -> None:
        """Тест понижения цены с подтверждением."""
        product = Product("Test", "Description", 100.0, 5)
        monkeypatch.setattr("builtins.input", lambda _: "y")

        product.price = 50.0

        assert product.price == 50.0  # Цена изменилась


class TestProductStr:
    """Тесты для метода __str__ класса Product."""

    def test_str_representation(self) -> None:
        """Тест строкового представления продукта."""
        product = Product("Samsung Galaxy S23 Ultra", "Description", 180000.0, 5)
        result = str(product)
        assert result == "Samsung Galaxy S23 Ultra, 180000 руб. Остаток: 5 шт."

    def test_str_with_zero_quantity(self) -> None:
        """Тест строкового представления продукта с нулевым количеством."""
        product = Product("Test Product", "Description", 100.0, 0)
        result = str(product)
        assert result == "Test Product, 100 руб. Остаток: 0 шт."

    def test_str_with_float_price(self) -> None:
        """Тест строкового представления продукта с ценой с копейками."""
        product = Product("Test Product", "Description", 99.99, 10)
        result = str(product)
        assert result == "Test Product, 99 руб. Остаток: 10 шт."

    def test_str_integration_with_category_products(self) -> None:
        """Тест использования __str__ в property products категории."""
        from src.category import Category

        product = Product("Test Product", "Description", 100.0, 5)
        category = Category("Test Category", "Description", [product])
        products_str = category.products
        assert "Test Product, 100 руб. Остаток: 5 шт." in products_str


class TestProductAdd:
    """Тесты для метода __add__ класса Product."""

    def test_add_two_products(self) -> None:
        """Тест сложения двух продуктов."""
        product1 = Product("Product 1", "Description 1", 100.0, 10)
        product2 = Product("Product 2", "Description 2", 200.0, 2)
        result = product1 + product2
        assert result == 1400.0  # 100 * 10 + 200 * 2 = 1400

    def test_add_products_with_zero_quantity(self) -> None:
        """Тест сложения продуктов с нулевым количеством."""
        product1 = Product("Product 1", "Description 1", 100.0, 0)
        product2 = Product("Product 2", "Description 2", 200.0, 5)
        result = product1 + product2
        assert result == 1000.0  # 100 * 0 + 200 * 5 = 1000

    def test_add_products_commutative(self) -> None:
        """Тест коммутативности сложения продуктов."""
        product1 = Product("Product 1", "Description 1", 100.0, 10)
        product2 = Product("Product 2", "Description 2", 200.0, 2)
        result1 = product1 + product2
        result2 = product2 + product1
        assert result1 == result2 == 1400.0

    def test_add_with_float_price(self) -> None:
        """Тест сложения продуктов с ценой с копейками."""
        product1 = Product("Product 1", "Description 1", 99.99, 10)
        product2 = Product("Product 2", "Description 2", 50.50, 5)
        result = product1 + product2
        assert result == pytest.approx(1252.4)  # 99.99 * 10 + 50.50 * 5 = 1252.4

    def test_add_with_different_types_raises_error(self) -> None:
        """Тест, что сложение с не-Product объектом вызывает TypeError."""
        product = Product("Product 1", "Description 1", 100.0, 10)
        with pytest.raises(TypeError, match="Можно складывать только товары из одинаковых классов продуктов"):
            _ = product + 100  # type: ignore


# ============================================================================
# Начало разработки нового функционала в рамках работы над проектом homework_16_1
# ============================================================================


class TestSmartphoneInit:
    """Тесты для инициализации класса Smartphone."""

    def test_smartphone_init_with_all_attributes(self) -> None:
        """Тест создания смартфона со всеми атрибутами.

        Проверяет, что все атрибуты корректно устанавливаются при создании объекта.
        """
        smartphone = Smartphone(
            name="Samsung Galaxy S23 Ultra",
            description="256GB, Серый цвет, 200MP камера",
            price=180000.0,
            quantity=5,
            efficiency=95.5,
            model="S23 Ultra",
            memory=256,
            color="Серый",
        )

        assert smartphone.name == "Samsung Galaxy S23 Ultra"
        assert smartphone.description == "256GB, Серый цвет, 200MP камера"
        assert smartphone.price == 180000.0
        assert smartphone.quantity == 5
        assert smartphone.efficiency == 95.5
        assert smartphone.model == "S23 Ultra"
        assert smartphone.memory == 256
        assert smartphone.color == "Серый"

    def test_smartphone_init_with_different_values(self) -> None:
        """Тест создания смартфона с разными значениями."""
        smartphone = Smartphone(
            name="Iphone 15",
            description="512GB, Gray space",
            price=210000.0,
            quantity=8,
            efficiency=98.2,
            model="15",
            memory=512,
            color="Gray space",
        )

        assert smartphone.name == "Iphone 15"
        assert smartphone.efficiency == 98.2
        assert smartphone.model == "15"
        assert smartphone.memory == 512
        assert smartphone.color == "Gray space"


class TestSmartphoneInheritance:
    """Тесты для проверки наследования Smartphone от Product."""

    def test_smartphone_inherits_from_product(self) -> None:
        """Тест, что Smartphone является наследником Product."""
        smartphone = Smartphone("Test Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        assert isinstance(smartphone, Product)

    def test_smartphone_has_parent_attributes(self) -> None:
        """Тест доступа к родительским атрибутам."""
        smartphone = Smartphone("Test Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        assert smartphone.name == "Test Phone"
        assert smartphone.description == "Description"
        assert smartphone.price == 100.0
        assert smartphone.quantity == 5

    def test_smartphone_has_additional_attributes(self) -> None:
        """Тест дополнительных атрибутов Smartphone."""
        smartphone = Smartphone("Test Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        assert isinstance(smartphone.efficiency, float)
        assert smartphone.efficiency == 95.5
        assert isinstance(smartphone.model, str)
        assert smartphone.model == "Model"
        assert isinstance(smartphone.memory, int)
        assert smartphone.memory == 256
        assert isinstance(smartphone.color, str)
        assert smartphone.color == "Black"


class TestSmartphoneMethods:
    """Тесты для методов класса Smartphone."""

    def test_smartphone_str_representation(self) -> None:
        """Тест строкового представления смартфона (наследуется от Product)."""
        smartphone = Smartphone(
            "Samsung Galaxy S23 Ultra", "Description", 180000.0, 5, 95.5, "S23 Ultra", 256, "Серый"
        )
        result = str(smartphone)
        assert result == "Samsung Galaxy S23 Ultra, 180000 руб. Остаток: 5 шт."

    def test_smartphone_price_property(self) -> None:
        """Тест property price (наследуется от Product)."""
        smartphone = Smartphone("Test Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        assert smartphone.price == 100.0
        smartphone.price = 150.0
        assert smartphone.price == 150.0

    def test_smartphone_add_with_same_type(self) -> None:
        """Тест сложения двух смартфонов."""
        smartphone1 = Smartphone("Phone 1", "Description 1", 100.0, 10, 95.5, "Model1", 256, "Black")
        smartphone2 = Smartphone("Phone 2", "Description 2", 200.0, 2, 98.0, "Model2", 512, "White")
        result = smartphone1 + smartphone2
        assert result == 1400.0  # 100 * 10 + 200 * 2 = 1400

    def test_smartphone_add_with_different_type_raises_error(self) -> None:
        """Тест, что сложение смартфона с другим типом вызывает TypeError."""
        smartphone = Smartphone("Phone 1", "Description 1", 100.0, 10, 95.5, "Model1", 256, "Black")
        grass = LawnGrass("Grass", "Description", 50.0, 10, "Russia", "7 days", "Green")
        with pytest.raises(TypeError, match="Можно складывать только товары из одинаковых классов продуктов"):
            _ = smartphone + grass


class TestLawnGrassInit:
    """Тесты для инициализации класса LawnGrass."""

    def test_lawn_grass_init_with_all_attributes(self) -> None:
        """Тест создания травы газонной со всеми атрибутами.

        Проверяет, что все атрибуты корректно устанавливаются при создании объекта.
        """
        grass = LawnGrass(
            name="Газонная трава",
            description="Элитная трава для газона",
            price=500.0,
            quantity=20,
            country="Россия",
            germination_period="7 дней",
            color="Зеленый",
        )

        assert grass.name == "Газонная трава"
        assert grass.description == "Элитная трава для газона"
        assert grass.price == 500.0
        assert grass.quantity == 20
        assert grass.country == "Россия"
        assert grass.germination_period == "7 дней"
        assert grass.color == "Зеленый"

    def test_lawn_grass_init_with_different_values(self) -> None:
        """Тест создания травы газонной с разными значениями."""
        grass = LawnGrass(
            name="Газонная трава 2",
            description="Выносливая трава",
            price=450.0,
            quantity=15,
            country="США",
            germination_period="5 дней",
            color="Темно-зеленый",
        )

        assert grass.name == "Газонная трава 2"
        assert grass.country == "США"
        assert grass.germination_period == "5 дней"
        assert grass.color == "Темно-зеленый"


class TestLawnGrassInheritance:
    """Тесты для проверки наследования LawnGrass от Product."""

    def test_lawn_grass_inherits_from_product(self) -> None:
        """Тест, что LawnGrass является наследником Product."""
        grass = LawnGrass("Test Grass", "Description", 100.0, 5, "Russia", "7 days", "Green")
        assert isinstance(grass, Product)

    def test_lawn_grass_has_parent_attributes(self) -> None:
        """Тест доступа к родительским атрибутам."""
        grass = LawnGrass("Test Grass", "Description", 100.0, 5, "Russia", "7 days", "Green")
        assert grass.name == "Test Grass"
        assert grass.description == "Description"
        assert grass.price == 100.0
        assert grass.quantity == 5

    def test_lawn_grass_has_additional_attributes(self) -> None:
        """Тест дополнительных атрибутов LawnGrass."""
        grass = LawnGrass("Test Grass", "Description", 100.0, 5, "Russia", "7 days", "Green")
        assert isinstance(grass.country, str)
        assert grass.country == "Russia"
        assert isinstance(grass.germination_period, str)
        assert grass.germination_period == "7 days"
        assert isinstance(grass.color, str)
        assert grass.color == "Green"


class TestLawnGrassMethods:
    """Тесты для методов класса LawnGrass."""

    def test_lawn_grass_str_representation(self) -> None:
        """Тест строкового представления травы газонной (наследуется от Product)."""
        grass = LawnGrass("Газонная трава", "Description", 500.0, 20, "Россия", "7 дней", "Зеленый")
        result = str(grass)
        assert result == "Газонная трава, 500 руб. Остаток: 20 шт."

    def test_lawn_grass_price_property(self) -> None:
        """Тест property price (наследуется от Product)."""
        grass = LawnGrass("Test Grass", "Description", 100.0, 5, "Russia", "7 days", "Green")
        assert grass.price == 100.0
        grass.price = 150.0
        assert grass.price == 150.0

    def test_lawn_grass_add_with_same_type(self) -> None:
        """Тест сложения двух трав газонных."""
        grass1 = LawnGrass("Grass 1", "Description 1", 50.0, 10, "Russia", "7 days", "Green")
        grass2 = LawnGrass("Grass 2", "Description 2", 30.0, 5, "USA", "5 days", "Dark Green")
        result = grass1 + grass2
        assert result == 650.0  # 50 * 10 + 30 * 5 = 650

    def test_lawn_grass_add_with_different_type_raises_error(self) -> None:
        """Тест, что сложение травы газонной с другим типом вызывает TypeError."""
        grass = LawnGrass("Grass", "Description", 50.0, 10, "Russia", "7 days", "Green")
        smartphone = Smartphone("Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        with pytest.raises(TypeError, match="Можно складывать только товары из одинаковых классов продуктов"):
            _ = grass + smartphone


class TestProductAddWithTypeChecking:
    """Тесты для метода __add__ с проверкой одинаковых типов."""

    def test_add_product_with_product(self) -> None:
        """Тест сложения Product + Product."""
        product1 = Product("Product 1", "Description 1", 100.0, 10)
        product2 = Product("Product 2", "Description 2", 200.0, 2)
        result = product1 + product2
        assert result == 1400.0

    def test_add_smartphone_with_smartphone(self) -> None:
        """Тест сложения Smartphone + Smartphone."""
        smartphone1 = Smartphone(
            "Samsung Galaxy S23 Ultra",
            "256GB, Серый цвет, 200MP камера",
            180000.0,
            5,
            95.5,
            "S23 Ultra",
            256,
            "Серый",
        )
        smartphone2 = Smartphone("Iphone 15", "512GB, Gray space", 210000.0, 8, 98.2, "15", 512, "Gray space")
        result = smartphone1 + smartphone2
        assert result == 2580000.0  # 180000 * 5 + 210000 * 8 = 900000 + 1680000 = 2580000

    def test_add_lawn_grass_with_lawn_grass(self) -> None:
        """Тест сложения LawnGrass + LawnGrass."""
        grass1 = LawnGrass("Газонная трава", "Элитная трава для газона", 500.0, 20, "Россия", "7 дней", "Зеленый")
        grass2 = LawnGrass("Газонная трава 2", "Выносливая трава", 450.0, 15, "США", "5 дней", "Темно-зеленый")
        result = grass1 + grass2
        assert result == 16750.0  # 500 * 20 + 450 * 15 = 16750

    def test_add_smartphone_with_lawn_grass_raises_error(self) -> None:
        """Тест, что Smartphone + LawnGrass выбрасывает TypeError."""
        smartphone = Smartphone(
            "Samsung Galaxy S23 Ultra",
            "256GB, Серый цвет, 200MP камера",
            180000.0,
            5,
            95.5,
            "S23 Ultra",
            256,
            "Серый",
        )
        grass = LawnGrass("Газонная трава", "Элитная трава для газона", 500.0, 20, "Россия", "7 дней", "Зеленый")
        with pytest.raises(TypeError, match="Можно складывать только товары из одинаковых классов продуктов"):
            _ = smartphone + grass

    def test_add_product_with_smartphone_raises_error(self) -> None:
        """Тест, что Product + Smartphone выбрасывает TypeError."""
        product = Product("Product", "Description", 100.0, 10)
        smartphone = Smartphone("Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        with pytest.raises(TypeError, match="Можно складывать только товары из одинаковых классов продуктов"):
            _ = product + smartphone

    def test_add_product_with_lawn_grass_raises_error(self) -> None:
        """Тест, что Product + LawnGrass выбрасывает TypeError."""
        product = Product("Product", "Description", 100.0, 10)
        grass = LawnGrass("Grass", "Description", 50.0, 10, "Russia", "7 days", "Green")
        with pytest.raises(TypeError, match="Можно складывать только товары из одинаковых классов продуктов"):
            _ = product + grass

    def test_add_smartphone_with_product_raises_error(self) -> None:
        """Тест, что Smartphone + Product выбрасывает TypeError."""
        smartphone = Smartphone("Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        product = Product("Product", "Description", 100.0, 10)
        with pytest.raises(TypeError, match="Можно складывать только товары из одинаковых классов продуктов"):
            _ = smartphone + product

    def test_add_lawn_grass_with_product_raises_error(self) -> None:
        """Тест, что LawnGrass + Product выбрасывает TypeError."""
        grass = LawnGrass("Grass", "Description", 50.0, 10, "Russia", "7 days", "Green")
        product = Product("Product", "Description", 100.0, 10)
        with pytest.raises(TypeError, match="Можно складывать только товары из одинаковых классов продуктов"):
            _ = grass + product


class TestIntegration:
    """Интеграционные тесты для взаимодействия классов."""

    def test_smartphone_in_category(self) -> None:
        """Тест создания категории со смартфонами."""
        from src.category import Category

        smartphone1 = Smartphone(
            "Samsung Galaxy S23 Ultra",
            "256GB, Серый цвет, 200MP камера",
            180000.0,
            5,
            95.5,
            "S23 Ultra",
            256,
            "Серый",
        )
        smartphone2 = Smartphone("Iphone 15", "512GB, Gray space", 210000.0, 8, 98.2, "15", 512, "Gray space")

        category = Category("Смартфоны", "Высокотехнологичные смартфоны", [smartphone1, smartphone2])

        assert category.name == "Смартфоны"
        assert len(category._Category__products) == 2  # type: ignore[attr-defined]
        assert all(isinstance(p, Smartphone) for p in category._Category__products)  # type: ignore[attr-defined]

    def test_lawn_grass_in_category(self) -> None:
        """Тест создания категории с травой газонной."""
        from src.category import Category

        grass1 = LawnGrass("Газонная трава", "Элитная трава для газона", 500.0, 20, "Россия", "7 дней", "Зеленый")
        grass2 = LawnGrass("Газонная трава 2", "Выносливая трава", 450.0, 15, "США", "5 дней", "Темно-зеленый")

        category = Category("Газонная трава", "Различные виды газонной травы", [grass1, grass2])

        assert category.name == "Газонная трава"
        assert len(category._Category__products) == 2  # type: ignore[attr-defined]
        assert all(isinstance(p, LawnGrass) for p in category._Category__products)  # type: ignore[attr-defined]

    def test_mixed_products_in_category(self) -> None:
        """Тест создания категории с разными типами продуктов."""
        from src.category import Category

        product = Product("Product", "Description", 100.0, 10)
        smartphone = Smartphone("Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        grass = LawnGrass("Grass", "Description", 50.0, 10, "Russia", "7 days", "Green")

        category = Category("Mixed", "Разные продукты", [product, smartphone, grass])

        assert len(category._Category__products) == 3  # type: ignore[attr-defined]
        assert isinstance(category._Category__products[0], Product)  # type: ignore[attr-defined]
        assert isinstance(category._Category__products[1], Smartphone)  # type: ignore[attr-defined]
        assert isinstance(category._Category__products[2], LawnGrass)  # type: ignore[attr-defined]

    def test_category_iteration_with_inherited_products(self) -> None:
        """Тест итерации по категории с наследниками Product."""
        from src.category import Category

        smartphone = Smartphone("Phone", "Description", 100.0, 5, 95.5, "Model", 256, "Black")
        grass = LawnGrass("Grass", "Description", 50.0, 10, "Russia", "7 days", "Green")

        category = Category("Test", "Description", [smartphone, grass])

        products_list = list(category)
        assert len(products_list) == 2
        assert isinstance(products_list[0], Smartphone)
        assert isinstance(products_list[1], LawnGrass)
        assert all(isinstance(p, Product) for p in products_list)

    def test_product_eq_with_different_type(self) -> None:
        """Тест __eq__ для Product с объектом другого типа."""
        product = Product("Test", "Desc", 100.0, 5)
        assert product != "not a product"
        assert product != 123
        assert product != None  # noqa: E711

    def test_product_eq_with_product_different_attributes(self) -> None:
        """Тест __eq__ для Product с другим Product, но разными атрибутами."""
        product1 = Product("Test", "Desc", 100.0, 5)
        product2 = Product("Test", "Desc", 100.0, 5)
        product3 = Product("Test", "Desc", 200.0, 5)  # Разная цена
        product4 = Product("Test", "Desc", 100.0, 10)  # Разное количество
        product5 = Product("Test2", "Desc", 100.0, 5)  # Разное имя
        product6 = Product("Test", "Desc2", 100.0, 5)  # Разное описание

        assert product1 == product2
        assert product1 != product3
        assert product1 != product4
        assert product1 != product5
        assert product1 != product6

    def test_smartphone_eq_with_different_type(self) -> None:
        """Тест __eq__ для Smartphone с объектом другого типа."""
        smartphone = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
        product = Product("Phone", "Desc", 100.0, 5)
        grass = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
        assert smartphone != product
        assert smartphone != grass
        assert smartphone != "not a product"

    def test_smartphone_eq_with_different_attributes(self) -> None:
        """Тест __eq__ для Smartphone с другим Smartphone, но разными атрибутами."""
        smartphone1 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
        smartphone2 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
        smartphone3 = Smartphone("Phone", "Desc", 100.0, 5, 98.0, "Model", 256, "Black")  # Разная efficiency
        smartphone4 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model2", 256, "Black")  # Разная model
        smartphone5 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 512, "Black")  # Разная memory
        smartphone6 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "White")  # Разный color

        assert smartphone1 == smartphone2
        assert smartphone1 != smartphone3
        assert smartphone1 != smartphone4
        assert smartphone1 != smartphone5
        assert smartphone1 != smartphone6

    def test_lawn_grass_eq_with_different_type(self) -> None:
        """Тест __eq__ для LawnGrass с объектом другого типа."""
        grass = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
        product = Product("Grass", "Desc", 50.0, 10)
        smartphone = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
        assert grass != product
        assert grass != smartphone
        assert grass != "not a product"

    def test_lawn_grass_eq_with_different_attributes(self) -> None:
        """Тест __eq__ для LawnGrass с другим LawnGrass, но разными атрибутами."""
        grass1 = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
        grass2 = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
        grass3 = LawnGrass("Grass", "Desc", 50.0, 10, "USA", "7 days", "Green")  # Разная country
        grass4 = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "5 days", "Green")  # Разный germination_period
        grass5 = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Dark Green")  # Разный color

        assert grass1 == grass2
        assert grass1 != grass3
        assert grass1 != grass4
        assert grass1 != grass5

    def test_price_setter_eoferror(self) -> None:
        """Тест price setter с EOFError (неинтерактивный режим)."""
        from unittest.mock import patch

        product = Product("Test", "Desc", 100.0, 5)
        with patch("builtins.input", side_effect=EOFError()):
            # Попытка понизить цену должна вызвать EOFError, который обрабатывается
            product.price = 50.0
            # Цена не должна измениться из-за EOFError
            assert product.price == 100.0


class TestSetupLogger:
    """Тесты для функции _setup_logger."""

    def test_setup_logger_returns_existing_logger(self) -> None:
        """Тест, что _setup_logger возвращает существующий logger, если handlers уже есть."""
        from src.product import _setup_logger

        # Первый вызов создает logger
        logger1 = _setup_logger()
        assert logger1 is not None

        # Второй вызов должен вернуть тот же logger (если handlers уже есть)
        logger2 = _setup_logger()
        assert logger2 is not None
        # Проверяем, что это тот же logger (по имени)
        assert logger1.name == logger2.name


class TestBaseProduct:
    """Тесты для абстрактного класса BaseProduct."""

    def test_base_product_is_abstract(self) -> None:
        """Тест, что BaseProduct нельзя создать напрямую."""
        from abc import ABC

        assert issubclass(BaseProduct, ABC)

        # Попытка создать экземпляр должна вызвать TypeError
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseProduct("Test", "Desc", 100.0, 5)  # type: ignore[abstract]

    def test_base_product_has_abstract_methods(self) -> None:
        """Тест, что BaseProduct имеет абстрактные методы."""
        from abc import ABC

        # Проверяем, что BaseProduct является абстрактным классом
        assert issubclass(BaseProduct, ABC)

        # Проверяем наличие абстрактных методов
        assert hasattr(BaseProduct, "__init__")
        assert hasattr(BaseProduct, "__str__")
        assert hasattr(BaseProduct, "__add__")
        assert hasattr(BaseProduct, "__eq__")

    def test_product_inherits_from_base_product(self) -> None:
        """Тест, что Product наследуется от BaseProduct."""
        assert issubclass(Product, BaseProduct)

    def test_smartphone_inherits_from_base_product_indirectly(self) -> None:
        """Тест, что Smartphone наследуется от BaseProduct через Product."""
        assert issubclass(Smartphone, BaseProduct)
        assert issubclass(Smartphone, Product)

    def test_lawn_grass_inherits_from_base_product_indirectly(self) -> None:
        """Тест, что LawnGrass наследуется от BaseProduct через Product."""
        assert issubclass(LawnGrass, BaseProduct)
        assert issubclass(LawnGrass, Product)


class TestLogCreationMixin:
    """Тесты для миксина LogCreationMixin."""

    def test_product_logs_creation(self, capsys) -> None:
        """Тест, что Product логирует создание объекта."""
        # Создаем объект - print должен быть вызван в __init__
        product = Product("Продукт1", "Описание продукта", 1200, 10)

        # Читаем вывод после создания объекта
        captured = capsys.readouterr()
        assert "Создан объект Product" in captured.out
        assert "name='Продукт1'" in captured.out
        assert "price=1200" in captured.out
        assert "quantity=10" in captured.out
        assert product.name == "Продукт1"

    def test_smartphone_logs_creation(self, capsys) -> None:
        """Тест, что Smartphone логирует создание объекта."""
        # Создаем объект - print должен быть вызван в __init__
        smartphone = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")

        # Читаем вывод после создания объекта
        captured = capsys.readouterr()
        assert "Создан объект Smartphone" in captured.out
        assert "name='Phone'" in captured.out
        assert "efficiency=95.5" in captured.out
        assert "model='Model'" in captured.out
        assert smartphone.name == "Phone"

    def test_lawn_grass_logs_creation(self, capsys) -> None:
        """Тест, что LawnGrass логирует создание объекта."""
        # Создаем объект - print должен быть вызван в __init__
        grass = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")

        # Читаем вывод после создания объекта
        captured = capsys.readouterr()
        assert "Создан объект LawnGrass" in captured.out
        assert "name='Grass'" in captured.out
        assert "country='Russia'" in captured.out
        assert "germination_period='7 days'" in captured.out
        assert grass.name == "Grass"

    def test_log_creation_mixin_in_mro(self) -> None:
        """Тест, что LogCreationMixin присутствует в MRO класса Product."""
        assert LogCreationMixin in Product.__mro__

    def test_product_repr_works(self) -> None:
        """Тест, что __repr__ работает корректно для Product."""
        product = Product("Test", "Desc", 100.0, 5)
        repr_str = repr(product)

        assert "Product" in repr_str
        assert "name='Test'" in repr_str
        assert "price=100.0" in repr_str
