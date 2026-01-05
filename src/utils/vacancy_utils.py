"""Вспомогательные функции для работы с вакансиями.

Модуль содержит функции для фильтрации, сортировки и обработки вакансий.
"""

# 1. Импорты стандартной библиотеки
from typing import Any, List

# 2. Импорты сторонних библиотек
# (нет сторонних библиотек)

# 3. Импорты из проекта
# (будут добавлены по мере необходимости)

# 4. Константы модуля
DEFAULT_RETURN_VALUE: List[Any] = []


def filter_vacancies_by_keywords(vacancies: List[Any], keywords: List[str]) -> List[Any]:
    """
    Фильтрует вакансии по ключевым словам в описании.

    Args:
        vacancies: Список объектов вакансий
        keywords: Список ключевых слов для поиска

    Returns:
        Отфильтрованный список вакансий. Возвращает пустой список при ошибке.

    Example:
        >>> vacancies = [vacancy1, vacancy2]
        >>> filtered = filter_vacancies_by_keywords(vacancies, ["Python", "Django"])
        >>> print(len(filtered))
        1
    """
    if not vacancies or not keywords:
        return vacancies if vacancies else DEFAULT_RETURN_VALUE

    filtered: List[Any] = []

    for vacancy in vacancies:
        try:
            description = vacancy.description.lower()
            if any(keyword.lower() in description for keyword in keywords):
                filtered.append(vacancy)
        except AttributeError:
            # Пропускаем вакансии без атрибута description
            continue

    return filtered


def sort_vacancies_by_salary(vacancies: List[Any], reverse: bool = True) -> List[Any]:
    """
    Сортирует вакансии по зарплате.

    Args:
        vacancies: Список объектов вакансий
        reverse: Если True, сортировка по убыванию (от большей к меньшей)

    Returns:
        Отсортированный список вакансий. Возвращает пустой список при ошибке.

    Example:
        >>> vacancies = [vacancy1, vacancy2, vacancy3]
        >>> sorted_vacancies = sort_vacancies_by_salary(vacancies, reverse=True)
        >>> print(sorted_vacancies[0].name)
        Highest Salary Vacancy
    """
    if not vacancies:
        return DEFAULT_RETURN_VALUE

    try:
        return sorted(vacancies, reverse=reverse)
    except (TypeError, AttributeError) as e:
        # Логируем ошибку для отладки, но не прерываем выполнение
        # Это может произойти, если объекты вакансий не поддерживают сравнение
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Ошибка при сортировке вакансий: {type(e).__name__} - {e}")
        return DEFAULT_RETURN_VALUE


def get_top_vacancies(vacancies: List[Any], top_n: int) -> List[Any]:
    """
    Получает топ N вакансий из отсортированного списка.

    Args:
        vacancies: Список объектов вакансий (должен быть отсортирован)
        top_n: Количество вакансий для возврата

    Returns:
        Список из топ N вакансий. Возвращает пустой список при ошибке.

    Example:
        >>> vacancies = [vacancy1, vacancy2, vacancy3, vacancy4, vacancy5]
        >>> top_3 = get_top_vacancies(vacancies, 3)
        >>> print(len(top_3))
        3
    """
    if not vacancies or top_n <= 0:
        return DEFAULT_RETURN_VALUE

    return vacancies[:top_n]
