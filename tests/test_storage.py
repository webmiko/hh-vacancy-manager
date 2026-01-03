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

    def test_add_vacancy(self, temp_json_file: Path, vacancy_object: Vacancy) -> None:
        """Тест добавления вакансии в файл."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        saver.add_vacancy(vacancy_object)

        assert temp_json_file.exists()

        with open(temp_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["name"] == vacancy_object.name
        assert data[0]["url"] == vacancy_object.url

    def test_add_vacancy_duplicate(self, temp_json_file: Path, vacancy_object: Vacancy) -> None:
        """Тест предотвращения дублирования вакансий."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        saver.add_vacancy(vacancy_object)
        saver.add_vacancy(vacancy_object)  # Попытка добавить ту же вакансию

        with open(temp_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1  # Дубликат не должен быть добавлен

    def test_get_vacancies_empty_file(self, temp_json_file: Path) -> None:
        """Тест получения вакансий из пустого файла."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        vacancies = saver.get_vacancies()

        assert vacancies == []

    def test_get_vacancies_with_data(self, temp_json_file: Path, vacancy_object: Vacancy) -> None:
        """Тест получения вакансий из файла с данными."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        saver.add_vacancy(vacancy_object)
        vacancies = saver.get_vacancies()

        assert len(vacancies) == 1
        assert vacancies[0]["name"] == vacancy_object.name

    def test_get_vacancies_filter_by_keywords(self, temp_json_file: Path) -> None:
        """Тест фильтрации вакансий по ключевым словам."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        vacancy1 = Vacancy("Python Developer", "https://test1.ru", None, "Python Django Flask")
        vacancy2 = Vacancy("Java Developer", "https://test2.ru", None, "Java Spring")

        saver.add_vacancy(vacancy1)
        saver.add_vacancy(vacancy2)

        filtered = saver.get_vacancies(filter_words=["Python"])

        assert len(filtered) == 1
        assert filtered[0]["name"] == "Python Developer"

    def test_get_vacancies_filter_by_salary(self, temp_json_file: Path) -> None:
        """Тест фильтрации вакансий по диапазону зарплат."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        vacancy1 = Vacancy("High Salary", "https://test1.ru", {"from": 200000, "currency": "RUR"}, "Desc")
        vacancy2 = Vacancy("Low Salary", "https://test2.ru", {"from": 50000, "currency": "RUR"}, "Desc")

        saver.add_vacancy(vacancy1)
        saver.add_vacancy(vacancy2)

        filtered = saver.get_vacancies(salary_from=100000, salary_to=300000)

        assert len(filtered) == 1
        assert filtered[0]["name"] == "High Salary"

    def test_delete_vacancy(self, temp_json_file: Path, vacancy_object: Vacancy) -> None:
        """Тест удаления вакансии из файла."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        saver.add_vacancy(vacancy_object)
        saver.delete_vacancy(vacancy_object)

        vacancies = saver.get_vacancies()
        assert len(vacancies) == 0

    def test_delete_vacancy_not_found(self, temp_json_file: Path, vacancy_object: Vacancy) -> None:
        """Тест удаления несуществующей вакансии."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        with pytest.raises(ValueError, match="не найдена"):
            saver.delete_vacancy(vacancy_object)

    def test_load_vacancies_invalid_json(self, temp_json_file: Path) -> None:
        """Тест обработки поврежденного JSON файла."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        # Создаем файл с невалидным JSON
        with open(temp_json_file, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        vacancies = saver.get_vacancies()

        assert vacancies == []

    def test_load_vacancies_not_list(self, temp_json_file: Path) -> None:
        """Тест обработки файла, содержащего не список."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        # Создаем файл с JSON объектом (не список)
        with open(temp_json_file, "w", encoding="utf-8") as f:
            json.dump({"key": "value"}, f)

        vacancies = saver.get_vacancies()

        assert vacancies == []

    def test_save_vacancies_permission_error(self, temp_json_file: Path, vacancy_object: Vacancy) -> None:
        """Тест обработки ошибки прав доступа при сохранении."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        # Создаем файл и делаем его только для чтения (на Unix)
        import os

        temp_json_file.touch()
        try:
            os.chmod(temp_json_file, 0o444)  # Только чтение

            with pytest.raises(IOError):
                saver._save_vacancies([{"name": "Test", "url": "https://test.ru", "salary": None, "description": ""}])
        finally:
            os.chmod(temp_json_file, 0o644)  # Восстанавливаем права

    def test_load_vacancies_permission_error(self, temp_json_file: Path) -> None:
        """Тест обработки ошибки прав доступа при чтении."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        # Создаем файл и делаем его недоступным для чтения
        import os

        temp_json_file.touch()
        try:
            os.chmod(temp_json_file, 0o000)  # Нет прав

            vacancies = saver._load_vacancies()

            assert vacancies == []
        finally:
            os.chmod(temp_json_file, 0o644)  # Восстанавливаем права

    def test_add_vacancy_invalid_object(self, temp_json_file: Path) -> None:
        """Тест добавления невалидного объекта вакансии."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        invalid_vacancy = Mock()
        del invalid_vacancy.name  # Удаляем атрибут name

        with pytest.raises(ValueError):
            saver.add_vacancy(invalid_vacancy)

    def test_delete_vacancy_invalid_object(self, temp_json_file: Path) -> None:
        """Тест удаления невалидного объекта вакансии."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        invalid_vacancy = Mock()
        del invalid_vacancy.name  # Удаляем атрибут name

        with pytest.raises(ValueError):
            saver.delete_vacancy(invalid_vacancy)

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

    def test_get_vacancies_no_filter(self, temp_json_file: Path, vacancy_object: Vacancy) -> None:
        """Тест получения вакансий без фильтров."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        saver.add_vacancy(vacancy_object)
        vacancies = saver.get_vacancies()

        assert len(vacancies) == 1

    def test_get_vacancies_exception_handling(self, temp_json_file: Path) -> None:
        """Тест обработки исключений при загрузке вакансий."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        # Создаем файл с невалидным JSON
        with open(temp_json_file, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        vacancies = saver._load_vacancies()

        assert vacancies == []

    def test_load_vacancies_empty_content(self, temp_json_file: Path) -> None:
        """Тест обработки файла с пустым содержимым."""
        saver = JSONSaver(temp_json_file.name)
        saver._file_path = temp_json_file

        # Создаем пустой файл
        temp_json_file.touch()

        vacancies = saver._load_vacancies()

        assert vacancies == []

    def test_matches_salary_range_both_none(self) -> None:
        """Тест проверки диапазона зарплат когда обе границы None."""
        saver = JSONSaver()

        salary = {"from": None, "to": None, "currency": "RUR"}
        result = saver._matches_salary_range(salary, 100000, 200000)

        assert result is False
