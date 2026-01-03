"""Тесты для основного модуля.

Модуль содержит тесты для main.py.
"""

# 1. Импорты стандартной библиотеки
from unittest.mock import patch

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from main import main

# 4. Константы модуля
# (нет констант)


class TestMain:
    """Тесты для основного модуля."""

    @patch("main.user_interaction")
    def test_main_calls_user_interaction(self, mock_user_interaction: pytest.Mock) -> None:
        """Тест, что main() вызывает user_interaction()."""
        main()

        mock_user_interaction.assert_called_once()

    def test_main_module_imports(self) -> None:
        """Тест, что main.py корректно импортируется."""
        import main

        assert hasattr(main, "main")
        assert callable(main.main)
