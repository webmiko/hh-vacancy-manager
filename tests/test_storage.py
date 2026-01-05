"""Тесты для работы с файлами.

Модуль содержит тесты для абстрактного класса FileSaverBase
и класса JSONSaver.
"""

# 1. Импорты стандартной библиотеки
import json
from pathlib import Path
from unittest.mock import Mock

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from src.storage.base import FileSaverBase
from src.storage.json_saver import JSONSaver
from src.vacancy.vacancy import Vacancy

# 4. Константы модуля
# (нет констант)


class TestFileSaverBase:
    """Тесты для абстрактного класса FileSaverBase."""

    def test_file_saver_base_is_abstract(self) -> None:
        """Тест, что нельзя создать экземпляр абстрактного класса."""
        with pytest.raises(TypeError):
            FileSaverBase()  # type: ignore

    def test_file_saver_base_has_abstract_methods(self) -> None:
        """Тест, что абстрактные методы определены."""
        assert hasattr(FileSaverBase, "add_vacancy")
        assert hasattr(FileSaverBase, "get_vacancies")
        assert hasattr(FileSaverBase, "delete_vacancy")


class TestJSONSaver:
    """Тесты для класса JSONSaver."""

    def test_json_saver_initialization_default(self) -> None:
        """Тест инициализации JSONSaver с именем файла по умолчанию."""
        saver = JSONSaver()

        assert saver._filename == "vacancies.json"
        assert saver._file_path.name == "vacancies.json"

    def test_json_saver_initialization_custom_filename(self) -> None:
        """Тест инициализации JSONSaver с пользовательским именем файла."""
        saver = JSONSaver("custom_vacancies.json")

        assert saver._filename == "custom_vacancies.json"
        assert saver._file_path.name == "custom_vacancies.json"

    def test_json_saver_inherits_from_base(self) -> None:
        """Тест, что JSONSaver наследуется от FileSaverBase."""
        assert issubclass(JSONSaver, FileSaverBase)

    def test_add_vacancy(self, json_saver: JSONSaver, vacancy_object: Vacancy) -> None:
        """Тест добавления вакансии в файл."""
        json_saver.add_vacancy(vacancy_object)

        assert json_saver._file_path.exists()

        with open(json_saver._file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["name"] == vacancy_object.name
        assert data[0]["url"] == vacancy_object.url

    def test_add_vacancy_duplicate(self, json_saver: JSONSaver, vacancy_object: Vacancy) -> None:
        """Тест предотвращения дублирования вакансий."""
        json_saver.add_vacancy(vacancy_object)
        json_saver.add_vacancy(vacancy_object)  # Попытка добавить ту же вакансию

        with open(json_saver._file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1  # Дубликат не должен быть добавлен

    def test_get_vacancies_empty_file(self, json_saver: JSONSaver) -> None:
        """Тест получения вакансий из пустого файла."""
        vacancies = json_saver.get_vacancies()

        assert vacancies == []

    def test_get_vacancies_with_data(self, json_saver: JSONSaver, vacancy_object: Vacancy) -> None:
        """Тест получения вакансий из файла с данными."""
        json_saver.add_vacancy(vacancy_object)
        vacancies = json_saver.get_vacancies()

        assert len(vacancies) == 1
        assert vacancies[0]["name"] == vacancy_object.name

    def test_get_vacancies_filter_by_keywords(self, json_saver: JSONSaver) -> None:
        """Тест фильтрации вакансий по ключевым словам."""
        vacancy1 = Vacancy("Python Developer", "https://test1.ru", None, "Python Django Flask")
        vacancy2 = Vacancy("Java Developer", "https://test2.ru", None, "Java Spring")

        json_saver.add_vacancy(vacancy1)
        json_saver.add_vacancy(vacancy2)

        filtered = json_saver.get_vacancies(filter_words=["Python"])

        assert len(filtered) == 1
        assert filtered[0]["name"] == "Python Developer"

    def test_get_vacancies_filter_by_salary(self, json_saver: JSONSaver) -> None:
        """Тест фильтрации вакансий по диапазону зарплат."""
        vacancy1 = Vacancy("High Salary", "https://test1.ru", {"from": 200000, "currency": "RUR"}, "Desc")
        vacancy2 = Vacancy("Low Salary", "https://test2.ru", {"from": 50000, "currency": "RUR"}, "Desc")

        json_saver.add_vacancy(vacancy1)
        json_saver.add_vacancy(vacancy2)

        filtered = json_saver.get_vacancies(salary_from=100000, salary_to=300000)

        assert len(filtered) == 1
        assert filtered[0]["name"] == "High Salary"

    def test_delete_vacancy(self, json_saver: JSONSaver, vacancy_object: Vacancy) -> None:
        """Тест удаления вакансии из файла."""
        json_saver.add_vacancy(vacancy_object)
        json_saver.delete_vacancy(vacancy_object)

        vacancies = json_saver.get_vacancies()
        assert len(vacancies) == 0

    def test_delete_vacancy_not_found(self, json_saver: JSONSaver, vacancy_object: Vacancy) -> None:
        """Тест удаления несуществующей вакансии."""
        with pytest.raises(ValueError, match="не найдена"):
            json_saver.delete_vacancy(vacancy_object)

    def test_load_vacancies_invalid_json(self, json_saver: JSONSaver) -> None:
        """Тест обработки поврежденного JSON файла."""
        # Создаем файл с невалидным JSON
        with open(json_saver._file_path, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        vacancies = json_saver.get_vacancies()

        assert vacancies == []

    def test_load_vacancies_not_list(self, json_saver: JSONSaver) -> None:
        """Тест обработки файла, содержащего не список."""
        # Создаем файл с JSON объектом (не список)
        with open(json_saver._file_path, "w", encoding="utf-8") as f:
            json.dump({"key": "value"}, f)

        vacancies = json_saver.get_vacancies()

        assert vacancies == []

    def test_save_vacancies_permission_error(self, json_saver: JSONSaver) -> None:
        """Тест обработки ошибки прав доступа при сохранении."""
        # Создаем файл и делаем его только для чтения (на Unix)
        import os

        json_saver._file_path.touch()
        try:
            os.chmod(json_saver._file_path, 0o444)  # Только чтение

            with pytest.raises(IOError):
                json_saver._save_vacancies([{"name": "Test", "url": "https://test.ru", "salary": None, "description": ""}])
        finally:
            os.chmod(json_saver._file_path, 0o644)  # Восстанавливаем права

    def test_load_vacancies_permission_error(self, json_saver: JSONSaver) -> None:
        """Тест обработки ошибки прав доступа при чтении."""
        # Создаем файл и делаем его недоступным для чтения
        import os

        json_saver._file_path.touch()
        try:
            os.chmod(json_saver._file_path, 0o000)  # Нет прав

            vacancies = json_saver._load_vacancies()

            assert vacancies == []
        finally:
            os.chmod(json_saver._file_path, 0o644)  # Восстанавливаем права

    def test_load_vacancies_memory_error(self, json_saver: JSONSaver) -> None:
        """Тест обработки MemoryError при загрузке (критично для пользователя)."""
        # Мокаем open чтобы вызвать MemoryError
        from unittest.mock import mock_open, patch

        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("json.load", side_effect=MemoryError("Out of memory")):
                vacancies = json_saver._load_vacancies()

                # Должно вернуть пустой список вместо падения программы
                assert vacancies == []

    def test_load_vacancies_unexpected_exception(self, json_saver: JSONSaver) -> None:
        """Тест обработки неожиданного исключения при загрузке (критично для пользователя)."""
        # Мокаем open чтобы вызвать неожиданное исключение
        from unittest.mock import mock_open, patch

        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("json.load", side_effect=RuntimeError("Unexpected error")):
                vacancies = json_saver._load_vacancies()

                # Должно вернуть пустой список вместо падения программы
                assert vacancies == []

    def test_save_vacancies_memory_error(self, json_saver: JSONSaver, vacancy_object: Vacancy) -> None:
        """Тест обработки MemoryError при сохранении (критично для пользователя)."""
        from unittest.mock import mock_open, patch

        json_saver.add_vacancy(vacancy_object)

        # Мокаем open чтобы вызвать MemoryError при сохранении
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump", side_effect=MemoryError("Out of memory")):
                with pytest.raises(IOError, match="Не удалось сохранить"):
                    json_saver._save_vacancies([{"name": "Test", "url": "https://test.ru", "salary": None, "description": ""}])

    def test_save_vacancies_unexpected_exception(self, json_saver: JSONSaver) -> None:
        """Тест обработки неожиданного исключения при сохранении (критично для пользователя)."""
        from unittest.mock import mock_open, patch

        # Мокаем open чтобы вызвать неожиданное исключение
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump", side_effect=RuntimeError("Unexpected error")):
                with pytest.raises(IOError, match="Не удалось сохранить"):
                    json_saver._save_vacancies([{"name": "Test", "url": "https://test.ru", "salary": None, "description": ""}])

    def test_add_vacancy_invalid_object(self, json_saver: JSONSaver) -> None:
        """Тест добавления невалидного объекта вакансии."""
        invalid_vacancy = Mock()
        del invalid_vacancy.name  # Удаляем атрибут name

        with pytest.raises(ValueError):
            json_saver.add_vacancy(invalid_vacancy)

    def test_delete_vacancy_invalid_object(self, json_saver: JSONSaver) -> None:
        """Тест удаления невалидного объекта вакансии."""
        invalid_vacancy = Mock()
        del invalid_vacancy.name  # Удаляем атрибут name

        with pytest.raises(ValueError):
            json_saver.delete_vacancy(invalid_vacancy)

    def test_matches_salary_range_no_salary(self) -> None:
        """Тест проверки диапазона зарплат без зарплаты."""
        saver = JSONSaver()

        result = saver._matches_salary_range(None, 100000, 200000)

        assert result is False

    def test_matches_salary_range_both_limits(self) -> None:
        """Тест проверки диапазона зарплат с обеими границами."""
        saver = JSONSaver()

        # Зарплата в диапазоне
        salary1 = {"from": 120000, "to": 180000, "currency": "RUR"}
        assert saver._matches_salary_range(salary1, 100000, 200000) is True

        # Зарплата ниже диапазона
        salary2 = {"from": 50000, "to": 80000, "currency": "RUR"}
        assert saver._matches_salary_range(salary2, 100000, 200000) is False

        # Зарплата выше диапазона
        salary3 = {"from": 250000, "to": 300000, "currency": "RUR"}
        assert saver._matches_salary_range(salary3, 100000, 200000) is False

    def test_matches_salary_range_only_from(self) -> None:
        """Тест проверки диапазона зарплат только с минимальной границей."""
        saver = JSONSaver()

        salary = {"from": 150000, "currency": "RUR"}
        assert saver._matches_salary_range(salary, 100000, None) is True
        assert saver._matches_salary_range(salary, 200000, None) is False

    def test_matches_salary_range_only_to(self) -> None:
        """Тест проверки диапазона зарплат только с максимальной границей."""
        saver = JSONSaver()

        salary = {"to": 150000, "currency": "RUR"}
        assert saver._matches_salary_range(salary, None, 200000) is True
        assert saver._matches_salary_range(salary, None, 100000) is False

    def test_get_vacancies_no_filter(self, json_saver: JSONSaver, vacancy_object: Vacancy) -> None:
        """Тест получения вакансий без фильтров."""
        json_saver.add_vacancy(vacancy_object)
        vacancies = json_saver.get_vacancies()

        assert len(vacancies) == 1

    def test_get_vacancies_exception_handling(self, json_saver: JSONSaver) -> None:
        """Тест обработки исключений при загрузке вакансий."""
        # Создаем файл с невалидным JSON
        with open(json_saver._file_path, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        vacancies = json_saver._load_vacancies()

        assert vacancies == []

    def test_load_vacancies_empty_content(self, json_saver: JSONSaver) -> None:
        """Тест обработки файла с пустым содержимым."""
        # Создаем пустой файл
        json_saver._file_path.touch()

        vacancies = json_saver._load_vacancies()

        assert vacancies == []

    def test_matches_salary_range_both_none(self) -> None:
        """Тест проверки диапазона зарплат когда обе границы None."""
        saver = JSONSaver()

        salary = {"from": None, "to": None, "currency": "RUR"}
        result = saver._matches_salary_range(salary, 100000, 200000)

        assert result is False
