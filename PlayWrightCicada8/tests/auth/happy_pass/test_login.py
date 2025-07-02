# Тест проверяет успешную авторизацию с корректными email и паролем
# Использует фикстуру logged_in_page из conftest.py для выполнения авторизации
# Проверяет наличие кнопки с email пользователя и текста "Моя организация"

from playwright.sync_api import expect, Page
import pytest
import os
import logging

# Создаем логгер для этого модуля
logger = logging.getLogger(__name__)

# Маркировка теста как smoke (быстрый и критически важный тест)
# Можно запускать отдельно командой: pytest -m smoke
@pytest.mark.smoke
def test_login(logged_in_page: Page):
    # logged_in_page: Фикстура из conftest.py, возвращает страницу после авторизации
    # Автоматически выполняет вход и закрывает модальное окно (если есть)
    try:
        # Проверяем наличие кнопки с email пользователя
        logger.info("Checking for successful login")
        user_email = os.getenv("TEST_EMAIL", "v.nedyukhin@cicada8.ru")
        expect(logged_in_page.locator('button', has_text=user_email)).to_be_visible(timeout=10000)

        # Проверяем наличие текста "Моя организация" на дашборде
        logger.info("Checking for 'Моя организация' text")
        expect(logged_in_page.locator("text=Моя организация")).to_be_visible(timeout=10000)

        # Логируем успешное прохождение теста
        logger.info("Login test passed successfully")
    except Exception as e:
        # При ошибке сохраняем скриншот и HTML страницы для отладки
        logger.error(f"Login test failed: {str(e)}")
        logged_in_page.screenshot(path="screenshot/error_screenshot_login.png")
        with open("screenshot/error_page_login.html", "w", encoding="utf-8") as f:
            f.write(logged_in_page.content())
        pytest.fail(f"Login test failed: {str(e)}")