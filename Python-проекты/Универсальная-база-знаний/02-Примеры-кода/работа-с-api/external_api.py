import os
from pathlib import Path
from typing import Any, Dict

import requests  # type: ignore
from dotenv import load_dotenv  # type: ignore


def convert_currency_to_rubles(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction: Словарь с данными транзакции, содержащий:
            - operationAmount.amount: сумма транзакции (строка или число)
            - operationAmount.currency.code: код валюты (RUB, USD, EUR)

    Returns:
        Сумма транзакции в рублях (float).

    Raises:
        KeyError: Если в транзакции отсутствуют необходимые поля.
        ValueError: Если не удалось преобразовать сумму в число или конвертировать валюту.
        requests.RequestException: Если произошла ошибка при запросе к API.
    """
    # Загружаем переменные окружения из .env файла
    # Пробуем несколько путей для надежности
    env_paths = [
        Path(__file__).parent.parent / ".env",  # Корень проекта
        Path.cwd() / ".env",  # Текущая рабочая директория
    ]

    env_loaded = False
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            env_loaded = True
            break

    # Если .env не найден, пробуем загрузить из текущей директории (стандартное поведение)
    if not env_loaded:
        load_dotenv(override=True)

    # Получаем API ключ из переменной окружения
    # Поддерживаем оба варианта имени для обратной совместимости
    api_key = os.getenv("API_KEY_CURRENCY")
    if api_key is None or api_key.strip() == "":
        # Формируем информативное сообщение об ошибке
        env_info = f"Проверенные пути: {[str(p) for p in env_paths]}"
        raise ValueError(
            f"API ключ не найден. Установите переменную окружения API_KEY_CURRENCY или EXCHANGE_RATE_API_KEY "
            f"в файле .env в корне проекта. Пример: API_KEY_CURRENCY=ваш_ключ\n{env_info}"
        )
    # Очищаем ключ от пробелов
    api_key = api_key.strip()

    # Извлекаем данные из транзакции
    if "operationAmount" not in transaction:
        raise KeyError("В транзакции отсутствует поле 'operationAmount'")

    operation_amount = transaction["operationAmount"]

    if "amount" not in operation_amount:
        raise KeyError("В транзакции отсутствует поле 'operationAmount.amount'")

    if "currency" not in operation_amount:
        raise KeyError("В транзакции отсутствует поле 'operationAmount.currency'")

    currency_data = operation_amount["currency"]

    if not isinstance(currency_data, dict):
        raise ValueError("Поле 'operationAmount.currency' должно быть словарем")

    if "code" not in currency_data:
        raise KeyError("В транзакции отсутствует поле 'operationAmount.currency.code'")

    amount_str = operation_amount["amount"]
    currency_code = currency_data["code"]

    # Преобразуем сумму в число
    try:
        amount = float(amount_str)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Не удалось преобразовать сумму '{amount_str}' в число: {e}") from e

    # Если валюта уже в рублях, возвращаем сумму как есть
    if currency_code == "RUB":
        return amount

    # Если валюта USD или EUR, делаем запрос к API
    if currency_code not in ("USD", "EUR"):
        raise ValueError(f"Неподдерживаемая валюта: {currency_code}. Поддерживаются только RUB, USD, EUR")

    # Формируем URL для API запроса
    api_url = "https://api.apilayer.com/exchangerates_data/convert"

    # Параметры запроса
    params = {
        "from": currency_code,
        "to": "RUB",
        "amount": amount,
    }

    # Заголовки с API ключом
    # Убеждаемся, что ключ не пустой перед использованием
    if not api_key:
        raise ValueError("API ключ пустой после очистки от пробелов")

    headers = {
        "apikey": api_key,
    }

    try:
        # Выполняем GET запрос к API
        response = requests.get(api_url, params=params, headers=headers, timeout=10)

        # Парсим JSON ответ для проверки ошибок
        try:
            response_data = response.json()
        except ValueError:
            # Если ответ не JSON, используем текст ответа
            response_text = response.text
            raise ValueError(f"API вернул невалидный JSON. Статус: {response.status_code}, Ответ: {response_text}")

        # Проверяем наличие ошибок в ответе API
        if "message" in response_data:
            error_message = response_data.get("message", "Неизвестная ошибка API")
            # Если ошибка связана с API ключом, даем более понятное сообщение
            if "api key" in error_message.lower() or "apikey" in error_message.lower():
                raise ValueError(
                    f"Ошибка API ключа: {error_message}. "
                    f"Проверьте, что переменная окружения API_KEY_CURRENCY установлена и содержит валидный ключ."
                )
            raise ValueError(f"Ошибка API: {error_message}. Полный ответ: {response_data}")

        # Проверяем статус ответа
        response.raise_for_status()

        # Проверяем наличие поля result в ответе
        if "result" not in response_data:
            raise ValueError(f"В ответе API отсутствует поле 'result'. Ответ: {response_data}")

        # Извлекаем конвертированную сумму
        converted_amount = response_data["result"]

        # Преобразуем в float и возвращаем
        return float(converted_amount)

    except requests.RequestException as e:
        # Если это HTTP ошибка, пытаемся извлечь детали из ответа
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get("message", str(e))
                raise requests.RequestException(
                    f"Ошибка при запросе к API конвертации валют (HTTP {e.response.status_code}): {error_message}"
                ) from e
            except (ValueError, AttributeError):
                pass
        raise requests.RequestException(f"Ошибка при запросе к API конвертации валют: {e}") from e
