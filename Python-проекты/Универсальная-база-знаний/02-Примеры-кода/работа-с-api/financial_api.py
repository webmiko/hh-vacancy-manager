"""Модуль для работы с внешними финансовыми API.

Этот модуль содержит функции для получения курсов валют
и цен акций через внешние API.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Константы модуля
ENCODING = "utf-8"
FILE_WRITE_MODE = "w"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_API_KEY_PLACEHOLDER = "your_api_key_here"
DEFAULT_API_URL = "https://api.exchangerate-api.com/v4"
ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query"
REQUEST_TIMEOUT = 10
STOCK_REQUEST_DELAY = 0.2


def _sanitize_error_message(error_msg: str) -> str:
    """
    Удаляет чувствительные данные (API ключи) из сообщения об ошибке.

    Args:
        error_msg: Исходное сообщение об ошибке

    Returns:
        Сообщение об ошибке без чувствительных данных

    Example:
        >>> msg = "Error: https://api.example.com?key=secret123"
        >>> _sanitize_error_message(msg)
        'Error: https://api.example.com?key=***'
    """
    # Маскируем API ключи в URL параметрах
    # Паттерны для различных форматов API ключей
    import re

    patterns = [
        (r"(access_key=)([^&\s]+)", r"\1***"),
        (r"(apikey=)([^&\s]+)", r"\1***"),
        (r"(api_key=)([^&\s]+)", r"\1***"),
        (r"(key=)([^&\s]+)", r"\1***"),
    ]

    sanitized = error_msg
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля financial_api.

    Returns:
        Настроенный логгер для модуля financial_api
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "financial_api.log"
    file_handler = logging.FileHandler(log_file, mode=FILE_WRITE_MODE, encoding=ENCODING)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=TIMESTAMP_FORMAT,
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# Создаем логгер для модуля
logger = _setup_logger()


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """
    Получает текущие курсы валют через API.

    Использует эндпоинт /latest для получения актуальных курсов.
    API ключ загружается из переменной окружения API_KEY.

    Args:
        currencies: Список кодов валют (например, ['USD', 'EUR'])

    Returns:
        Список словарей с курсами валют. Каждый словарь содержит:
        - currency: код валюты
        - rate: курс валюты
        Возвращает пустой список при ошибке.

    Example:
        >>> rates = get_currency_rates(['USD', 'EUR'])
        >>> print(rates)
        [{'currency': 'USD', 'rate': 73.21}, {'currency': 'EUR', 'rate': 87.08}]
    """
    logger.info(f"Запрос курсов валют: {', '.join(currencies)}")

    if not currencies:
        logger.warning("Список валют пуст")
        return []

    # Загрузка API ключа из переменных окружения
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL", DEFAULT_API_URL)

    # Используем бесплатный exchangerate-api.com по умолчанию
    # Он не требует ключа и работает стабильно
    use_free_api = "exchangerate-api.com" in api_url or not api_key or api_key == DEFAULT_API_KEY_PLACEHOLDER

    try:
        # Формирование URL для запроса
        if use_free_api:
            # Бесплатный API exchangerate-api.com - используем базовую валюту RUB
            # API вернет курсы типа 1 RUB = X USD, нам нужно инвертировать для отображения
            free_api_url = DEFAULT_API_URL
            base_currency = "RUB"
            url = f"{free_api_url}/latest/{base_currency}"
            params = {}  # Не требует ключа для базового использования
            logger.debug("Использование бесплатного API exchangerate-api.com")
        else:
            # Другие API требуют ключ
            symbols = ",".join(currencies)
            url = f"{api_url}/latest"
            params = {"access_key": api_key, "symbols": symbols}
            logger.debug(f"Использование API с ключом: {api_url}")

        logger.debug(f"Запрос к API: {url}")

        # Выполнение запроса
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

        # Проверка статуса ответа
        response.raise_for_status()

        data = response.json()

        # Обработка ответа API
        rates: List[Dict[str, Any]] = []
        # Поддержка разных форматов ответа API
        # Явная проверка типов для безопасности
        if isinstance(data, dict) and "rates" in data:
            # Формат exchangerate-api.com и подобных
            rates_data = data["rates"]
            base_currency_from_response = data.get("base", "USD")

            if isinstance(rates_data, dict):
                for currency in currencies:
                    if currency in rates_data:
                        rate_value = rates_data[currency]
                        # Явная проверка типа значения курса
                        if isinstance(rate_value, (int, float)):
                            # Если базовая валюта RUB, инвертируем курс
                            # (API возвращает 1 RUB = X USD, нам нужно 1 USD = Y RUB)
                            if base_currency_from_response == "RUB" and rate_value > 0:
                                final_rate = 1.0 / float(rate_value)
                            else:
                                final_rate = float(rate_value)
                            rates.append({"currency": currency, "rate": final_rate})
                        else:
                            logger.warning(f"Некорректный тип курса для валюты {currency}: {type(rate_value)}")
                    else:
                        logger.warning(f"Курс для валюты {currency} не найден в ответе API")
        elif isinstance(data, dict) and "conversion_rates" in data:
            # Альтернативный формат
            conversion_rates = data["conversion_rates"]
            if isinstance(conversion_rates, dict):
                for currency in currencies:
                    if currency in conversion_rates:
                        rate_value = conversion_rates[currency]
                        # Явная проверка типа значения курса
                        if isinstance(rate_value, (int, float)):
                            rates.append({"currency": currency, "rate": float(rate_value)})
                        else:
                            logger.warning(f"Некорректный тип курса для валюты {currency}: {type(rate_value)}")
        else:
            logger.warning(f"Неожиданный формат ответа API. Доступные ключи: {list(data.keys())}")
            return []

        logger.info(f"Получено курсов валют: {len(rates)}")
        return rates

    except requests.exceptions.HTTPError as e:
        # Если ошибка 401 (Unauthorized), пробуем бесплатный API
        if e.response is not None and e.response.status_code == 401 and not use_free_api:
            logger.warning("Ошибка авторизации API. Пробуем бесплатный API exchangerate-api.com")
            try:
                # Используем бесплатный API как fallback
                free_api_url = DEFAULT_API_URL
                base_currency = "RUB"
                url = f"{free_api_url}/latest/{base_currency}"
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()

                # Обработка ответа бесплатного API
                fallback_rates: List[Dict[str, Any]] = []
                if isinstance(data, dict) and "rates" in data:
                    rates_data = data["rates"]
                    base_currency_from_response = data.get("base", "USD")
                    if isinstance(rates_data, dict):
                        for currency in currencies:
                            if currency in rates_data:
                                rate_value = rates_data[currency]
                                if isinstance(rate_value, (int, float)):
                                    if base_currency_from_response == "RUB" and rate_value > 0:
                                        final_rate = 1.0 / float(rate_value)
                                    else:
                                        final_rate = float(rate_value)
                                    fallback_rates.append({"currency": currency, "rate": final_rate})
                logger.info(f"Получено курсов валют через бесплатный API: {len(fallback_rates)}")
                return fallback_rates
            except Exception as fallback_error:
                error_msg = "Ошибка при использовании бесплатного API"
                logger.error(f"{error_msg}: {type(fallback_error).__name__} - {fallback_error}")
                return []

        error_msg = "Ошибка при запросе к API валют"
        safe_error = _sanitize_error_message(str(e))
        logger.error(f"{error_msg}: {type(e).__name__} - {safe_error}")
        return []
    except requests.exceptions.RequestException as e:
        error_msg = "Ошибка при запросе к API валют"
        # Безопасное логирование без API ключей
        safe_error = _sanitize_error_message(str(e))
        logger.error(f"{error_msg}: {type(e).__name__} - {safe_error}")
        return []
    except json.JSONDecodeError as e:
        error_msg = "Ошибка парсинга JSON ответа от API"
        logger.error(f"{error_msg}: {type(e).__name__} - {e}")
        return []
    except Exception as e:
        error_msg = "Неожиданная ошибка при получении курсов валют"
        logger.error(f"{error_msg}: {type(e).__name__} - {e}")
        return []


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает текущие цены акций через Alpha Vantage API.

    API ключ загружается из переменной окружения API_KEY.

    Args:
        stocks: Список тикеров акций (например, ['AAPL', 'AMZN'])

    Returns:
        Список словарей с ценами акций. Каждый словарь содержит:
        - stock: тикер акции
        - price: цена акции
        Возвращает пустой список при ошибке.

    Example:
        >>> prices = get_stock_prices(['AAPL', 'AMZN'])
        >>> print(prices)
        [{'stock': 'AAPL', 'price': 150.12}, {'stock': 'AMZN', 'price': 3173.18}]
    """
    logger.info(f"Запрос цен акций: {', '.join(stocks)}")

    if not stocks:
        logger.warning("Список акций пуст")
        return []

    # Загрузка API ключа из переменных окружения
    api_key = os.getenv("API_KEY")

    if not api_key or api_key == DEFAULT_API_KEY_PLACEHOLDER:
        error_msg = "API ключ не найден или не установлен"
        logger.error(error_msg)
        return []

    prices: List[Dict[str, Any]] = []

    # Alpha Vantage требует отдельный запрос для каждой акции
    # (или можно использовать BATCH_QUOTES, но GLOBAL_QUOTE проще)
    for stock in stocks:
        try:
            # Формирование параметров для Alpha Vantage
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": stock,
                "apikey": api_key,
            }

            logger.debug(f"Запрос к Alpha Vantage API для {stock}")

            # Выполнение запроса
            response = requests.get(ALPHA_VANTAGE_API_URL, params=params, timeout=REQUEST_TIMEOUT)

            # Проверка статуса ответа
            response.raise_for_status()

            data = response.json()

            # Обработка ответа Alpha Vantage
            # Формат: {"Global Quote": {"01. symbol": "AAPL", "05. price": "150.12", ...}}
            # Явная проверка типов для безопасности
            if isinstance(data, dict) and "Global Quote" in data:
                quote = data["Global Quote"]
                if isinstance(quote, dict) and quote:
                    # Alpha Vantage возвращает цену в поле "05. price"
                    price_value = quote.get("05. price", "")
                    if price_value:
                        # Явная проверка типа: может быть строка или число
                        if isinstance(price_value, (int, float)):
                            price = float(price_value)
                        elif isinstance(price_value, str):
                            try:
                                price = float(price_value)
                            except ValueError:
                                logger.warning(f"Некорректный формат цены для {stock}: {price_value}")
                                continue
                        else:
                            logger.warning(f"Некорректный тип цены для {stock}: {type(price_value)}")
                            continue
                        prices.append({"stock": stock, "price": price})
                        logger.debug(f"Получена цена для {stock}: {price}")
                    else:
                        logger.warning(f"Цена не найдена в ответе API для {stock}")
            elif isinstance(data, dict) and "Error Message" in data:
                error_msg_value = data.get("Error Message")
                error_msg = str(error_msg_value) if error_msg_value else "Неизвестная ошибка API"
                logger.warning(f"Ошибка API для {stock}: {error_msg}")
            elif "Note" in data:
                # Alpha Vantage может вернуть сообщение о лимите запросов
                # Не логируем это сообщение, так как оно содержит API ключ
                # Это просто информационное сообщение о лимите запросов
                pass
            else:
                logger.warning(f"Неожиданный формат ответа API для {stock}")

            # Небольшая задержка между запросами (Alpha Vantage имеет лимит 5 запросов/минуту для бесплатного плана)
            time.sleep(STOCK_REQUEST_DELAY)

        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка при запросе к API для акции {stock}"
            # Безопасное логирование без API ключей
            safe_error = _sanitize_error_message(str(e))
            logger.error(f"{error_msg}: {type(e).__name__} - {safe_error}")
        except json.JSONDecodeError as e:
            error_msg = f"Ошибка парсинга JSON ответа от API для {stock}"
            logger.error(f"{error_msg}: {type(e).__name__} - {e}")
        except Exception as e:
            error_msg = f"Неожиданная ошибка при получении цены для {stock}"
            logger.error(f"{error_msg}: {type(e).__name__} - {e}")

    logger.info(f"Получено цен акций: {len(prices)} из {len(stocks)}")
    return prices

