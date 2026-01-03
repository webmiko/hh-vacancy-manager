"""Тесты для класса Category.

Этот модуль содержит тесты для проверки корректности работы класса Category,
включая инициализацию, атрибуты и атрибуты класса.
"""

import pytest

from src.category import DEFAULT_PRODUCTS_LIST, Category
from src.product import LawnGrass, Product, Smartphone


class TestCategoryInit:
    """Тесты для инициализации класса Category."""

    def test_category_init_with_all_attributes(self) -> None:
        """Тест создания категории со всеми атрибутами.

        Проверяет, что все атрибуты корректно устанавливаются при создании объекта.
        """
        product1 = Product("Product 1", "Description 1", 100.0, 5)
        product2 = Product("Product 2", "Description 2", 200.0, 10)

        category = Category(
            name="Смартфоны",
            description="Смартфоны для коммуникации",
            products=[product1, product2],
        )

        assert category.name == "Смартфоны"
        assert category.description == "Смартфоны для коммуникации"
        assert len(category._Category__products) == 2  # type: ignore[attr-defined]
        assert category._Category__products[0] == product1  # type: ignore[attr-defined]
        assert category._Category__products[1] == product2  # type: ignore[attr-defined]
        # Проверяем строковое представление
        assert "Product 1" in category.products
        assert "Product 2" in category.products

    def test_category_init_with_empty_products_list(self) -> None:
        """Тест создания категории с пустым списком продуктов."""
        category = Category(
            name="Пустая категория",
            description="Категория без продуктов",
            products=[],
        )

        assert category.name == "Пустая категория"
        assert len(category._Category__products) == 0  # type: ignore[attr-defined]
        assert category.products == ""

    def test_category_init_products_are_objects(self) -> None:
        """Тест, что products содержит объекты класса Product."""
        product = Product("Test", "Description", 100.0, 5)
        category = Category("Test Category", "Description", [product])

        assert isinstance(category._Category__products[0], Product)  # type: ignore[attr-defined]
        assert category._Category__products[0].name == "Test"  # type: ignore[attr-defined]
        assert "Test" in category.products


class TestCategoryClassAttributes:
    """Тесты для атрибутов класса Category."""

    def test_category_count_increments_on_init(self) -> None:
        """Тест увеличения счетчика категорий при создании объекта."""
        initial_count = Category.category_count

        category1 = Category("Category 1", "Description 1", [])
        assert Category.category_count == initial_count + 1
        assert category1.name == "Category 1"

        category2 = Category("Category 2", "Description 2", [])
        assert Category.category_count == initial_count + 2
        assert category2.name == "Category 2"

    def test_product_count_increments_on_init(self) -> None:
        """Тест увеличения счетчика продуктов при создании категории."""
        initial_count = Category.product_count

        product1 = Product("Product 1", "Description 1", 100.0, 5)
        product2 = Product("Product 2", "Description 2", 200.0, 10)
        product3 = Product("Product 3", "Description 3", 300.0, 15)

        category = Category("Test Category", "Description", [product1, product2, product3])
        assert Category.product_count == initial_count + 3
        assert len(category._Category__products) == 3  # type: ignore[attr-defined]
        assert "Product 1" in category.products
        assert "Product 2" in category.products
        assert "Product 3" in category.products

    def test_product_count_counts_all_products_in_category(self) -> None:
        """Тест подсчета всех продуктов в категории."""
        initial_count = Category.product_count

        products = [Product(f"Product {i}", f"Description {i}", 100.0 * i, i) for i in range(1, 6)]

        category = Category("Test Category", "Description", products)
        assert Category.product_count == initial_count + 5
        assert len(category._Category__products) == 5  # type: ignore[attr-defined]
        products_str = category.products
        for i in range(1, 6):
            assert f"Product {i}" in products_str

    def test_category_count_and_product_count_are_class_attributes(self) -> None:
        """Тест, что category_count и product_count - атрибуты класса."""
        assert hasattr(Category, "category_count")
        assert hasattr(Category, "product_count")
        assert isinstance(Category.category_count, int)
        assert isinstance(Category.product_count, int)

    def test_category_count_accessible_from_instance(self) -> None:
        """Тест доступа к category_count через экземпляр."""
        category = Category("Test", "Description", [])
        assert hasattr(category, "category_count")
        assert category.category_count == Category.category_count

    def test_product_count_accessible_from_instance(self) -> None:
        """Тест доступа к product_count через экземпляр."""
        product = Product("Test", "Description", 100.0, 5)
        category = Category("Test", "Description", [product])
        assert hasattr(category, "product_count")
        assert category.product_count == Category.product_count


class TestCategoryAttributes:
    """Тесты для атрибутов экземпляра класса Category."""

    def test_category_attributes_are_accessible(self) -> None:
        """Тест доступа к атрибутам категории."""
        product = Product("Test Product", "Test Description", 100.0, 5)
        category = Category(
            name="Test Category",
            description="Test category description",
            products=[product],
        )

        assert category.name == "Test Category"
        assert category.description == "Test category description"
        assert len(category._Category__products) == 1  # type: ignore[attr-defined]
        assert category._Category__products[0] == product  # type: ignore[attr-defined]
        assert "Test Product" in category.products

    def test_category_products_list_can_be_accessed(self) -> None:
        """Тест доступа к списку продуктов категории."""
        products = [
            Product("Product 1", "Description 1", 100.0, 5),
            Product("Product 2", "Description 2", 200.0, 10),
        ]

        category = Category("Test", "Description", products)

        assert len(category._Category__products) == 2  # type: ignore[attr-defined]
        assert category._Category__products[0].name == "Product 1"  # type: ignore[attr-defined]
        assert category._Category__products[1].name == "Product 2"  # type: ignore[attr-defined]
        products_str = category.products
        assert "Product 1" in products_str
        assert "Product 2" in products_str


class TestCategoryConstants:
    """Тесты для констант модуля Category."""

    def test_default_products_list_constant(self) -> None:
        """Тест константы DEFAULT_PRODUCTS_LIST."""
        assert DEFAULT_PRODUCTS_LIST == []
        assert isinstance(DEFAULT_PRODUCTS_LIST, list)


class TestCategoryEdgeCases:
    """Тесты для граничных случаев класса Category."""

    def test_category_with_empty_string_name(self) -> None:
        """Тест создания категории с пустым именем."""
        category = Category("", "Description", [])
        assert category.name == ""

    def test_category_with_empty_string_description(self) -> None:
        """Тест создания категории с пустым описанием."""
        category = Category("Name", "", [])
        assert category.description == ""

    def test_category_with_very_long_strings(self) -> None:
        """Тест создания категории с очень длинными строками."""
        long_name = "A" * 1000
        long_description = "B" * 2000
        category = Category(long_name, long_description, [])
        assert len(category.name) == 1000
        assert len(category.description) == 2000

    def test_category_with_large_product_list(self) -> None:
        """Тест создания категории с большим списком продуктов."""
        products = [Product(f"Product {i}", f"Description {i}", 100.0 * i, i) for i in range(100)]
        category = Category("Large Category", "Description", products)
        assert len(category._Category__products) == 100  # type: ignore[attr-defined]
        assert Category.product_count >= 100
        products_str = category.products
        assert "Product 0" in products_str
        assert "Product 99" in products_str

    def test_category_products_list_mutation(self) -> None:
        """Тест, что список продуктов защищен от изменений через property."""
        product1 = Product("Product 1", "Description 1", 100.0, 5)
        original_list = [product1]
        category = Category("Test", "Description", original_list)
        initial_count = Category.product_count
        assert len(category._Category__products) == 1  # type: ignore[attr-defined]

        # Изменение исходного списка не влияет на категорию
        product2 = Product("Product 2", "Description 2", 200.0, 10)
        original_list.append(product2)
        assert (
            len(category._Category__products) == 1  # type: ignore[attr-defined]
        ), "Список продуктов должен быть защищен от изменений исходного списка"
        assert Category.product_count == initial_count, "Счетчик не должен изменяться при изменении исходного списка"

        # Property возвращает строку, поэтому изменения строки не влияют на внутренний список
        # Проверяем, что изменения строки не влияют на категорию
        assert len(category._Category__products) == 1, "Property возвращает строку, изменения не влияют на категорию"  # type: ignore[attr-defined]
        assert Category.product_count == initial_count, "Счетчик не должен изменяться при изменении через property"

    def test_category_with_none_values_in_products(self) -> None:
        """Тест создания категории с None в списке продуктов (не допускается)."""
        with pytest.raises(TypeError, match="Нельзя добавлять None в список продуктов"):
            Category("Test", "Description", [None])  # type: ignore

    def test_category_with_invalid_products_in_init(self) -> None:
        """Тест создания категории с невалидными объектами в списке продуктов."""
        with pytest.raises(TypeError, match="Можно добавлять только объекты класса Product и его наследников"):
            Category("Test", "Description", ["not a product", 123])  # type: ignore


class TestCategoryAddProduct:
    """Тесты для метода add_product класса Category."""

    def test_add_product_to_empty_category(self) -> None:
        """Тест добавления продукта в пустую категорию."""
        category = Category("Test", "Description", [])
        product = Product("Test Product", "Description", 100.0, 5)
        initial_count = Category.product_count

        category.add_product(product)

        assert len(category._Category__products) == 1  # type: ignore[attr-defined]
        assert category._Category__products[0] == product  # type: ignore[attr-defined]
        assert Category.product_count == initial_count + 1
        assert "Test Product" in category.products

    def test_add_product_to_category_with_products(self) -> None:
        """Тест добавления продукта в категорию с существующими продуктами."""
        product1 = Product("Product 1", "Description 1", 100.0, 5)
        category = Category("Test", "Description", [product1])
        product2 = Product("Product 2", "Description 2", 200.0, 10)
        initial_count = Category.product_count

        category.add_product(product2)

        assert len(category._Category__products) == 2  # type: ignore[attr-defined]
        assert category._Category__products[0] == product1  # type: ignore[attr-defined]
        assert category._Category__products[1] == product2  # type: ignore[attr-defined]
        assert Category.product_count == initial_count + 1
        assert "Product 1" in category.products
        assert "Product 2" in category.products

    def test_add_multiple_products(self) -> None:
        """Тест добавления нескольких продуктов."""
        category = Category("Test", "Description", [])
        products = [Product(f"Product {i}", f"Description {i}", 100.0 * i, i) for i in range(1, 4)]
        initial_count = Category.product_count

        for product in products:
            category.add_product(product)

        assert len(category._Category__products) == 3  # type: ignore[attr-defined]
        assert Category.product_count == initial_count + 3
        products_str = category.products
        for i in range(1, 4):
            assert f"Product {i}" in products_str

    # ============================================================================
    # Начало разработки нового функционала в рамках работы над проектом homework_16_1
    # ============================================================================

    def test_add_product_accepts_product(self) -> None:
        """Тест, что можно добавить Product в категорию."""
        category = Category("Test", "Description", [])
        product = Product("Test Product", "Description", 100.0, 5)
        initial_count = Category.product_count

        category.add_product(product)

        assert len(category._Category__products) == 1  # type: ignore[attr-defined]
        assert Category.product_count == initial_count + 1

    def test_add_product_accepts_smartphone(self) -> None:
        """Тест, что можно добавить Smartphone в категорию."""
        category = Category("Test", "Description", [])
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
        initial_count = Category.product_count

        category.add_product(smartphone)

        assert len(category._Category__products) == 1  # type: ignore[attr-defined]
        assert Category.product_count == initial_count + 1
        assert isinstance(category._Category__products[0], Smartphone)  # type: ignore[attr-defined]

    def test_add_product_accepts_lawn_grass(self) -> None:
        """Тест, что можно добавить LawnGrass в категорию."""
        category = Category("Test", "Description", [])
        grass = LawnGrass("Газонная трава", "Элитная трава для газона", 500.0, 20, "Россия", "7 дней", "Зеленый")
        initial_count = Category.product_count

        category.add_product(grass)

        assert len(category._Category__products) == 1  # type: ignore[attr-defined]
        assert Category.product_count == initial_count + 1
        assert isinstance(category._Category__products[0], LawnGrass)  # type: ignore[attr-defined]

    def test_add_product_rejects_string(self) -> None:
        """Тест, что нельзя добавить строку в категорию."""
        category = Category("Test", "Description", [])
        with pytest.raises(TypeError, match="Можно добавлять только объекты класса Product и его наследников"):
            category.add_product("Not a product")  # type: ignore

    def test_add_product_rejects_int(self) -> None:
        """Тест, что нельзя добавить число в категорию."""
        category = Category("Test", "Description", [])
        with pytest.raises(TypeError, match="Можно добавлять только объекты класса Product и его наследников"):
            category.add_product(123)  # type: ignore

    def test_add_product_rejects_list(self) -> None:
        """Тест, что нельзя добавить список в категорию."""
        category = Category("Test", "Description", [])
        with pytest.raises(TypeError, match="Можно добавлять только объекты класса Product и его наследников"):
            category.add_product([1, 2, 3])  # type: ignore

    def test_add_product_rejects_dict(self) -> None:
        """Тест, что нельзя добавить словарь в категорию."""
        category = Category("Test", "Description", [])
        with pytest.raises(TypeError, match="Можно добавлять только объекты класса Product и его наследников"):
            category.add_product({"name": "Product"})  # type: ignore

    def test_add_product_rejects_none(self) -> None:
        """Тест, что нельзя добавить None в категорию."""
        category = Category("Test", "Description", [])
        with pytest.raises(TypeError, match="Можно добавлять только объекты класса Product и его наследников"):
            category.add_product(None)  # type: ignore

    def test_add_product_rejects_duplicate_same_object(self) -> None:
        """Тест, что нельзя добавить тот же объект дважды."""
        category = Category("Test", "Description", [])
        product = Product("Test Product", "Description", 100.0, 5)
        category.add_product(product)

        with pytest.raises(ValueError, match="Продукт с такими же атрибутами уже существует в категории"):
            category.add_product(product)

    def test_add_product_rejects_duplicate_same_attributes(self) -> None:
        """Тест, что нельзя добавить продукт с такими же атрибутами."""
        category = Category("Test", "Description", [])
        product1 = Product("Test Product", "Description", 100.0, 5)
        product2 = Product("Test Product", "Description", 100.0, 5)  # Те же атрибуты
        category.add_product(product1)

        with pytest.raises(ValueError, match="Продукт с такими же атрибутами уже существует в категории"):
            category.add_product(product2)

    def test_add_product_rejects_duplicate_smartphone(self) -> None:
        """Тест, что нельзя добавить смартфон с такими же атрибутами."""
        category = Category("Test", "Description", [])
        smartphone1 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")
        smartphone2 = Smartphone("Phone", "Desc", 100.0, 5, 95.5, "Model", 256, "Black")  # Те же атрибуты
        category.add_product(smartphone1)

        with pytest.raises(ValueError, match="Продукт с такими же атрибутами уже существует в категории"):
            category.add_product(smartphone2)

    def test_add_product_rejects_duplicate_lawn_grass(self) -> None:
        """Тест, что нельзя добавить газонную траву с такими же атрибутами."""
        category = Category("Test", "Description", [])
        grass1 = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")
        grass2 = LawnGrass("Grass", "Desc", 50.0, 10, "Russia", "7 days", "Green")  # Те же атрибуты
        category.add_product(grass1)

        with pytest.raises(ValueError, match="Продукт с такими же атрибутами уже существует в категории"):
            category.add_product(grass2)

    def test_add_product_allows_different_products(self) -> None:
        """Тест, что можно добавить разные продукты."""
        category = Category("Test", "Description", [])
        product1 = Product("Product 1", "Description 1", 100.0, 5)
        product2 = Product("Product 2", "Description 2", 200.0, 10)
        category.add_product(product1)
        category.add_product(product2)

        assert len(category._Category__products) == 2  # type: ignore[attr-defined]

    def test_add_product_allows_similar_but_different_products(self) -> None:
        """Тест, что можно добавить продукты с похожими, но разными атрибутами."""
        category = Category("Test", "Description", [])
        product1 = Product("Product", "Description", 100.0, 5)
        product2 = Product("Product", "Description", 200.0, 5)  # Разная цена
        product3 = Product("Product", "Description", 100.0, 10)  # Разное количество
        category.add_product(product1)
        category.add_product(product2)
        category.add_product(product3)

        assert len(category._Category__products) == 3  # type: ignore[attr-defined]


class TestCategoryStr:
    """Тесты для метода __str__ класса Category."""

    def test_str_representation_with_products(self) -> None:
        """Тест строкового представления категории с продуктами."""
        product1 = Product("Product 1", "Description 1", 100.0, 5)
        product2 = Product("Product 2", "Description 2", 200.0, 10)
        category = Category("Смартфоны", "Description", [product1, product2])
        result = str(category)
        assert result == "Смартфоны, количество продуктов: 15 шт."  # 5 + 10 = 15

    def test_str_with_empty_category(self) -> None:
        """Тест строкового представления пустой категории."""
        category = Category("Пустая категория", "Description", [])
        result = str(category)
        assert result == "Пустая категория, количество продуктов: 0 шт."

    def test_str_calculates_total_quantity_correctly(self) -> None:
        """Тест правильного подсчета общей суммы quantity всех продуктов."""
        products = [
            Product("Product 1", "Description 1", 100.0, 3),
            Product("Product 2", "Description 2", 200.0, 7),
            Product("Product 3", "Description 3", 300.0, 10),
        ]
        category = Category("Test Category", "Description", products)
        result = str(category)
        assert result == "Test Category, количество продуктов: 20 шт."  # 3 + 7 + 10 = 20

    def test_str_with_zero_quantity_products(self) -> None:
        """Тест строкового представления категории с продуктами с нулевым количеством."""
        product1 = Product("Product 1", "Description 1", 100.0, 0)
        product2 = Product("Product 2", "Description 2", 200.0, 0)
        category = Category("Test Category", "Description", [product1, product2])
        result = str(category)
        assert result == "Test Category, количество продуктов: 0 шт."

    def test_str_with_single_product(self) -> None:
        """Тест строкового представления категории с одним продуктом."""
        product = Product("Product 1", "Description 1", 100.0, 15)
        category = Category("Test Category", "Description", [product])
        result = str(category)
        assert result == "Test Category, количество продуктов: 15 шт."


class TestCategoryIteration:
    """Тесты для метода __iter__ класса Category."""

    def test_iteration_over_products(self) -> None:
        """Тест итерации по продуктам категории в цикле for."""
        product1 = Product("Product 1", "Description 1", 100.0, 5)
        product2 = Product("Product 2", "Description 2", 200.0, 10)
        product3 = Product("Product 3", "Description 3", 300.0, 15)
        category = Category("Test Category", "Description", [product1, product2, product3])

        products_list = list(category)
        assert len(products_list) == 3
        assert products_list[0] == product1
        assert products_list[1] == product2
        assert products_list[2] == product3

    def test_iteration_with_for_loop(self) -> None:
        """Тест использования категории в цикле for."""
        product1 = Product("Product 1", "Description 1", 100.0, 5)
        product2 = Product("Product 2", "Description 2", 200.0, 10)
        category = Category("Test Category", "Description", [product1, product2])

        product_names = [product.name for product in category]
        assert product_names == ["Product 1", "Product 2"]

    def test_iteration_with_empty_category(self) -> None:
        """Тест итерации по пустой категории."""
        category = Category("Empty Category", "Description", [])
        products_list = list(category)
        assert len(products_list) == 0

    def test_multiple_iterations(self) -> None:
        """Тест множественных итераций по одной категории."""
        product1 = Product("Product 1", "Description 1", 100.0, 5)
        product2 = Product("Product 2", "Description 2", 200.0, 10)
        category = Category("Test Category", "Description", [product1, product2])

        # Первая итерация
        products1 = list(category)
        assert len(products1) == 2

        # Вторая итерация
        products2 = list(category)
        assert len(products2) == 2
        assert products1 == products2

    def test_iteration_returns_product_objects(self) -> None:
        """Тест, что итерация возвращает объекты класса Product."""
        product = Product("Product 1", "Description 1", 100.0, 5)
        category = Category("Test Category", "Description", [product])

        for item in category:
            assert isinstance(item, Product)
            assert item.name == "Product 1"
