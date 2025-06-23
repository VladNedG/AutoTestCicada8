from playwright.sync_api import sync_playwright, expect, Page
import pytest
import os
import logging
from dotenv import load_dotenv

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загружаем переменные окружения
load_dotenv()

# Тест на проверку авторизации с пустым паролем
def test_auth_null_pass(page: Page):
    try:
        # Переходим на страницу логина
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load")

        # Получаем логин из переменных окружения
        user_email = os.getenv("TEST_USER", "v.nedyukhin@cicada8.ru")

        # Заполняем поле логина
        page.fill('input[placeholder="Введите e-mail"]', user_email)

        # Нажимаем кнопку входа
        page.locator('button[type="submit"]').wait_for(state="visible")
        page.click('button[type="submit"]')

        # Ожидаем редирект
        page.wait_for_url("https://cicada.develop.apt.lan/statistics?current_screen=dashboard")

        # Проверяем наличие элемента, подтверждающего авторизацию
        expect(page.locator('button', has_text=user_email)).to_be_visible()

        # Проверяем URL
        assert page.url == "https://cicada.develop.apt.lan/statistics?current_screen=dashboard"

        # Проверяем текст
        page.wait_for_selector("text=Моя организация", state="visible")
        expect(page.locator("text=Моя организация")).to_be_visible()
    except Exception as e:
        pytest.fail(f"Authorization test failed: {e}")

if __name__ == "__main__":
    pytest.main(["-v", __file__])