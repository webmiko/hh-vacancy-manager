"""Тесты для утилит безопасности.

Модуль содержит тесты для функций проверки безопасности.
"""

# 1. Импорты стандартной библиотеки
from pathlib import Path

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from src.utils.security_utils import check_logs_for_leaks, print_leaks_report

# 4. Константы модуля
# (нет констант)


class TestSecurityUtils:
    """Тесты для утилит безопасности."""

    def test_check_logs_for_leaks_no_directory(self) -> None:
        """Тест проверки логов при отсутствии директории."""
        result = check_logs_for_leaks("nonexistent_directory")

        assert result == []

    def test_check_logs_for_leaks_no_leaks(self, tmp_path: Path) -> None:
        """Тест проверки логов без утечек."""
        log_file = tmp_path / "test.log"
        log_file.write_text("This is a normal log message\nNo sensitive data here\n", encoding="utf-8")

        result = check_logs_for_leaks(str(tmp_path))

        assert result == []

    def test_check_logs_for_leaks_with_api_key(self, tmp_path: Path) -> None:
        """Тест проверки логов с API ключом."""
        log_file = tmp_path / "test.log"
        # API ключ должен быть минимум 20 символов согласно паттерну
        log_file.write_text("api_key=supersecretkey1234567890\nNormal log message\n", encoding="utf-8")

        result = check_logs_for_leaks(str(tmp_path))

        assert len(result) > 0
        assert result[0][0] == "test.log"
        assert "API" in result[0][1] or "ключ" in result[0][1]

    def test_check_logs_for_leaks_with_bearer_token(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Тест проверки логов с Bearer токеном."""
        log_file = tmp_path / "test.log"
        # Bearer токен должен быть минимум 20 символов согласно паттерну
        log_file.write_text("bearer my_jwt_token_12345678901234567890\nNormal log message\n", encoding="utf-8")

        result = check_logs_for_leaks(str(tmp_path))

        assert len(result) > 0

    def test_check_logs_for_leaks_with_jwt_token(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Тест проверки логов с JWT токеном."""
        log_file = tmp_path / "test.log"
        jwt_token = (
            "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgI8V4J6B5u5v5v5v5v5v5v5v5v5v5v5v5v5v5v\n"
        )
        log_file.write_text(jwt_token, encoding="utf-8")

        result = check_logs_for_leaks(str(tmp_path))

        assert len(result) > 0

    def test_check_logs_for_leaks_empty_file(self, tmp_path: Path) -> None:
        """Тест проверки пустого лог-файла."""
        log_file = tmp_path / "empty.log"
        log_file.write_text("", encoding="utf-8")

        result = check_logs_for_leaks(str(tmp_path))

        assert result == []

    def test_check_logs_for_leaks_multiple_files(self, tmp_path: Path) -> None:
        """Тест проверки нескольких лог-файлов."""
        log_file1 = tmp_path / "test1.log"
        log_file1.write_text("Normal log message\n", encoding="utf-8")

        log_file2 = tmp_path / "test2.log"
        # API ключ должен быть минимум 20 символов согласно паттерну
        log_file2.write_text("api_key=secret12345678901234567890\n", encoding="utf-8")

        result = check_logs_for_leaks(str(tmp_path))

        assert len(result) > 0

    def test_check_logs_for_leaks_with_password(self, tmp_path: Path) -> None:
        """Тест проверки логов с паролем."""
        log_file = tmp_path / "test.log"
        # Пароль должен быть минимум 8 символов согласно паттерну
        log_file.write_text("password=mypassword123\nNormal log message\n", encoding="utf-8")

        result = check_logs_for_leaks(str(tmp_path))

        assert len(result) > 0

    def test_check_logs_for_leaks_with_secret(self, tmp_path: Path) -> None:
        """Тест проверки логов с секретом."""
        log_file = tmp_path / "test.log"
        # Секрет должен быть минимум 20 символов согласно паттерну
        log_file.write_text("secret=mysecretkey12345678901234567890\nNormal log message\n", encoding="utf-8")

        result = check_logs_for_leaks(str(tmp_path))

        assert len(result) > 0

    def test_check_logs_for_leaks_read_error(self, tmp_path: Path) -> None:
        """Тест обработки ошибки чтения файла."""
        log_file = tmp_path / "test.log"
        log_file.write_text("Normal log message\n", encoding="utf-8")

        # Делаем файл недоступным для чтения (на Unix)
        import os

        try:
            os.chmod(log_file, 0o000)

            result = check_logs_for_leaks(str(tmp_path))

            # Должен вернуть пустой список при ошибке
            assert result == []
        finally:
            os.chmod(log_file, 0o644)

    def test_print_leaks_report_empty(self, capsys: pytest.CaptureFixture) -> None:
        """Тест вывода отчета об утечках при их отсутствии."""
        print_leaks_report([])

        captured = capsys.readouterr()
        assert "не обнаружено" in captured.out or "Утечек" in captured.out

    def test_print_leaks_report_with_leaks(self, capsys: pytest.CaptureFixture) -> None:
        """Тест вывода отчета об утечках."""
        leaks = [("test.log", "API ключ", 1), ("test2.log", "Bearer токен", 5)]

        print_leaks_report(leaks)

        captured = capsys.readouterr()
        assert "test.log" in captured.out or "утечка" in captured.out.lower()
        assert "ВНИМАНИЕ" in captured.out or "потенциальных утечек" in captured.out
