# Тест проверяет заголовок (title) главной страницы приложения
# Использует фикстуры page и base_url из conftest.py для открытия страницы и получения URL
# Ожидает, что заголовок страницы равен "CICADA8"

import pytest
from playwright.sync_api import expect, Page
import logging

# Создаем логгер для этого модуля
# Логи выводятся в консоль и сохраняются в test_logs.log (настроено в conftest.py)
logger = logging.getLogger(__name__)


# Маркировка теста как smoke (быстрый и критически важный тест)
# Можно запускать отдельно командой: pytest -m smoke
@pytest.mark.smoke
def test_title(page: Page, base_url):
    # page: Фикстура из conftest.py, возвращает новую страницу, открытую на базовом URL
    # base_url: Фикстура из conftest.py, содержит базовый URL приложения (https://cicada.develop.apt.lan/)
    try:
        # Логируем начало теста
        logger.info("Navigating to main page")

        # Проверяем, что страница загружена (фикстура page уже открывает base_url)
        logger.info("Waiting for page to load")
        page.wait_for_load_state("load", timeout=10000)

        # Проверяем заголовок страницы
        logger.info("Checking page title")
        expect(page).to_have_title("CICADA8", timeout=10000)

        # Логируем успешное прохождение теста
        logger.info("Main page title test passed successfully")
    except Exception as e:
        # При ошибке сохраняем скриншот и HTML страницы для отладки
        logger.error(f"Main page title test failed: {str(e)}")
        page.screenshot(path="screenshot/error_screenshot_title.png")
        with open("screenshot/error_page_title.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        pytest.fail(f"Main page title test failed: {str(e)}")