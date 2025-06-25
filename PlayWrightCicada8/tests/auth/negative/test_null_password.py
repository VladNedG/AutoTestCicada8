from playwright.sync_api import sync_playwright, expect, Page
import pytest
import os
import logging
from dotenv import load_dotenv

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загружаем переменные окружения
load_dotenv()

# Тест на негативную проверку авторизации (только email, без пароля)
def test_null_password(page: Page):
    try:
        # Переходим на страницу логина
        logging.info("Navigating to login page")
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load", timeout=10000)

        # Получаем учетные данные из переменных окружения
        logging.info("Retrieving credentials from environment variables")
        user_email = os.getenv("TEST_USER", "v.nedyukhin@cicada8.ru")

        # Заполняем поля логина и пароля
        logging.info(f"Filling email field with: {user_email}")
        page.fill('input[placeholder="Введите e-mail"]', user_email)

        # Проверяем, что поле пароля пустое
        logging.info("Ensuring password field is empty")
        page.fill('input[placeholder="Введите пароль"]', "")

        # Нажимаем кнопку входа
        logging.info("Clicking submit button")
        page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)
        page.click('button[type="submit"]')

        # Проверяем, что редирект не произошел
        logging.info("Verifying no redirect occurred")
        expect(page).to_have_url("https://cicada.develop.apt.lan/", timeout=10000)

        # Проверяем появление сообщения об ошибке под полем пароля
        logging.info("Checking for 'Введите пароль' error message")
        error_message_selector = 'text="Введите пароль"'
        page.wait_for_selector(error_message_selector, state="visible", timeout=10000)
        expect(page.locator(error_message_selector)).to_be_visible(timeout=10000)

        # Проверяем, что кнопка входа неактивна
        logging.info("Checking if submit button is disabled")
        expect(page.locator('button[type="submit"]')).to_be_disabled(timeout=10000)

        logging.info("Negative authorization test passed successfully")

    except Exception as e:
        logging.error(f"Negative authorization test failed: {str(e)}")
        page.screenshot(path="screenshot/error_screenshot_auth.png")
        pytest.fail(f"Negative authorization test failed: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v", __file__])