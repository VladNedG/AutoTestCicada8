from playwright.sync_api import sync_playwright, expect, Page
import pytest

# Тест на проверку Title
def test_main_page_title(page: Page):
    try:
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load")
        assert page.title() == "CICADA8"
    except Exception as e:
        pytest.fail(f"Failed to load page or check title: {e}")