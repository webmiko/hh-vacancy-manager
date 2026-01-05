"""Тесты для пользовательского интерфейса.

Модуль содержит тесты для функции user_interaction().
"""

# 1. Импорты стандартной библиотеки
from unittest.mock import Mock, patch

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from src.user_interface import _print_vacancies, _print_vacancy, user_interaction
from src.vacancy.vacancy import Vacancy

# 4. Константы модуля
# (нет констант)


class TestUserInterface:
    """Тесты для пользовательского интерфейса."""

    def test_print_vacancy(self, vacancy_object: Vacancy, capsys: pytest.CaptureFixture) -> None:
        """Тест вывода информации о вакансии."""
        _print_vacancy(vacancy_object, 0)

        captured = capsys.readouterr()
        assert "Вакансия #1" in captured.out
        assert vacancy_object.name in captured.out
        assert vacancy_object.url in captured.out

    def test_print_vacancies_empty(self, capsys: pytest.CaptureFixture) -> None:
        """Тест вывода пустого списка вакансий."""
        _print_vacancies([])

        captured = capsys.readouterr()
        assert "Вакансии не найдены" in captured.out

    def test_print_vacancies_with_data(self, vacancy_object: Vacancy, capsys: pytest.CaptureFixture) -> None:
        """Тест вывода списка вакансий."""
        vacancies = [vacancy_object]
        _print_vacancies(vacancies)

        captured = capsys.readouterr()
        assert "Найдено вакансий: 1" in captured.out
        assert vacancy_object.name in captured.out

    @patch("src.user_interface.HeadHunterAPI")
    @patch("src.user_interface.Vacancy")
    @patch("src.user_interface.JSONSaver")
    @patch("builtins.input")
    def test_user_interaction_success(
        self,
        mock_input: Mock,
        mock_saver: Mock,
        mock_vacancy: Mock,
        mock_api: Mock,
        sample_vacancies_list: list,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Тест успешного взаимодействия с пользователем."""
        # Настройка моков
        mock_api_instance = Mock()
        mock_api_instance.get_vacancies.return_value = sample_vacancies_list
        mock_api.return_value = mock_api_instance

        mock_vacancy.cast_to_object_list.return_value = [Vacancy("Test", "https://test.ru", None, "Python Django")]

        mock_saver_instance = Mock()
        mock_saver.return_value = mock_saver_instance

        # Симуляция ввода пользователя
        mock_input.side_effect = ["Python", "5", "Django"]

        user_interaction()

        captured = capsys.readouterr()
        assert "HH Vacancy Manager" in captured.out
        mock_api_instance.get_vacancies.assert_called_once_with("Python")

    @patch("src.user_interface.HeadHunterAPI")
    @patch("builtins.input")
    def test_user_interaction_empty_query(
        self, mock_input: Mock, mock_api: Mock, capsys: pytest.CaptureFixture
    ) -> None:
        """Тест взаимодействия с пустым запросом."""
        mock_input.return_value = ""

        user_interaction()

        captured = capsys.readouterr()
        assert "Ошибка" in captured.out or "не может быть пустым" in captured.out

    @patch("src.user_interface.HeadHunterAPI")
    @patch("builtins.input")
    def test_user_interaction_api_error(self, mock_input: Mock, mock_api: Mock, capsys: pytest.CaptureFixture) -> None:
        """Тест обработки ошибки API."""
        import requests

        mock_api_instance = Mock()
        mock_api_instance.get_vacancies.side_effect = requests.RequestException("API Error")
        mock_api.return_value = mock_api_instance

        mock_input.return_value = "Python"

        user_interaction()

        captured = capsys.readouterr()
        assert "Ошибка" in captured.out

    @patch("src.user_interface.HeadHunterAPI")
    @patch("src.user_interface.Vacancy")
    @patch("src.user_interface.JSONSaver")
    @patch("builtins.input")
    def test_user_interaction_no_vacancies(
        self,
        mock_input: Mock,
        mock_saver: Mock,
        mock_vacancy: Mock,
        mock_api: Mock,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Тест взаимодействия когда вакансии не найдены."""
        mock_api_instance = Mock()
        mock_api_instance.get_vacancies.return_value = []
        mock_api.return_value = mock_api_instance

        mock_input.return_value = "Python"

        user_interaction()

        captured = capsys.readouterr()
        assert "не найдены" in captured.out

    @patch("src.user_interface.HeadHunterAPI")
    @patch("src.user_interface.Vacancy")
    @patch("src.user_interface.JSONSaver")
    @patch("builtins.input")
    def test_user_interaction_invalid_top_n(
        self,
        mock_input: Mock,
        mock_saver: Mock,
        mock_vacancy: Mock,
        mock_api: Mock,
        sample_vacancies_list: list,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Тест взаимодействия с некорректным значением топ N."""
        mock_api_instance = Mock()
        mock_api_instance.get_vacancies.return_value = sample_vacancies_list
        mock_api.return_value = mock_api_instance

        mock_vacancy.cast_to_object_list.return_value = [Vacancy("Test", "https://test.ru", None, "Desc")]

        mock_saver_instance = Mock()
        mock_saver.return_value = mock_saver_instance

        # Некорректное значение для топ N
        mock_input.side_effect = ["Python", "abc"]

        user_interaction()

        captured = capsys.readouterr()
        assert "Ошибка" in captured.out or "корректное число" in captured.out

    @patch("src.user_interface.HeadHunterAPI")
    @patch("src.user_interface.Vacancy")
    @patch("src.user_interface.JSONSaver")
    @patch("builtins.input")
    def test_user_interaction_no_vacancies_created(
        self,
        mock_input: Mock,
        mock_saver: Mock,
        mock_vacancy: Mock,
        mock_api: Mock,
        sample_vacancies_list: list,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Тест взаимодействия когда не удалось создать объекты вакансий."""
        mock_api_instance = Mock()
        mock_api_instance.get_vacancies.return_value = sample_vacancies_list
        mock_api.return_value = mock_api_instance

        mock_vacancy.cast_to_object_list.return_value = []

        mock_input.return_value = "Python"

        user_interaction()

        captured = capsys.readouterr()
        assert "Не удалось создать" in captured.out or "не найдены" in captured.out

    @patch("src.user_interface.HeadHunterAPI")
    @patch("src.user_interface.Vacancy")
    @patch("src.user_interface.JSONSaver")
    @patch("builtins.input")
    def test_user_interaction_save_error(
        self,
        mock_input: Mock,
        mock_saver: Mock,
        mock_vacancy: Mock,
        mock_api: Mock,
        sample_vacancies_list: list,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Тест обработки ошибки при сохранении вакансии."""
        mock_api_instance = Mock()
        mock_api_instance.get_vacancies.return_value = sample_vacancies_list
        mock_api.return_value = mock_api_instance

        mock_vacancy.cast_to_object_list.return_value = [
            Vacancy("Test", "https://test.ru", None, "Desc")
        ]

        mock_saver_instance = Mock()
        mock_saver_instance.add_vacancy.side_effect = IOError("Save error")
        mock_saver.return_value = mock_saver_instance

        mock_input.side_effect = ["Python", "5", ""]

        user_interaction()

        # Должно продолжить работу несмотря на ошибку сохранения
        captured = capsys.readouterr()
        assert "Сохранено" in captured.out or "Топ" in captured.out

    @patch("src.user_interface.HeadHunterAPI")
    @patch("src.user_interface.Vacancy")
    @patch("src.user_interface.JSONSaver")
    @patch("builtins.input")
    def test_user_interaction_save_value_error(
        self,
        mock_input: Mock,
        mock_saver: Mock,
        mock_vacancy: Mock,
        mock_api: Mock,
        sample_vacancies_list: list,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Тест обработки ValueError при сохранении (критично для пользователя)."""
        mock_api_instance = Mock()
        mock_api_instance.get_vacancies.return_value = sample_vacancies_list
        mock_api.return_value = mock_api_instance

        mock_vacancy.cast_to_object_list.return_value = [
            Vacancy("Test", "https://test.ru", None, "Desc")
        ]

        mock_saver_instance = Mock()
        mock_saver_instance.add_vacancy.side_effect = ValueError("Invalid vacancy data")
        mock_saver.return_value = mock_saver_instance

        mock_input.side_effect = ["Python", "5", ""]

        user_interaction()

        # Должно продолжить работу несмотря на ошибку сохранения
        captured = capsys.readouterr()
        assert "Сохранено" in captured.out or "Топ" in captured.out

    @patch("src.user_interface.HeadHunterAPI")
    @patch("src.user_interface.Vacancy")
    @patch("src.user_interface.JSONSaver")
    @patch("builtins.input")
    def test_user_interaction_save_attribute_error(
        self,
        mock_input: Mock,
        mock_saver: Mock,
        mock_vacancy: Mock,
        mock_api: Mock,
        sample_vacancies_list: list,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Тест обработки AttributeError при сохранении (критично для пользователя)."""
        mock_api_instance = Mock()
        mock_api_instance.get_vacancies.return_value = sample_vacancies_list
        mock_api.return_value = mock_api_instance

        mock_vacancy.cast_to_object_list.return_value = [
            Vacancy("Test", "https://test.ru", None, "Desc")
        ]

        mock_saver_instance = Mock()
        mock_saver_instance.add_vacancy.side_effect = AttributeError("Missing attribute")
        mock_saver.return_value = mock_saver_instance

        mock_input.side_effect = ["Python", "5", ""]

        user_interaction()

        # Должно продолжить работу несмотря на ошибку сохранения
        captured = capsys.readouterr()
        assert "Сохранено" in captured.out or "Топ" in captured.out
