"""Модуль для взаимодействия с пользователем.

Модуль содержит функцию user_interaction() для консольного
взаимодействия с пользователем при работе с вакансиями.
"""

# 1. Импорты стандартной библиотеки
import logging
import sys
from pathlib import Path
from typing import List

# 2. Импорты сторонних библиотек
import requests

# 3. Импорты из проекта
# Добавляем корневую директорию проекта в путь для корректных импортов при прямом запуске
_script_file = Path(__file__).resolve()
_project_root = _script_file.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.api.hh_api import HeadHunterAPI
from src.storage.json_saver import JSONSaver
from src.utils.input_utils import validate_keyword, validate_top_n
from src.utils.vacancy_utils import (
    filter_vacancies_by_keywords,
    get_top_vacancies,
    sort_vacancies_by_salary,
)
from src.vacancy.vacancy import Vacancy


# 4. Константы модуля
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
FILE_WRITE_MODE = "w"
ENCODING = "utf-8"


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

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "user_interface.log"
    file_handler = logging.FileHandler(log_file, mode=FILE_WRITE_MODE, encoding=ENCODING)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=TIMESTAMP_FORMAT,
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# 6. Создаем логгер для модуля
logger = _setup_logger()


def _print_vacancy(vacancy: Vacancy, index: int) -> None:
    """
    Выводит информацию о вакансии в консоль.

    Args:
        vacancy: Объект вакансии
        index: Номер вакансии в списке
    """
    print(f"\n{'=' * 80}")
    print(f"Вакансия #{index + 1}")
    print(f"{'=' * 80}")
    print(str(vacancy))
    print(f"{'=' * 80}\n")


def _print_vacancies(vacancies: List[Vacancy]) -> None:
    """
    Выводит список вакансий в консоль.

    Args:
        vacancies: Список объектов вакансий
    """
    if not vacancies:
        print("\nВакансии не найдены.\n")
        return

    print(f"\nНайдено вакансий: {len(vacancies)}\n")

    for index, vacancy in enumerate(vacancies):
        _print_vacancy(vacancy, index)


# 7. Публичные функции
def user_interaction() -> None:
    """
    Функция взаимодействия с пользователем через консоль.

    Позволяет пользователю:
    - Ввести поисковый запрос для запроса вакансий из hh.ru
    - Получить топ N вакансий по зарплате
    - Получить вакансии с ключевым словом в описании

    Returns:
        None

    Example:
        >>> user_interaction()
        Введите поисковый запрос: Python
        ...
    """
    logger.info("Начало взаимодействия с пользователем")

    print("\n" + "=" * 80)
    print("HH Vacancy Manager - Программа для работы с вакансиями hh.ru")
    print("=" * 80 + "\n")

    # Ввод поискового запроса
    search_query = input("Введите поисковый запрос для запроса вакансий из hh.ru: ").strip()

    validated_query = validate_keyword(search_query)
    if not validated_query:
        print("\nОшибка: Поисковый запрос не может быть пустым.\n")
        logger.warning("Пользователь ввел пустой поисковый запрос")
        return

    logger.info(f"Поисковый запрос: {validated_query}")

    # Получение вакансий через API
    print(f"\nПолучение вакансий по запросу '{validated_query}'...")
    api = HeadHunterAPI()

    try:
        vacancies_data = api.get_vacancies(validated_query)
    except ConnectionError as e:
        # Критично: проблемы с подключением требуют внимания
        print(f"\nОшибка подключения к API: {e}\n")
        logger.error(f"Ошибка подключения к API: {type(e).__name__} - {e}")
        return
    except requests.RequestException as e:
        print(f"\nОшибка при запросе к API: {e}\n")
        logger.error(f"Ошибка при запросе к API: {type(e).__name__} - {e}")
        return

    if not vacancies_data:
        print("\nВакансии не найдены.\n")
        logger.warning("Вакансии не найдены по запросу")
        return

    print(f"Получено вакансий: {len(vacancies_data)}")

    # Преобразование в объекты
    vacancies = Vacancy.cast_to_object_list(vacancies_data)

    if not vacancies:
        print("\nНе удалось создать объекты вакансий.\n")
        logger.warning("Не удалось создать объекты вакансий")
        return

    # Сохранение в файл
    saver = JSONSaver()
    saved_count = 0
    for vacancy in vacancies:
        try:
            saver.add_vacancy(vacancy)
            saved_count += 1
        except IOError as e:
            # Критично: проблемы с сохранением данных требуют внимания
            logger.error(f"Ошибка ввода-вывода при сохранении вакансии: {type(e).__name__} - {e}")
        except ValueError as e:
            logger.warning(f"Некорректные данные вакансии: {type(e).__name__} - {e}")
        except AttributeError as e:
            logger.warning(f"Ошибка атрибутов вакансии: {type(e).__name__} - {e}")

    print(f"Сохранено вакансий в файл: {saved_count} из {len(vacancies)}")

    # Ввод количества вакансий для топа
    top_n_input = input("\nВведите количество вакансий для вывода в топ N: ").strip()

    top_n = validate_top_n(top_n_input)
    if not top_n:
        print("\nОшибка: Введите корректное число от 1 до 1000.\n")
        logger.warning(f"Некорректный ввод для топ N: {top_n_input}")
        return

    # Ввод ключевых слов для фильтрации
    filter_input = input("Введите ключевые слова для фильтрации вакансий (через пробел): ").strip()

    filter_words: List[str] = []
    if filter_input:
        filter_words = [word.strip() for word in filter_input.split() if word.strip()]

    # Фильтрация по ключевым словам
    if filter_words:
        vacancies = filter_vacancies_by_keywords(vacancies, filter_words)
        print(f"\nПосле фильтрации по ключевым словам: {len(vacancies)} вакансий")

    # Сортировка по зарплате
    vacancies = sort_vacancies_by_salary(vacancies, reverse=True)

    # Получение топ N
    top_vacancies = get_top_vacancies(vacancies, top_n)

    # Вывод результатов
    print(f"\nТоп {len(top_vacancies)} вакансий по зарплате:")
    _print_vacancies(top_vacancies)

    logger.info("Взаимодействие с пользователем завершено")


if __name__ == "__main__":
    """Запуск функции взаимодействия с пользователем при прямом вызове модуля."""
    user_interaction()
