"""Класс для работы с вакансиями.

Модуль содержит класс Vacancy для представления вакансии
с поддержкой сравнения по зарплате и валидации данных.
"""

# 1. Импорты стандартной библиотеки
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# 2. Импорты сторонних библиотек
# (нет сторонних библиотек)

# 3. Импорты из проекта
# (нет локальных импортов)

# 4. Константы модуля
SALARY_NOT_SPECIFIED = "Зарплата не указана"
DEFAULT_SALARY_VALUE = 0
EMPTY_STRING = ""


# 5. Приватные функции
def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля.

    Returns:
        Настроенный логгер для модуля
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "vacancy.log"
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# 6. Создаем логгер для модуля
logger = _setup_logger()


# 7. Публичные классы
class Vacancy:
    """Класс для представления вакансии.

    Класс содержит информацию о вакансии и поддерживает сравнение
    вакансий по зарплате через магические методы.

    Attributes:
        name: Название вакансии
        url: Ссылка на вакансию
        salary: Зарплата (словарь с ключами 'from', 'to', 'currency', 'gross' или None)
        description: Описание и требования к вакансии
    """

    __slots__ = ("_name", "_url", "_salary", "_description")

    def __init__(
        self,
        name: str,
        url: str,
        salary: Optional[Dict[str, Any]],
        description: str,
    ) -> None:
        """
        Инициализирует экземпляр класса Vacancy.

        Args:
            name: Название вакансии
            url: Ссылка на вакансию
            salary: Зарплата (словарь или None)
            description: Описание и требования к вакансии

        Example:
            >>> vacancy = Vacancy(
            ...     "Python Developer",
            ...     "https://hh.ru/vacancy/123456",
            ...     {"from": 100000, "to": 150000, "currency": "RUR"},
            ...     "Требования: опыт работы от 3 лет..."
            ... )
        """
        self._name = self._validate_name(name)
        self._url = self._validate_url(url)
        self._salary = self._validate_salary(salary)
        self._description = self._validate_description(description)

    @property
    def name(self) -> str:
        """Возвращает название вакансии."""
        return self._name

    @property
    def url(self) -> str:
        """Возвращает ссылку на вакансию."""
        return self._url

    @property
    def salary(self) -> Optional[Dict[str, Any]]:
        """Возвращает информацию о зарплате."""
        return self._salary

    @property
    def description(self) -> str:
        """Возвращает описание вакансии."""
        return self._description

    def _validate_name(self, name: Any) -> str:
        """
        Валидирует название вакансии.

        Args:
            name: Название вакансии

        Returns:
            Валидное название вакансии

        Raises:
            ValueError: Если название пустое или не является строкой
        """
        if not isinstance(name, str):
            logger.error(f"Название вакансии должно быть строкой. Получен тип: {type(name)}")
            raise ValueError(f"Название вакансии должно быть строкой, получен тип: {type(name)}")

        name_stripped = name.strip()
        if not name_stripped:
            logger.error("Название вакансии не может быть пустым")
            raise ValueError("Название вакансии не может быть пустым")

        return str(name_stripped)

    def _validate_url(self, url: Any) -> str:
        """
        Валидирует ссылку на вакансию.

        Args:
            url: Ссылка на вакансию

        Returns:
            Валидная ссылка на вакансию

        Raises:
            ValueError: Если ссылка пустая или не является строкой
        """
        if not isinstance(url, str):
            logger.error(f"Ссылка на вакансию должна быть строкой. Получен тип: {type(url)}")
            raise ValueError(f"Ссылка на вакансию должна быть строкой, получен тип: {type(url)}")

        url_stripped = url.strip()
        if not url_stripped:
            logger.error("Ссылка на вакансию не может быть пустой")
            raise ValueError("Ссылка на вакансию не может быть пустой")

        return str(url_stripped)

    def _validate_salary(self, salary: Any) -> Optional[Dict[str, Any]]:
        """
        Валидирует информацию о зарплате.

        Args:
            salary: Зарплата (словарь или None)

        Returns:
            Валидная информация о зарплате или None
        """
        if salary is None:
            return None

        if not isinstance(salary, dict):
            logger.warning(f"Зарплата должна быть словарем или None. Получен тип: {type(salary)}")
            return None

        return salary

    def _validate_description(self, description: Any) -> str:
        """
        Валидирует описание вакансии.

        Args:
            description: Описание вакансии

        Returns:
            Валидное описание вакансии
        """
        if not isinstance(description, str):
            logger.warning(f"Описание должно быть строкой. Получен тип: {type(description)}")
            return EMPTY_STRING

        return description.strip()

    def _get_salary_value(self) -> float:
        """
        Получает числовое значение зарплаты для сравнения.

        Returns:
            Числовое значение зарплаты (0 если не указана)
        """
        if self._salary is None:
            return float(DEFAULT_SALARY_VALUE)

        salary_from = self._salary.get("from")
        salary_to = self._salary.get("to")

        if salary_from is not None and salary_to is not None:
            return (float(salary_from) + float(salary_to)) / 2.0

        if salary_from is not None:
            return float(salary_from)

        if salary_to is not None:
            return float(salary_to)

        return float(DEFAULT_SALARY_VALUE)

    def __lt__(self, other: "Vacancy") -> bool:
        """
        Сравнивает вакансии по зарплате (меньше).

        Args:
            other: Другая вакансия для сравнения

        Returns:
            True если зарплата текущей вакансии меньше зарплаты другой
        """
        if not isinstance(other, Vacancy):
            return NotImplemented

        return self._get_salary_value() < other._get_salary_value()

    def __le__(self, other: "Vacancy") -> bool:
        """
        Сравнивает вакансии по зарплате (меньше или равно).

        Args:
            other: Другая вакансия для сравнения

        Returns:
            True если зарплата текущей вакансии меньше или равна зарплате другой
        """
        if not isinstance(other, Vacancy):
            return NotImplemented

        return self._get_salary_value() <= other._get_salary_value()

    def __gt__(self, other: "Vacancy") -> bool:
        """
        Сравнивает вакансии по зарплате (больше).

        Args:
            other: Другая вакансия для сравнения

        Returns:
            True если зарплата текущей вакансии больше зарплаты другой
        """
        if not isinstance(other, Vacancy):
            return NotImplemented

        return self._get_salary_value() > other._get_salary_value()

    def __ge__(self, other: "Vacancy") -> bool:
        """
        Сравнивает вакансии по зарплате (больше или равно).

        Args:
            other: Другая вакансия для сравнения

        Returns:
            True если зарплата текущей вакансии больше или равна зарплате другой
        """
        if not isinstance(other, Vacancy):
            return NotImplemented

        return self._get_salary_value() >= other._get_salary_value()

    def __eq__(self, other: object) -> bool:
        """
        Сравнивает вакансии по зарплате (равно).

        Args:
            other: Другая вакансия для сравнения

        Returns:
            True если зарплаты вакансий равны
        """
        if not isinstance(other, Vacancy):
            return NotImplemented

        return self._get_salary_value() == other._get_salary_value()

    def __str__(self) -> str:
        """
        Возвращает строковое представление вакансии.

        Returns:
            Строковое представление вакансии
        """
        salary_str = SALARY_NOT_SPECIFIED
        if self._salary:
            salary_from = self._salary.get("from")
            salary_to = self._salary.get("to")
            currency = self._salary.get("currency", "RUR")

            if salary_from is not None and salary_to is not None:
                salary_str = f"{salary_from} - {salary_to} {currency}"
            elif salary_from is not None:
                salary_str = f"от {salary_from} {currency}"
            elif salary_to is not None:
                salary_str = f"до {salary_to} {currency}"

        return f"Вакансия: {self._name}\nСсылка: {self._url}\nЗарплата: {salary_str}\nОписание: {self._description}"

    def __repr__(self) -> str:
        """
        Возвращает представление вакансии для отладки.

        Returns:
            Представление вакансии для отладки
        """
        desc_preview = self._description[:50] + "..." if len(self._description) > 50 else self._description
        return f"Vacancy(name='{self._name}', url='{self._url}', salary={self._salary}, description='{desc_preview}')"

    @classmethod
    def cast_to_object_list(cls, vacancies_data: List[Dict[str, Any]]) -> List["Vacancy"]:
        """
        Преобразует список словарей из API в список объектов Vacancy.

        Args:
            vacancies_data: Список словарей с данными о вакансиях из API

        Returns:
            Список объектов Vacancy. Пропускает некорректные вакансии.

        Example:
            >>> data = [{"name": "Python", "alternate_url": "https://...", ...}]
            >>> vacancies = Vacancy.cast_to_object_list(data)
            >>> print(len(vacancies))
            1
        """
        logger.info(f"Начало преобразования {len(vacancies_data)} вакансий в объекты")

        vacancies: List["Vacancy"] = []

        for item in vacancies_data:
            try:
                name = item.get("name", "")
                url = item.get("alternate_url") or item.get("url", "")
                salary = item.get("salary")
                snippet = item.get("snippet", {})

                requirement = snippet.get("requirement", "")
                responsibility = snippet.get("responsibility", "")
                description = f"{requirement} {responsibility}".strip()

                vacancy = cls(name=name, url=url, salary=salary, description=description)
                vacancies.append(vacancy)

            # Некритичные ошибки валидации данных - можно объединить
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Пропущена некорректная вакансия: {type(e).__name__} - {e}")
                continue
            # Некритичные ошибки доступа к атрибутам - можно объединить
            except (AttributeError, IndexError) as e:
                logger.warning(f"Ошибка доступа к атрибутам при создании вакансии: {type(e).__name__} - {e}")
                continue
            except Exception as e:
                # Исключительный случай: обработка любых других неожиданных ошибок
                # для предотвращения прерывания обработки всего списка вакансий
                logger.error(f"Неожиданная ошибка при создании вакансии: {type(e).__name__} - {e}")
                continue

        logger.info(f"Успешно создано {len(vacancies)} вакансий из {len(vacancies_data)}")
        return vacancies
