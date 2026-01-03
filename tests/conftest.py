"""Общие фикстуры для тестов.

Модуль содержит фикстуры, используемые в различных тестах.
"""

# 1. Импорты стандартной библиотеки
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from src.vacancy.vacancy import Vacancy

# 4. Константы модуля
# (нет констант)


# 5. Фикстуры
@pytest.fixture
def sample_vacancy_data() -> Dict[str, Any]:
    """
    Фикстура с примером данных вакансии из API.

    Returns:
        Словарь с данными вакансии
    """
    return {
        "id": "123456",
        "name": "Python Developer",
        "alternate_url": "https://hh.ru/vacancy/123456",
        "url": "https://api.hh.ru/vacancies/123456",
        "salary": {"from": 100000, "to": 150000, "currency": "RUR", "gross": False},
        "snippet": {
            "requirement": "Опыт работы от 3 лет. Знание Python, Django.",
            "responsibility": "Разработка веб-приложений. Участие в проектах.",
        },
    }


@pytest.fixture
def sample_vacancy_data_no_salary() -> Dict[str, Any]:
    """
    Фикстура с примером данных вакансии без зарплаты.

    Returns:
        Словарь с данными вакансии без зарплаты
    """
    return {
        "id": "789012",
        "name": "Junior Developer",
        "alternate_url": "https://hh.ru/vacancy/789012",
        "url": "https://api.hh.ru/vacancies/789012",
        "salary": None,
        "snippet": {
            "requirement": "Базовые знания Python.",
            "responsibility": "Обучение и участие в проектах.",
        },
    }


@pytest.fixture
def sample_vacancies_list(
    sample_vacancy_data: Dict[str, Any], sample_vacancy_data_no_salary: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Фикстура со списком примеров данных вакансий.

    Args:
        sample_vacancy_data: Фикстура с данными вакансии
        sample_vacancy_data_no_salary: Фикстура с данными вакансии без зарплаты

    Returns:
        Список словарей с данными вакансий
    """
    return [sample_vacancy_data, sample_vacancy_data_no_salary]


@pytest.fixture
def vacancy_object(sample_vacancy_data: Dict[str, Any]) -> Vacancy:
    """
    Фикстура с объектом вакансии.

    Args:
        sample_vacancy_data: Фикстура с данными вакансии

    Returns:
        Объект Vacancy
    """
    snippet = sample_vacancy_data.get("snippet", {})
    description = f"{snippet.get('requirement', '')} {snippet.get('responsibility', '')}".strip()

    return Vacancy(
        name=sample_vacancy_data["name"],
        url=sample_vacancy_data["alternate_url"],
        salary=sample_vacancy_data["salary"],
        description=description,
    )


@pytest.fixture
def temp_json_file() -> Path:
    """
    Фикстура с временным JSON файлом.

    Returns:
        Путь к временному файлу
    """
    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / "test_vacancies.json"

    # Очищаем файл перед тестом
    if temp_file.exists():
        temp_file.unlink()

    yield temp_file

    # Очищаем файл после теста
    if temp_file.exists():
        temp_file.unlink()


@pytest.fixture
def mock_api_response(sample_vacancies_list: List[Dict[str, Any]]) -> Mock:
    """
    Фикстура с моком ответа API.

    Args:
        sample_vacancies_list: Фикстура со списком вакансий

    Returns:
        Мок объекта Response
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": sample_vacancies_list,
        "found": 2,
        "pages": 1,
        "page": 0,
        "per_page": 100,
    }
    mock_response.raise_for_status = Mock()
    return mock_response
