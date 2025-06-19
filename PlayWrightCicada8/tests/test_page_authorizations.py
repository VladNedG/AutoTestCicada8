from playwright.sync_api import sync_playwright, expect, Page
import pytest
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Тест на проверку Title
def test_main_page_title(page: Page):
    try:
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load")
        assert page.title() == "CICADA8"
    except Exception as e:
        pytest.fail(f"Failed to load page or check title: {e}")

# Тест на проверку авторизации
def test_authorization(page: Page):
    try:
        # Переходим на страницу логина
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load")

        # Получаем учетные данные из переменных окружения
        user_email = os.getenv("TEST_USER", "v.nedyukhin@cicada8.ru")
        user_password = os.getenv("TEST_PASSWORD", "Vnedyhin2419@")

        # Заполняем поля логина и пароля
        page.fill('input[placeholder="Введите e-mail"]', user_email)
        page.fill('input[placeholder="Введите пароль"]', user_password)

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