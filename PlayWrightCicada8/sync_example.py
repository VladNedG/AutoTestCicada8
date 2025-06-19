from playwright.sync_api import  sync_playwright
from pytest_playwright.pytest_playwright import browser

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://cicada.develop.apt.lan/")
    page.screenshot(path="screenshot/s_homepage.png")
    browser.close()