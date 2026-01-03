"""Тесты для класса Vacancy.

Модуль содержит тесты для класса вакансии, включая валидацию,
методы сравнения и преобразование из JSON.
"""

# 1. Импорты стандартной библиотеки
from typing import Any, Dict, List

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from src.vacancy.vacancy import Vacancy

# 4. Константы модуля
# (нет констант)


class TestVacancy:
    """Тесты для класса Vacancy."""

    def test_vacancy_creation(self, sample_vacancy_data: Dict[str, Any]) -> None:
        """Тест создания вакансии с валидными данными."""
        snippet = sample_vacancy_data.get("snippet", {})
        description = f"{snippet.get('requirement', '')} {snippet.get('responsibility', '')}".strip()

        vacancy = Vacancy(
            name=sample_vacancy_data["name"],
            url=sample_vacancy_data["alternate_url"],
            salary=sample_vacancy_data["salary"],
            description=description,
        )

        assert vacancy.name == sample_vacancy_data["name"]
        assert vacancy.url == sample_vacancy_data["alternate_url"]
        assert vacancy.salary == sample_vacancy_data["salary"]
        assert vacancy.description == description

    def test_vacancy_creation_no_salary(self, sample_vacancy_data_no_salary: Dict[str, Any]) -> None:
        """Тест создания вакансии без зарплаты."""
        snippet = sample_vacancy_data_no_salary.get("snippet", {})
        description = f"{snippet.get('requirement', '')} {snippet.get('responsibility', '')}".strip()

        vacancy = Vacancy(
            name=sample_vacancy_data_no_salary["name"],
            url=sample_vacancy_data_no_salary["alternate_url"],
            salary=None,
            description=description,
        )

        assert vacancy.salary is None

    def test_vacancy_validation_empty_name(self) -> None:
        """Тест валидации пустого названия."""
        with pytest.raises(ValueError, match="Название вакансии не может быть пустым"):
            Vacancy(name="", url="https://test.ru", salary=None, description="Test")

    def test_vacancy_validation_empty_url(self) -> None:
        """Тест валидации пустой ссылки."""
        with pytest.raises(ValueError, match="Ссылка на вакансию не может быть пустой"):
            Vacancy(name="Test", url="", salary=None, description="Test")

    def test_vacancy_comparison_lt(self, vacancy_object: Vacancy) -> None:
        """Тест сравнения вакансий (меньше)."""
        vacancy_lower = Vacancy("Test Lower", "https://test1.ru", {"from": 50000, "currency": "RUR"}, "Desc")
        vacancy_higher = Vacancy("Test Higher", "https://test2.ru", {"from": 200000, "currency": "RUR"}, "Desc")

        assert vacancy_lower < vacancy_higher
        assert not (vacancy_higher < vacancy_lower)

    def test_vacancy_comparison_gt(self, vacancy_object: Vacancy) -> None:
        """Тест сравнения вакансий (больше)."""
        vacancy_lower = Vacancy("Test Lower", "https://test1.ru", {"from": 50000, "currency": "RUR"}, "Desc")
        vacancy_higher = Vacancy("Test Higher", "https://test2.ru", {"from": 200000, "currency": "RUR"}, "Desc")

        assert vacancy_higher > vacancy_lower
        assert not (vacancy_lower > vacancy_higher)

    def test_vacancy_comparison_eq(self) -> None:
        """Тест сравнения вакансий (равно)."""
        vacancy1 = Vacancy("Test", "https://test1.ru", {"from": 100000, "currency": "RUR"}, "Desc")
        vacancy2 = Vacancy("Test", "https://test2.ru", {"from": 100000, "currency": "RUR"}, "Desc")
        vacancy3 = Vacancy("Test", "https://test3.ru", None, "Desc")

        assert vacancy1 == vacancy2
        assert vacancy3 == vacancy3  # Обе без зарплаты считаются равными

    def test_vacancy_comparison_salary_range(self, vacancy_with_salary_range: Vacancy) -> None:
        """Тест сравнения вакансий с диапазоном зарплат."""
        vacancy_fixed = Vacancy("Test Fixed", "https://test2.ru", {"from": 120000, "currency": "RUR"}, "Desc")

        # Средняя зарплата диапазона = 125000, фиксированная = 120000
        assert vacancy_with_salary_range > vacancy_fixed

    def test_vacancy_comparison_no_salary(self, vacancy_no_salary: Vacancy) -> None:
        """Тест сравнения вакансий без зарплаты."""
        vacancy2 = Vacancy("Test2", "https://test2.ru", None, "Desc")
        vacancy_with_salary = Vacancy("Test3", "https://test3.ru", {"from": 100000, "currency": "RUR"}, "Desc")

        assert vacancy_no_salary == vacancy2  # Обе без зарплаты
        assert vacancy_with_salary > vacancy_no_salary  # С зарплатой больше чем без

    def test_vacancy_str(self, vacancy_object: Vacancy) -> None:
        """Тест строкового представления вакансии."""
        str_repr = str(vacancy_object)

        assert "Python Developer" in str_repr
        assert "https://hh.ru/vacancy/123456" in str_repr
        assert "Зарплата" in str_repr

    def test_vacancy_str_no_salary(self) -> None:
        """Тест строкового представления вакансии без зарплаты."""
        vacancy = Vacancy("Test", "https://test.ru", None, "Desc")
        str_repr = str(vacancy)

        assert "Зарплата не указана" in str_repr

    def test_cast_to_object_list(self, sample_vacancies_list: List[Dict[str, Any]]) -> None:
        """Тест преобразования списка словарей в список объектов."""
        vacancies = Vacancy.cast_to_object_list(sample_vacancies_list)

        assert len(vacancies) == 2
        assert all(isinstance(v, Vacancy) for v in vacancies)
        assert vacancies[0].name == "Python Developer"
        assert vacancies[1].name == "Junior Developer"

    def test_cast_to_object_list_invalid_data(self) -> None:
        """Тест преобразования с некорректными данными."""
        invalid_data = [
            {"name": "", "alternate_url": "https://test.ru"},  # Пустое name
            {"alternate_url": "https://test.ru"},  # Нет name
            "invalid",  # Не словарь
        ]

        vacancies = Vacancy.cast_to_object_list(invalid_data)

        # Некорректные данные должны быть пропущены
        assert len(vacancies) == 0

    def test_vacancy_slots(self, vacancy_object: Vacancy) -> None:
        """Тест использования __slots__."""
        # Проверяем, что __slots__ определен
        assert hasattr(Vacancy, "__slots__")

        # Проверяем, что нельзя добавить новый атрибут
        with pytest.raises(AttributeError):
            vacancy_object.new_attribute = "test"  # type: ignore

    def test_vacancy_validation_name_not_string(self) -> None:
        """Тест валидации названия - не строка."""
        with pytest.raises(ValueError, match="должно быть строкой"):
            Vacancy(name=123, url="https://test.ru", salary=None, description="Test")

    def test_vacancy_validation_url_not_string(self) -> None:
        """Тест валидации URL - не строка."""
        with pytest.raises(ValueError, match="должна быть строкой"):
            Vacancy(name="Test", url=123, salary=None, description="Test")

    def test_vacancy_validation_salary_not_dict(self) -> None:
        """Тест валидации зарплаты - не словарь."""
        vacancy = Vacancy(name="Test", url="https://test.ru", salary="invalid", description="Test")

        assert vacancy.salary is None

    def test_vacancy_validation_description_not_string(self) -> None:
        """Тест валидации описания - не строка."""
        vacancy = Vacancy(name="Test", url="https://test.ru", salary=None, description=123)

        assert vacancy.description == ""

    def test_vacancy_str_salary_from_only(self) -> None:
        """Тест строкового представления с только from в зарплате."""
        vacancy = Vacancy("Test", "https://test.ru", {"from": 100000, "currency": "RUR"}, "Desc")
        str_repr = str(vacancy)

        assert "от 100000" in str_repr

    def test_vacancy_str_salary_to_only(self) -> None:
        """Тест строкового представления с только to в зарплате."""
        vacancy = Vacancy("Test", "https://test.ru", {"to": 150000, "currency": "RUR"}, "Desc")
        str_repr = str(vacancy)

        assert "до 150000" in str_repr

    def test_vacancy_get_salary_value_range(self) -> None:
        """Тест получения значения зарплаты для диапазона."""
        vacancy = Vacancy("Test", "https://test.ru", {"from": 100000, "to": 150000, "currency": "RUR"}, "Desc")

        # Проверяем через сравнение
        vacancy_single = Vacancy("Test2", "https://test2.ru", {"from": 120000, "currency": "RUR"}, "Desc")

        # Средняя зарплата диапазона = 125000, одиночная = 120000
        assert vacancy > vacancy_single

    def test_vacancy_get_salary_value_from_only(self, vacancy_no_salary: Vacancy) -> None:
        """Тест получения значения зарплаты только с from."""
        vacancy = Vacancy("Test", "https://test.ru", {"from": 100000, "currency": "RUR"}, "Desc")

        assert vacancy > vacancy_no_salary

    def test_vacancy_get_salary_value_to_only(self, vacancy_no_salary: Vacancy) -> None:
        """Тест получения значения зарплаты только с to."""
        vacancy = Vacancy("Test", "https://test.ru", {"to": 150000, "currency": "RUR"}, "Desc")

        assert vacancy > vacancy_no_salary

    def test_vacancy_comparison_not_implemented(self) -> None:
        """Тест сравнения с неверным типом."""
        vacancy = Vacancy("Test", "https://test.ru", None, "Desc")

        # Проверяем, что сравнение с неверным типом возвращает NotImplemented
        result_lt = vacancy.__lt__("not a vacancy")  # type: ignore
        result_le = vacancy.__le__("not a vacancy")  # type: ignore
        result_gt = vacancy.__gt__("not a vacancy")  # type: ignore
        result_ge = vacancy.__ge__("not a vacancy")  # type: ignore

        assert result_lt is NotImplemented
        assert result_le is NotImplemented
        assert result_gt is NotImplemented
        assert result_ge is NotImplemented

    def test_vacancy_repr(self, vacancy_object: Vacancy) -> None:
        """Тест представления вакансии для отладки."""
        repr_str = repr(vacancy_object)

        assert "Vacancy" in repr_str
        assert vacancy_object.name in repr_str
        assert vacancy_object.url in repr_str

    def test_cast_to_object_list_empty_snippet(self) -> None:
        """Тест преобразования с пустым snippet."""
        data = [
            {
                "name": "Test",
                "alternate_url": "https://test.ru",
                "salary": None,
                "snippet": {},
            }
        ]

        vacancies = Vacancy.cast_to_object_list(data)

        assert len(vacancies) == 1
        assert vacancies[0].description == ""

    def test_cast_to_object_list_missing_snippet(self) -> None:
        """Тест преобразования без snippet."""
        data = [
            {
                "name": "Test",
                "alternate_url": "https://test.ru",
                "salary": None,
            }
        ]

        vacancies = Vacancy.cast_to_object_list(data)

        assert len(vacancies) == 1
        assert vacancies[0].description == ""
