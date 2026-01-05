"""Класс для работы с API hh.ru.

Модуль содержит класс HeadHunterAPI для получения вакансий
с платформы hh.ru через их публичное API.
"""

# 1. Импорты стандартной библиотеки
import logging
from pathlib import Path
from typing import Any, Dict, List

# 2. Импорты сторонних библиотек
import requests

# 3. Импорты из проекта
from src.api.base import DEFAULT_RETURN_VALUE, APIBase

# 4. Константы модуля
HH_API_URL = "https://api.hh.ru/vacancies"
HH_USER_AGENT = "HH-User-Agent"
REQUEST_TIMEOUT = 10
MAX_PAGES = 20
DEFAULT_PER_PAGE = 100
RUSSIA_AREA_ID = 113  # ID России в API hh.ru
RUR_CURRENCY = "RUR"  # Валюта - рубли


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

    log_file = logs_dir / "hh_api.log"
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
class HeadHunterAPI(APIBase):
    """Класс для работы с API hh.ru.

    Реализует методы для подключения к API hh.ru и получения вакансий
    по ключевому слову с поддержкой пагинации.

    Attributes:
        _url: Базовый URL API hh.ru
        _headers: Заголовки для запросов к API
        _params: Параметры запросов по умолчанию
    """

    def __init__(self) -> None:
        """
        Инициализирует экземпляр класса HeadHunterAPI.

        Устанавливает базовый URL, заголовки и параметры по умолчанию.
        Параметры включают поиск только по России (area=113) и валюту RUR.
        """
        self._url: str = HH_API_URL
        self._headers: Dict[str, str] = {"User-Agent": HH_USER_AGENT}
        self._params: Dict[str, Any] = {
            "text": "",
            "page": 0,
            "per_page": DEFAULT_PER_PAGE,
            "area": RUSSIA_AREA_ID,  # Поиск только по России
        }

    def connect(self) -> None:
        """
        Подключается к API hh.ru и проверяет доступность.

        Выполняет тестовый запрос к базовому URL API для проверки доступности.

        Raises:
            ConnectionError: Если не удалось подключиться к API
            requests.RequestException: При ошибках сетевого запроса
        """
        logger.info("Начало подключения к API hh.ru")

        try:
            response = requests.get(self._url, headers=self._headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            logger.info(f"Успешное подключение к API hh.ru. Статус: {response.status_code}")

        except requests.RequestException as e:
            # Детальное логирование HTTP ошибок для лучшей отладки
            error_msg = f"Ошибка подключения к API hh.ru: {type(e).__name__} - {e}"
            if hasattr(e, "response") and e.response is not None:
                status_code = e.response.status_code
                url = e.response.url
                error_msg += f" | HTTP {status_code} | URL: {url}"
            logger.error(error_msg)
            raise ConnectionError(f"Не удалось подключиться к API hh.ru: {e}") from e

    def get_vacancies(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает вакансии по ключевому слову с пагинацией.

        Выполняет запросы к API hh.ru для получения вакансий по ключевому слову.
        Собирает данные со всех страниц (до MAX_PAGES страниц).

        Args:
            keyword: Ключевое слово для поиска вакансий

        Returns:
            Список словарей с данными о вакансиях из ключа 'items'.
            Возвращает пустой список при ошибке.

        Example:
            >>> api = HeadHunterAPI()
            >>> vacancies = api.get_vacancies("Python")
            >>> print(len(vacancies))
            2000
        """
        logger.info(f"Начало получения вакансий по ключевому слову: {keyword}")

        if not keyword or not keyword.strip():
            logger.warning("Передано пустое ключевое слово")
            return DEFAULT_RETURN_VALUE

        # Подключаемся к API перед запросом
        try:
            self.connect()
        except ConnectionError as e:
            logger.error(f"Ошибка подключения: {type(e).__name__} - {e}")
            return DEFAULT_RETURN_VALUE

        all_vacancies: List[Dict[str, Any]] = []
        self._params["text"] = keyword.strip()
        self._params["page"] = 0

        try:
            while self._params["page"] < MAX_PAGES:
                logger.debug(f"Запрос страницы {self._params['page']}")

                response = requests.get(self._url, headers=self._headers, params=self._params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                try:
                    response_data = response.json()
                except ValueError as e:
                    logger.error(f"Ошибка парсинга JSON ответа: {type(e).__name__} - {e}")
                    break

                if "items" not in response_data:
                    logger.warning("В ответе API отсутствует ключ 'items'")
                    break

                items = response_data["items"]
                if not isinstance(items, list):
                    logger.warning(f"Ключ 'items' не является списком. Тип: {type(items)}")
                    break

                if not items:
                    logger.info(f"Страница {self._params['page']} пуста, завершение пагинации")
                    break

                # Фильтруем вакансии по валюте RUR (рубли)
                filtered_items = self._filter_by_currency(items, RUR_CURRENCY)
                all_vacancies.extend(filtered_items)
                logger.debug(
                    f"Получено {len(items)} вакансий со страницы {self._params['page']}, "
                    f"отфильтровано по валюте RUR: {len(filtered_items)}"
                )

                self._params["page"] += 1

            logger.info(f"Всего получено вакансий по России с зарплатой в рублях: {len(all_vacancies)}")
            return all_vacancies

        except requests.RequestException as e:
            # Детальное логирование HTTP ошибок для лучшей отладки
            error_msg = f"Ошибка при запросе к API hh.ru: {type(e).__name__} - {e}"
            if hasattr(e, "response") and e.response is not None:
                status_code = e.response.status_code
                url = e.response.url
                error_msg += f" | HTTP {status_code} | URL: {url}"
            logger.error(error_msg)
            return DEFAULT_RETURN_VALUE
        except KeyError as e:
            logger.error(f"Ошибка: отсутствует ключ в данных API: {e}")
            return DEFAULT_RETURN_VALUE
        except AttributeError as e:
            logger.error(f"Ошибка: отсутствует атрибут в данных API: {e}")
            return DEFAULT_RETURN_VALUE
        except TypeError as e:
            logger.error(f"Ошибка типа данных API: {e}")
            return DEFAULT_RETURN_VALUE
        except Exception as e:
            # Исключительный случай: обработка любых других неожиданных ошибок
            # для предотвращения падения программы
            logger.critical(f"Критическая неожиданная ошибка при получении вакансий: {type(e).__name__} - {e}")
            return DEFAULT_RETURN_VALUE

    def _filter_by_currency(self, items: List[Dict[str, Any]], currency: str) -> List[Dict[str, Any]]:
        """
        Фильтрует вакансии по валюте зарплаты.

        Оставляет только вакансии с зарплатой в указанной валюте или без указания зарплаты.

        Args:
            items: Список вакансий для фильтрации
            currency: Код валюты (например, "RUR" для рублей)

        Returns:
            Отфильтрованный список вакансий
        """
        filtered: List[Dict[str, Any]] = []

        for item in items:
            salary = item.get("salary")
            # Включаем вакансии без зарплаты или с зарплатой в указанной валюте
            if salary is None or salary.get("currency") == currency:
                filtered.append(item)

        return filtered
