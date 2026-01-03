"""Тесты для вспомогательных функций.

Модуль содержит тесты для функций из модулей utils.
"""

# 1. Импорты стандартной библиотеки
# (нет импортов стандартной библиотеки)

# 2. Импорты сторонних библиотек
# (нет импортов сторонних библиотек)

# 3. Импорты из проекта
from src.utils.input_utils import validate_keyword, validate_top_n
from src.utils.vacancy_utils import filter_vacancies_by_keywords, get_top_vacancies, sort_vacancies_by_salary
from src.vacancy.vacancy import Vacancy

# 4. Константы модуля
# (нет констант)


class TestInputUtils:
    """Тесты для функций валидации ввода."""

    def test_validate_top_n_valid(self) -> None:
        """Тест валидации корректного значения для топ N."""
        assert validate_top_n("10") == 10
        assert validate_top_n("1") == 1
        assert validate_top_n("1000") == 1000

    def test_validate_top_n_invalid(self) -> None:
        """Тест валидации некорректного значения для топ N."""
        assert validate_top_n("-5") is None
        assert validate_top_n("0") is None
        assert validate_top_n("1001") is None
        assert validate_top_n("abc") is None
        assert validate_top_n("") is None

    def test_validate_keyword_valid(self) -> None:
        """Тест валидации корректного ключевого слова."""
        assert validate_keyword("Python") == "Python"
        assert validate_keyword("  Django  ") == "Django"

    def test_validate_keyword_invalid(self) -> None:
        """Тест валидации некорректного ключевого слова."""
        assert validate_keyword("") is None
        assert validate_keyword("   ") is None


class TestVacancyUtils:
    """Тесты для функций работы с вакансиями."""

    def test_filter_vacancies_by_keywords(self) -> None:
        """Тест фильтрации вакансий по ключевым словам."""
        vacancy1 = Vacancy("Python Dev", "https://test1.ru", None, "Python Django разработка")
        vacancy2 = Vacancy("Java Dev", "https://test2.ru", None, "Java Spring разработка")
        vacancy3 = Vacancy("Full Stack", "https://test3.ru", None, "Python JavaScript разработка")

        vacancies = [vacancy1, vacancy2, vacancy3]

        filtered = filter_vacancies_by_keywords(vacancies, ["Python"])

        assert len(filtered) == 2
        # Проверяем по URL, так как объекты сравниваются по зарплате
        filtered_urls = [v.url for v in filtered]
        assert vacancy1.url in filtered_urls
        assert vacancy3.url in filtered_urls
        assert vacancy2.url not in filtered_urls

    def test_filter_vacancies_by_keywords_empty(self) -> None:
        """Тест фильтрации с пустым списком вакансий."""
        filtered = filter_vacancies_by_keywords([], ["Python"])

        assert filtered == []

    def test_filter_vacancies_by_keywords_no_keywords(self) -> None:
        """Тест фильтрации без ключевых слов."""
        vacancy = Vacancy("Test", "https://test.ru", None, "Description")
        vacancies = [vacancy]

        filtered = filter_vacancies_by_keywords(vacancies, [])

        assert filtered == vacancies

    def test_sort_vacancies_by_salary(self) -> None:
        """Тест сортировки вакансий по зарплате."""
        vacancy1 = Vacancy("Low", "https://test1.ru", {"from": 50000, "currency": "RUR"}, "Desc")
        vacancy2 = Vacancy("High", "https://test2.ru", {"from": 200000, "currency": "RUR"}, "Desc")
        vacancy3 = Vacancy("Medium", "https://test3.ru", {"from": 100000, "currency": "RUR"}, "Desc")

        vacancies = [vacancy1, vacancy2, vacancy3]
        sorted_vacancies = sort_vacancies_by_salary(vacancies, reverse=True)

        assert sorted_vacancies[0] == vacancy2  # Самая высокая зарплата
        assert sorted_vacancies[1] == vacancy3
        assert sorted_vacancies[2] == vacancy1  # Самая низкая зарплата

    def test_sort_vacancies_by_salary_ascending(self) -> None:
        """Тест сортировки вакансий по зарплате по возрастанию."""
        vacancy1 = Vacancy("Low", "https://test1.ru", {"from": 50000, "currency": "RUR"}, "Desc")
        vacancy2 = Vacancy("High", "https://test2.ru", {"from": 200000, "currency": "RUR"}, "Desc")

        vacancies = [vacancy2, vacancy1]
        sorted_vacancies = sort_vacancies_by_salary(vacancies, reverse=False)

        assert sorted_vacancies[0] == vacancy1
        assert sorted_vacancies[1] == vacancy2

    def test_sort_vacancies_by_salary_empty(self) -> None:
        """Тест сортировки пустого списка."""
        sorted_vacancies = sort_vacancies_by_salary([])

        assert sorted_vacancies == []

    def test_get_top_vacancies(self) -> None:
        """Тест получения топ N вакансий."""
        vacancies = [
            Vacancy(f"Vacancy {i}", f"https://test{i}.ru", {"from": i * 10000, "currency": "RUR"}, "Desc")
            for i in range(1, 6)
        ]

        top_3 = get_top_vacancies(vacancies, 3)

        assert len(top_3) == 3
        assert top_3 == vacancies[:3]

    def test_get_top_vacancies_all(self) -> None:
        """Тест получения всех вакансий, если N больше размера списка."""
        vacancies = [
            Vacancy(f"Vacancy {i}", f"https://test{i}.ru", {"from": i * 10000, "currency": "RUR"}, "Desc")
            for i in range(1, 4)
        ]

        top_10 = get_top_vacancies(vacancies, 10)

        assert len(top_10) == 3
        assert top_10 == vacancies

    def test_get_top_vacancies_invalid_n(self) -> None:
        """Тест получения топ N с некорректным значением."""
        vacancies = [Vacancy("Test", "https://test.ru", None, "Desc")]

        result = get_top_vacancies(vacancies, 0)
        assert result == []

        result = get_top_vacancies(vacancies, -5)
        assert result == []

        result = get_top_vacancies([], 5)
        assert result == []
