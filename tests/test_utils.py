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

    def test_sort_vacancies_by_salary(self, vacancies_with_salaries: List[Vacancy]) -> None:
        """Тест сортировки вакансий по зарплате."""
        sorted_vacancies = sort_vacancies_by_salary(vacancies_with_salaries, reverse=True)

        assert sorted_vacancies[0] == vacancies_with_salaries[2]  # Самая высокая зарплата
        assert sorted_vacancies[1] == vacancies_with_salaries[1]
        assert sorted_vacancies[2] == vacancies_with_salaries[0]  # Самая низкая зарплата

    def test_sort_vacancies_by_salary_ascending(self, vacancies_with_salaries: List[Vacancy]) -> None:
        """Тест сортировки вакансий по зарплате по возрастанию."""
        # Используем только первые две вакансии из фикстуры
        vacancies = [vacancies_with_salaries[2], vacancies_with_salaries[0]]
        sorted_vacancies = sort_vacancies_by_salary(vacancies, reverse=False)

        assert sorted_vacancies[0] == vacancies_with_salaries[0]
        assert sorted_vacancies[1] == vacancies_with_salaries[2]

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

    def test_sort_vacancies_by_salary_type_error(self) -> None:
        """Тест обработки TypeError при сортировке (критично для пользователя)."""
        # Создаем объекты, которые не поддерживают сравнение
        from unittest.mock import Mock

        invalid_vacancy1 = Mock()
        invalid_vacancy2 = Mock()
        # Удаляем методы сравнения, чтобы вызвать TypeError
        del invalid_vacancy1.__lt__
        del invalid_vacancy1.__gt__

        vacancies = [invalid_vacancy1, invalid_vacancy2]

        # Должно вернуть пустой список вместо падения программы
        result = sort_vacancies_by_salary(vacancies, reverse=True)

        assert result == []

    def test_sort_vacancies_by_salary_attribute_error(self) -> None:
        """Тест обработки AttributeError при сортировке (критично для пользователя)."""
        # Создаем объекты, которые вызывают AttributeError при сравнении
        from unittest.mock import Mock

        invalid_vacancy1 = Mock()
        invalid_vacancy2 = Mock()

        # Настраиваем моки так, чтобы сравнение вызывало AttributeError
        def raise_attribute_error(*args, **kwargs):
            raise AttributeError("Missing attribute for comparison")

        invalid_vacancy1.__lt__ = raise_attribute_error
        invalid_vacancy1.__gt__ = raise_attribute_error

        vacancies = [invalid_vacancy1, invalid_vacancy2]

        # Должно вернуть пустой список вместо падения программы
        result = sort_vacancies_by_salary(vacancies, reverse=True)

        assert result == []

    def test_filter_vacancies_by_keywords_missing_description(self) -> None:
        """Тест фильтрации вакансий без атрибута description (критично для пользователя)."""
        from unittest.mock import Mock

        # Создаем вакансию без description
        vacancy_no_desc = Mock()
        vacancy_no_desc.description = None
        del vacancy_no_desc.description  # Удаляем атрибут

        vacancy_with_desc = Vacancy("Test", "https://test.ru", None, "Python Django")

        vacancies = [vacancy_no_desc, vacancy_with_desc]

        # Должно обработать ошибку и продолжить работу
        filtered = filter_vacancies_by_keywords(vacancies, ["Python"])

        # Должна остаться только вакансия с description
        assert len(filtered) == 1
        assert filtered[0] == vacancy_with_desc
