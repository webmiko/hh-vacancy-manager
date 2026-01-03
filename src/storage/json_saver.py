"""Класс для работы с JSON-файлами для сохранения вакансий.

Модуль содержит класс JSONSaver для сохранения, загрузки и удаления
вакансий в формате JSON с предотвращением дублирования.
"""

# 1. Импорты стандартной библиотеки
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# 3. Импорты из проекта
from src.storage.base import DEFAULT_RETURN_VALUE, FileSaverBase

# 2. Импорты сторонних библиотек
# (нет сторонних библиотек)


# 4. Константы модуля
ENCODING = "utf-8"
FILE_READ_MODE = "r"
FILE_WRITE_MODE = "w"
DEFAULT_FILENAME = "vacancies.json"
DATA_DIR = "data"


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

    log_file = logs_dir / "json_saver.log"
    file_handler = logging.FileHandler(log_file, mode=FILE_WRITE_MODE, encoding=ENCODING)
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
class JSONSaver(FileSaverBase):
    """Класс для работы с JSON-файлами для сохранения вакансий.

    Реализует методы для добавления, получения и удаления вакансий
    в формате JSON с предотвращением дублирования.

    Attributes:
        _filename: Имя файла для сохранения данных (приватный атрибут)
    """

    def __init__(self, filename: str = DEFAULT_FILENAME) -> None:
        """
        Инициализирует экземпляр класса JSONSaver.

        Args:
            filename: Имя файла для сохранения данных. По умолчанию "vacancies.json"

        Example:
            >>> saver = JSONSaver()
            >>> saver = JSONSaver("my_vacancies.json")
        """
        self._filename: str = filename
        self._file_path = Path(__file__).parent.parent.parent / DATA_DIR / self._filename
        self._file_path.parent.mkdir(exist_ok=True)

    def _load_vacancies(self) -> List[Dict[str, Any]]:
        """
        Загружает вакансии из JSON-файла.

        Returns:
            Список словарей с данными о вакансиях.
            Возвращает пустой список при ошибке или если файл не существует.
        """
        if not self._file_path.exists():
            logger.debug(f"Файл не существует, возвращаем пустой список: {self._filename}")
            return []

        try:
            with open(self._file_path, FILE_READ_MODE, encoding=ENCODING) as file:
                content = file.read().strip()

                if not content:
                    logger.warning(f"Файл пустой: {self._filename}")
                    return []

                data = json.loads(content)

                if not isinstance(data, list):
                    logger.warning(f"Файл содержит не список. Тип: {type(data)}")
                    return []

                logger.debug(f"Загружено {len(data)} вакансий из файла: {self._filename}")
                return data

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON в файле {self._filename}: {type(e).__name__} - {e}")
            return []
        except PermissionError as e:
            # Критично: проблемы с правами доступа требуют внимания админа
            logger.critical(f"КРИТИЧНО: Отсутствуют права доступа к файлу {self._filename}: {e}")
            return []
        except MemoryError as e:
            # Критично: нехватка памяти требует внимания админа
            logger.critical(f"КРИТИЧНО: Нехватка памяти при загрузке файла {self._filename}: {e}")
            return []
        except OSError as e:
            logger.error(f"Ошибка ввода-вывода при чтении файла {self._filename}: {type(e).__name__} - {e}")
            return []
        except UnicodeDecodeError as e:
            logger.error(f"Ошибка декодирования файла {self._filename}: {type(e).__name__} - {e}")
            return []
        except Exception as e:
            # Исключительный случай: обработка любых других неожиданных ошибок
            # для предотвращения падения программы при работе с файлами
            logger.critical(
                f"Критическая неожиданная ошибка при загрузке файла {self._filename}: {type(e).__name__} - {e}"
            )
            return []

    def _save_vacancies(self, vacancies: List[Dict[str, Any]]) -> None:
        """
        Сохраняет вакансии в JSON-файл.

        Args:
            vacancies: Список словарей с данными о вакансиях
        """
        try:
            with open(self._file_path, FILE_WRITE_MODE, encoding=ENCODING) as file:
                json.dump(vacancies, file, ensure_ascii=False, indent=2)

            logger.debug(f"Сохранено {len(vacancies)} вакансий в файл: {self._filename}")

        except PermissionError as e:
            # Критично: проблемы с правами доступа требуют внимания админа
            logger.critical(f"КРИТИЧНО: Отсутствуют права доступа для записи в файл {self._filename}: {e}")
            raise IOError(f"Не удалось сохранить данные в файл {self._filename}: {e}") from e
        except MemoryError as e:
            # Критично: нехватка памяти требует внимания админа
            logger.critical(f"КРИТИЧНО: Нехватка памяти при сохранении файла {self._filename}: {e}")
            raise IOError(f"Не удалось сохранить данные в файл {self._filename}: {e}") from e
        except OSError as e:
            logger.error(f"Ошибка ввода-вывода при записи в файл {self._filename}: {type(e).__name__} - {e}")
            raise IOError(f"Не удалось сохранить данные в файл {self._filename}: {e}") from e
        except TypeError as e:
            logger.error(f"Ошибка типа данных при сохранении файла {self._filename}: {type(e).__name__} - {e}")
            raise IOError(f"Не удалось сохранить данные в файл {self._filename}: {e}") from e
        except Exception as e:
            # Исключительный случай: обработка любых других неожиданных ошибок
            # для предотвращения потери данных при критических ошибках
            logger.critical(
                f"Критическая неожиданная ошибка при сохранении файла {self._filename}: {type(e).__name__} - {e}"
            )
            raise IOError(f"Не удалось сохранить данные в файл {self._filename}: {e}") from e

    def _vacancy_to_dict(self, vacancy: Any) -> Dict[str, Any]:
        """
        Преобразует объект вакансии в словарь.

        Args:
            vacancy: Объект вакансии

        Returns:
            Словарь с данными о вакансии
        """
        return {
            "name": vacancy.name,
            "url": vacancy.url,
            "salary": vacancy.salary,
            "description": vacancy.description,
        }

    def _is_duplicate(self, vacancy_dict: Dict[str, Any], existing_vacancies: List[Dict[str, Any]]) -> bool:
        """
        Проверяет, является ли вакансия дубликатом.

        Args:
            vacancy_dict: Словарь с данными о вакансии
            existing_vacancies: Список существующих вакансий

        Returns:
            True если вакансия уже существует (по URL)
        """
        vacancy_url = vacancy_dict.get("url", "")

        for existing in existing_vacancies:
            if existing.get("url") == vacancy_url:
                return True

        return False

    def add_vacancy(self, vacancy: Any) -> None:
        """
        Добавляет вакансию в JSON-файл.

        Если вакансия уже существует (по URL), она не будет добавлена повторно.

        Args:
            vacancy: Объект вакансии для добавления

        Raises:
            IOError: При ошибках записи в файл
            ValueError: При неверных данных вакансии

        Example:
            >>> from src.vacancy.vacancy import Vacancy
            >>> saver = JSONSaver()
            >>> vacancy = Vacancy("Python", "https://hh.ru/vacancy/123", None, "Desc")
            >>> saver.add_vacancy(vacancy)
        """
        logger.info(f"Добавление вакансии в файл: {self._filename}")

        try:
            vacancy_dict = self._vacancy_to_dict(vacancy)
        except AttributeError as e:
            logger.error(f"Ошибка при преобразовании вакансии в словарь: {type(e).__name__} - {e}")
            raise ValueError(f"Неверный объект вакансии: {e}") from e

        existing_vacancies = self._load_vacancies()

        if self._is_duplicate(vacancy_dict, existing_vacancies):
            logger.warning(f"Вакансия уже существует (URL: {vacancy_dict.get('url')}), пропускаем")
            return

        existing_vacancies.append(vacancy_dict)
        self._save_vacancies(existing_vacancies)

        logger.info(f"Вакансия успешно добавлена в файл: {self._filename}")

    def get_vacancies(self, **criteria: Any) -> List[Dict[str, Any]]:
        """
        Получает вакансии из файла по критериям.

        Args:
            **criteria: Критерии фильтрации:
                - filter_words: список ключевых слов для поиска в описании
                - salary_from: минимальная зарплата
                - salary_to: максимальная зарплата

        Returns:
            Список словарей с данными о вакансиях.
            Возвращает пустой список при ошибке или если вакансии не найдены.

        Example:
            >>> saver = JSONSaver()
            >>> vacancies = saver.get_vacancies(filter_words=["Python", "Django"])
            >>> print(len(vacancies))
            10
        """
        logger.info(f"Получение вакансий из файла: {self._filename}")

        all_vacancies = self._load_vacancies()

        if not all_vacancies:
            logger.debug("Вакансии не найдены в файле")
            return DEFAULT_RETURN_VALUE

        filtered_vacancies = all_vacancies

        # Фильтрация по ключевым словам
        filter_words = criteria.get("filter_words", [])
        if filter_words:
            filtered_vacancies = [
                v
                for v in filtered_vacancies
                if any(word.lower() in v.get("description", "").lower() for word in filter_words)
            ]
            logger.debug(f"После фильтрации по ключевым словам: {len(filtered_vacancies)} вакансий")

        # Фильтрация по диапазону зарплат
        salary_from = criteria.get("salary_from")
        salary_to = criteria.get("salary_to")

        if salary_from is not None or salary_to is not None:
            filtered_vacancies = [
                v for v in filtered_vacancies if self._matches_salary_range(v.get("salary"), salary_from, salary_to)
            ]
            logger.debug(f"После фильтрации по зарплате: {len(filtered_vacancies)} вакансий")

        logger.info(f"Найдено {len(filtered_vacancies)} вакансий по критериям")
        return filtered_vacancies

    def _matches_salary_range(
        self, salary: Optional[Dict[str, Any]], salary_from: Optional[int], salary_to: Optional[int]
    ) -> bool:
        """
        Проверяет, соответствует ли зарплата диапазону.

        Args:
            salary: Словарь с данными о зарплате или None
            salary_from: Минимальная зарплата
            salary_to: Максимальная зарплата

        Returns:
            True если зарплата соответствует диапазону
        """
        if salary is None:
            return False

        vac_salary_from = salary.get("from")
        vac_salary_to = salary.get("to")

        if vac_salary_from is None and vac_salary_to is None:
            return False

        vac_min = vac_salary_from if vac_salary_from is not None else vac_salary_to
        vac_max = vac_salary_to if vac_salary_to is not None else vac_salary_from

        if salary_from is not None and vac_max is not None and vac_max < salary_from:
            return False

        if salary_to is not None and vac_min is not None and vac_min > salary_to:
            return False

        return True

    def delete_vacancy(self, vacancy: Any) -> None:
        """
        Удаляет вакансию из JSON-файла.

        Args:
            vacancy: Объект вакансии для удаления

        Raises:
            IOError: При ошибках чтения/записи файла
            ValueError: Если вакансия не найдена

        Example:
            >>> saver = JSONSaver()
            >>> vacancy = Vacancy("Python", "https://hh.ru/vacancy/123", None, "Desc")
            >>> saver.delete_vacancy(vacancy)
        """
        logger.info(f"Удаление вакансии из файла: {self._filename}")

        try:
            vacancy_dict = self._vacancy_to_dict(vacancy)
        except AttributeError as e:
            logger.error(f"Ошибка при преобразовании вакансии в словарь: {type(e).__name__} - {e}")
            raise ValueError(f"Неверный объект вакансии: {e}") from e

        existing_vacancies = self._load_vacancies()
        vacancy_url = vacancy_dict.get("url", "")

        original_count = len(existing_vacancies)
        existing_vacancies = [v for v in existing_vacancies if v.get("url") != vacancy_url]

        if len(existing_vacancies) == original_count:
            logger.warning(f"Вакансия не найдена для удаления (URL: {vacancy_url})")
            raise ValueError(f"Вакансия с URL {vacancy_url} не найдена в файле")

        self._save_vacancies(existing_vacancies)
        logger.info(f"Вакансия успешно удалена из файла: {self._filename}")
