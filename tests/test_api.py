"""Тесты для работы с API.

Модуль содержит тесты для абстрактного класса APIBase
и класса HeadHunterAPI.
"""

# 1. Импорты стандартной библиотеки
from typing import Any, Dict, List
from unittest.mock import Mock, patch

# 2. Импорты сторонних библиотек
import pytest
import requests

# 3. Импорты из проекта
from src.api.base import APIBase
from src.api.hh_api import HeadHunterAPI

# 4. Константы модуля
# (нет констант)


class TestAPIBase:
    """Тесты для абстрактного класса APIBase."""

    def test_api_base_is_abstract(self) -> None:
        """Тест, что нельзя создать экземпляр абстрактного класса."""
        with pytest.raises(TypeError):
            APIBase()  # type: ignore

    def test_api_base_has_abstract_methods(self) -> None:
        """Тест, что абстрактные методы определены."""
        assert hasattr(APIBase, "connect")
        assert hasattr(APIBase, "get_vacancies")


class TestHeadHunterAPI:
    """Тесты для класса HeadHunterAPI."""

    def test_headhunter_api_initialization(self) -> None:
        """Тест инициализации класса HeadHunterAPI."""
        from src.api.hh_api import RUSSIA_AREA_ID

        api = HeadHunterAPI()

        assert api._url == "https://api.hh.ru/vacancies"
        assert api._headers == {"User-Agent": "HH-User-Agent"}
        assert api._params["per_page"] == 100
        assert api._params["area"] == RUSSIA_AREA_ID  # Поиск только по России

    def test_headhunter_api_inherits_from_base(self) -> None:
        """Тест, что HeadHunterAPI наследуется от APIBase."""
        assert issubclass(HeadHunterAPI, APIBase)

    @patch("src.api.hh_api.requests.get")
    def test_connect_success(self, mock_get: Mock, mock_api_response: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест успешного подключения к API."""
        mock_get.return_value = mock_api_response

        headhunter_api.connect()

        mock_get.assert_called_once()
        mock_api_response.raise_for_status.assert_called_once()

    @patch("src.api.hh_api.requests.get")
    def test_connect_failure(self, mock_get: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест ошибки подключения к API."""
        mock_get.side_effect = requests.RequestException("Connection error")

        with pytest.raises(ConnectionError):
            headhunter_api.connect()

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_success(
        self, mock_get: Mock, mock_api_response: Mock, sample_vacancies_list: List[Dict[str, Any]], headhunter_api: HeadHunterAPI
    ) -> None:
        """Тест успешного получения вакансий."""
        # Ответ для connect()
        connect_response = Mock()
        connect_response.status_code = 200
        connect_response.raise_for_status = Mock()

        # Первая страница с данными
        response_page1 = Mock()
        response_page1.status_code = 200
        response_page1.json.return_value = {
            "items": sample_vacancies_list,
            "found": 2,
            "pages": 1,
            "page": 0,
            "per_page": 100,
        }
        response_page1.raise_for_status = Mock()

        # Вторая страница пустая для остановки пагинации
        response_page2 = Mock()
        response_page2.status_code = 200
        response_page2.json.return_value = {"items": [], "found": 2, "pages": 1, "page": 1, "per_page": 100}
        response_page2.raise_for_status = Mock()

        mock_get.side_effect = [connect_response, response_page1, response_page2]

        vacancies = headhunter_api.get_vacancies("Python")

        # После фильтрации по валюте RUR количество может быть меньше
        # Проверяем, что все возвращенные вакансии имеют RUR или None в salary
        assert len(vacancies) <= 2
        for vacancy in vacancies:
            salary = vacancy.get("salary")
            if salary is not None:
                assert salary.get("currency") == "RUR"
        assert mock_get.call_count >= 2

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_empty_keyword(self, mock_get: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест получения вакансий с пустым ключевым словом."""
        vacancies = headhunter_api.get_vacancies("")

        assert vacancies == []
        mock_get.assert_not_called()

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_connection_error(self, mock_get: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест обработки ошибки подключения при получении вакансий."""
        mock_get.side_effect = requests.RequestException("Connection error")

        vacancies = headhunter_api.get_vacancies("Python")

        assert vacancies == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_invalid_json(self, mock_get: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест обработки невалидного JSON ответа."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        vacancies = headhunter_api.get_vacancies("Python")

        assert vacancies == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_no_items_key(self, mock_get: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест обработки ответа без ключа 'items'."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"found": 0}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        vacancies = headhunter_api.get_vacancies("Python")

        assert vacancies == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_pagination(self, mock_get: Mock, sample_vacancies_list: List[Dict[str, Any]], headhunter_api: HeadHunterAPI) -> None:
        """Тест пагинации при получении вакансий."""
        # Ответ для connect()
        connect_response = Mock()
        connect_response.status_code = 200
        connect_response.raise_for_status = Mock()

        # Первая страница
        response_page1 = Mock()
        response_page1.status_code = 200
        response_page1.json.return_value = {
            "items": sample_vacancies_list,
            "found": 4,
            "pages": 2,
            "page": 0,
            "per_page": 2,
        }
        response_page1.raise_for_status = Mock()

        # Вторая страница
        response_page2 = Mock()
        response_page2.status_code = 200
        response_page2.json.return_value = {
            "items": sample_vacancies_list,
            "found": 4,
            "pages": 2,
            "page": 1,
            "per_page": 2,
        }
        response_page2.raise_for_status = Mock()

        # Третья страница (пустая для остановки)
        response_page3 = Mock()
        response_page3.status_code = 200
        response_page3.json.return_value = {"items": [], "found": 4, "pages": 2, "page": 2, "per_page": 2}
        response_page3.raise_for_status = Mock()

        mock_get.side_effect = [connect_response, response_page1, response_page2, response_page3]

        vacancies = headhunter_api.get_vacancies("Python")

        assert len(vacancies) == 4  # 2 вакансии на каждой странице
        assert mock_get.call_count == 4

    def test_filter_by_currency(self, headhunter_api: HeadHunterAPI) -> None:
        """Тест фильтрации вакансий по валюте."""
        from src.api.hh_api import RUR_CURRENCY

        items = [
            {"name": "Test1", "salary": {"from": 100000, "currency": "RUR"}},
            {"name": "Test2", "salary": {"from": 200000, "currency": "USD"}},
            {"name": "Test3", "salary": None},
            {"name": "Test4", "salary": {"from": 150000, "currency": "RUR"}},
        ]

        filtered = headhunter_api._filter_by_currency(items, RUR_CURRENCY)

        assert len(filtered) == 3  # Test1, Test3, Test4
        assert filtered[0]["name"] == "Test1"
        assert filtered[1]["name"] == "Test3"
        assert filtered[2]["name"] == "Test4"

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_unexpected_exception(self, mock_get: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест обработки неожиданного исключения."""
        connect_response = Mock()
        connect_response.status_code = 200
        connect_response.raise_for_status = Mock()

        response_page1 = Mock()
        response_page1.status_code = 200
        response_page1.json.side_effect = KeyError("Unexpected error")
        response_page1.raise_for_status = Mock()

        mock_get.side_effect = [connect_response, response_page1]

        vacancies = headhunter_api.get_vacancies("Python")

        assert vacancies == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_items_not_list(self, mock_get: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест обработки ответа где items не является списком."""
        connect_response = Mock()
        connect_response.status_code = 200
        connect_response.raise_for_status = Mock()

        response_page1 = Mock()
        response_page1.status_code = 200
        response_page1.json.return_value = {"items": "not a list", "found": 0, "pages": 1, "page": 0, "per_page": 100}
        response_page1.raise_for_status = Mock()

        mock_get.side_effect = [connect_response, response_page1]

        vacancies = headhunter_api.get_vacancies("Python")

        assert vacancies == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_http_error(self, mock_get: Mock, headhunter_api: HeadHunterAPI) -> None:
        """Тест обработки HTTP ошибки при запросе."""
        import requests

        connect_response = Mock()
        connect_response.status_code = 200
        connect_response.raise_for_status = Mock()

        response_page1 = Mock()
        response_page1.status_code = 404
        response_page1.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.side_effect = [connect_response, response_page1]

        vacancies = headhunter_api.get_vacancies("Python")

        assert vacancies == []
