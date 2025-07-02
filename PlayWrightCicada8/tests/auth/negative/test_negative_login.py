# Тест проверяет негативный сценарий авторизации: ввод только email, без пароля
# Ожидается сообщение об ошибке "Введите пароль" и неактивная кнопка входа
# Использует фикстуры page и base_url из conftest.py

import pytest
from playwright.sync_api import expect, Page
import os
import logging

# Создаем логгер для этого модуля
logger = logging.getLogger(__name__)

# Маркировка теста как smoke (быстрый и критически важный тест)
@pytest.mark.smoke
def test_negative_login(page: Page, base_url):
    # page: Фикстура из conftest.py, возвращает новую страницу, открытую на базовом URL
    # base_url: Фикстура из conftest.py, содержит базовый URL приложения
    try:
        # Логируем начало теста
        logger.info("Navigating to login page")
        user_email = os.getenv("TEST_EMAIL", "v.nedyukhin@cicada8.ru")

        # Заполняем поле email
        logger.info(f"Filling email field with: {user_email}")
        page.fill('input[placeholder="Введите e-mail"]', user_email)

        # Убеждаемся, что поле пароля пустое
        logger.info("Ensuring password field is empty")
        page.fill('input[placeholder="Введите пароль"]', "")

        # Нажимаем кнопку входа
        logger.info("Clicking submit button")
        page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)
        page.click('button[type="submit"]')

        # Проверяем, что редирект не произошел (остались на странице логина)
        logger.info("Verifying no redirect occurred")
        expect(page).to_have_url(base_url, timeout=10000)

        # Проверяем появление сообщения об ошибке
        logger.info("Checking for 'Введите пароль' error message")
        expect(page.locator('text="Введите пароль"')).to_be_visible(timeout=10000)

        # Проверяем, что кнопка входа неактивна
        logger.info("Checking if submit button is disabled")
        expect(page.locator('button[type="submit"]')).to_be_disabled(timeout=10000)

        # Логируем успешное прохождение теста
        logger.info("Negative login test passed successfully")
    except Exception as e:
        # При ошибке сохраняем скриншот и HTML страницы
        logger.error(f"Negative login test failed: {str(e)}")
        page.screenshot(path="screenshot/error_screenshot_negative_login.png")
        with open("screenshot/error_page_negative_login.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        pytest.fail(f"Negative login test failed: {str(e)}")