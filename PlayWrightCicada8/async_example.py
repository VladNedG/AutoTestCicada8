from playwright.async_api import async_playwright
import asyncio

from sync_example import browser


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await  browser.new_page()
        await page.goto("https://cicada.develop.apt.lan/")
        await page.screenshot(path = "screenshot/as_homepage.png")
        await browser.close()

asyncio.run(main())