from playwright.sync_api import sync_playwright, expect, Page
import pytest
import os
import logging
from dotenv import load_dotenv

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загружаем переменные окружения
load_dotenv()

# Тест на проверку авторизации
def test_authorization(page: Page):
    try:
        # Переходим на страницу логина
        logging.info("Navigating to login page")
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load")

        # Получаем учетные данные из переменных окружения
        logging.info("Retrieving credentials from environment variables")
        user_email = os.getenv("TEST_USER", "v.nedyukhin@cicada8.ru")
        user_password = os.getenv("TEST_PASSWORD", "Vnedyhin2419@")

        # Заполняем поля логина и пароля
        logging.info(f"Filling email field with: {user_email}")
        page.fill('input[placeholder="Введите e-mail"]', user_email)
        logging.info("Filling password field")
        page.fill('input[placeholder="Введите пароль"]', user_password)

        # Нажимаем кнопку входа
        logging.info("Clicking submit button")
        page.locator('button[type="submit"]').wait_for(state="visible")
        page.click('button[type="submit"]')

        # Ожидаем редирект
        logging.info("Waiting for redirect to dashboard")
        page.wait_for_url("https://cicada.develop.apt.lan/monitoring?current_screen=dashboard")

        # Проверяем наличие элемента, подтверждающего авторизацию
        logging.info(f"Checking for button with email: {user_email}")
        expect(page.locator('button', has_text=user_email)).to_be_visible()

        # Проверяем URL
        logging.info("Verifying URL")
        assert page.url == "https://cicada.develop.apt.lan/monitoring?current_screen=dashboard"

        # Проверяем текст
        logging.info("Checking for 'Моя организация' text")
        page.wait_for_selector("text=Моя организация", state="visible")
        expect(page.locator("text=Моя организация")).to_be_visible()

        logging.info("Authorization test passed successfully")

    except Exception as e:
        logging.error(f"Authorization test failed: {str(e)}")
        page.screenshot(path="screenshot/error_screenshot_auth.png")
        pytest.fail(f"Authorization test failed: {e}")

if __name__ == "__main__":
    pytest.main(["-v", __file__])