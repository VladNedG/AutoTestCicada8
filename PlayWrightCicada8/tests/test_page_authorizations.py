from playwright.sync_api import sync_playwright, expect, Page
import pytest
import os
import logging
from dotenv import load_dotenv

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Тест на проверку восстановления пароля
def test_password_recovery(page: Page):
    try:
        # Переходим на страницу логина
        logging.info("Navigating to login page")
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load")

        # Нажимаем кнопку "Забыли пароль?"
        logging.info("Clicking 'Forgot Password' link")
        forgot_password_selector = 'a[href="/password-recovery"]'  # Исправленный селектор
        page.locator(forgot_password_selector).wait_for(state="visible", timeout=10000)
        page.click(forgot_password_selector)

        # Ожидаем редирект на страницу восстановления
        logging.info("Waiting for password recovery page")
        page.wait_for_url("https://cicada.develop.apt.lan/password-recovery", timeout=10000)

        # Проверяем наличие текста, подтверждающего переход
        logging.info("Checking for recovery page text")
        expect(page.locator("text=Если вы забыли пароль, введите e-mail")).to_be_visible()

        # Проверяем заголовок страницы восстановления
        logging.info("Checking for 'Восстановление пароля' text")
        page.wait_for_selector("text=Восстановление пароля", state="visible", timeout=10000)
        expect(page.locator("text=Восстановление пароля")).to_be_visible()

        # Получаем учетные данные из переменных окружения
        user_email = os.getenv("TEST_USER", "v.nedyukhin@cicada8.ru")
        logging.info(f"Filling email field with: {user_email}")

        # Заполняем поле email
        email_selector = 'input[placeholder="E-mail"]'
        page.locator(email_selector).wait_for(state="visible", timeout=10000)
        page.fill(email_selector, user_email)

        # Нажимаем кнопку "Восстановить"
        logging.info("Clicking 'Recover' button")
        page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)
        page.click('button[type="submit"]')

        # Проверяем сообщение об успешной отправке
        logging.info("Checking for success message")
        success_message = "text=Инструкция по восстановлению отправлена на указанную почту"
        page.wait_for_selector(success_message, state="visible", timeout=15000)
        expect(page.locator(success_message)).to_be_visible()

    except Exception as e:
        # Сохраняем скриншот при ошибке
        page.screenshot(path="screenshot/error_screenshot.png")
        logging.error(f"Password recovery test failed: {e}")
        pytest.fail(f"Password recovery test failed: {e}")

if __name__ == "__main__":
    pytest.main(["-v", __file__])