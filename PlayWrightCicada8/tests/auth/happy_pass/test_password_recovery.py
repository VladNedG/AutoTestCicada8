from playwright.sync_api import Page, expect
import pytest
import os
import logging
import imaplib
import email
from email.header import decode_header
import re
import time
from urllib.parse import unquote
from dotenv import load_dotenv

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загружаем переменные окружения
load_dotenv()


# Функция для декодирования заголовков письма
def decode_email_subject(subject):
    decoded = decode_header(subject)[0][0]
    if isinstance(decoded, bytes):
        return decoded.decode('utf-8', errors='ignore')
    return decoded


# Функция для получения ссылки из письма через IMAP
def get_reset_link_from_email(email_address, email_password, max_attempts=10, delay=5):
    try:
        # Подключаемся к IMAP-серверу
        logging.info(f"Connecting to IMAP server for {email_address}")
        mail = imaplib.IMAP4_SSL("mail.cicada8.ru", port=993)
        mail.login(email_address, email_password)
        mail.select("inbox")

        # Ищем письмо от отправителя info-dev@cicada8.ru
        for _ in range(max_attempts):
            _, data = mail.search(None, 'FROM "info-dev@cicada8.ru" UNSEEN')
            if data[0]:
                latest_email_id = data[0].split()[-1]
                _, msg_data = mail.fetch(latest_email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                # Проверяем тему письма
                subject = decode_email_subject(msg["subject"])
                logging.info(f"Found email with subject: {subject}")

                # Извлекаем тело письма
                body = None
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type in ["text/plain", "text/html"]:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                if not body:
                    raise Exception("No suitable body found in email")

                # Ищем ссылку в теле письма
                url_pattern = r'(https://cicada\.develop\.apt\.lan/set-password/[\w\-]+/)'
                match = re.search(url_pattern, body)
                if match:
                    reset_link = unquote(match.group(0))  # Декодируем URL
                    logging.info(f"Extracted reset link: {reset_link}")
                    mail.logout()
                    return reset_link
            logging.info("No email found, retrying...")
            time.sleep(delay)

        mail.logout()
        raise Exception("No email with reset link found within timeout")
    except Exception as e:
        logging.error(f"Failed to retrieve email: {e}")
        raise


# Тест на проверку восстановления пароля и авторизации с новым паролем
def test_password_recovery(page: Page):
    try:
        # Получаем учетные данные из переменных окружения
        test_email = os.getenv("TEST_EMAIL", "v.nedyukhin@cicada8.ru")
        email_password = os.getenv("EMAIL_PASSWORD")
        if not email_password:
            raise Exception("EMAIL_PASSWORD not set in .env")

        # Переходим на страницу логина
        logging.info("Navigating to login page")
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load", timeout=10000)

        # Нажимаем кнопку "Забыли пароль?"
        logging.info("Clicking 'Forgot Password' link")
        forgot_password_selector = 'a[href="/password-recovery"]'
        page.locator(forgot_password_selector).wait_for(state="visible", timeout=10000)
        page.click(forgot_password_selector)

        # Ожидаем редирект на страницу восстановления
        logging.info("Waiting for password recovery page")
        page.wait_for_url("https://cicada.develop.apt.lan/password-recovery", timeout=10000)

        # Проверяем наличие текста, подтверждающего переход
        logging.info("Checking for recovery page text")
        expect(page.locator("text=Если вы забыли пароль, введите e-mail")).to_be_visible(timeout=10000)

        # Проверяем заголовок страницы восстановления
        logging.info("Checking for 'Восстановление пароля' text")
        page.wait_for_selector("text=Восстановление пароля", state="visible", timeout=10000)
        expect(page.locator("text=Восстановление пароля")).to_be_visible()

        # Заполняем поле email
        logging.info(f"Filling email field with: {test_email}")
        email_selector = 'input[placeholder="E-mail"]'
        page.locator(email_selector).wait_for(state="visible", timeout=10000)
        page.fill(email_selector, test_email)

        # Нажимаем кнопку "Восстановить"
        logging.info("Clicking 'Recover' button")
        page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)
        page.click('button[type="submit"]')

        # Проверяем сообщение об успешной отправке
        logging.info("Checking for success message")
        success_message = "text=Инструкция по восстановлению отправлена на указанную почту"
        page.wait_for_selector(success_message, state="visible", timeout=15000)
        expect(page.locator(success_message)).to_be_visible()

        # Получаем ссылку из письма
        logging.info("Retrieving reset link from email")
        reset_link = get_reset_link_from_email(test_email, email_password)

        # Переходим по ссылке из письма
        logging.info("Navigating to reset link")
        page.goto(reset_link)
        page.wait_for_load_state("load", timeout=10000)

        # Проверяем, что открылась страница сброса пароля
        logging.info("Checking reset password page")
        expect(page.locator("text=Новый пароль")).to_be_visible(timeout=10000)

        # Заполняем новый пароль
        logging.info("Filling new password")
        new_password = "Vnedyhin2419@"
        page.fill('input[placeholder="Введите пароль"]', new_password)
        page.fill('input[placeholder="Повторите пароль"]', new_password)

        # Нажимаем кнопку "Сохранить"
        logging.info("Clicking 'Save' button")
        page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)
        page.click('button[type="submit"]')

        # Проверяем успешное изменение пароля или редирект
        logging.info("Checking for password change success")
        try:
            expect(page.locator("text=Пароль успешно изменен")).to_be_visible(timeout=20000)
        except:
            logging.info("No success message found, checking for redirect to login page")
            page.wait_for_url("https://cicada.develop.apt.lan/*", timeout=10000)
            expect(page.locator("text=Вход в систему")).to_be_visible(timeout=10000)

        # Выполняем авторизацию с новым паролем
        logging.info("Attempting login with new password")
        page.goto("https://cicada.develop.apt.lan/")
        page.wait_for_load_state("load", timeout=10000)

        # Заполняем поля логина и нового пароля
        page.fill('input[placeholder="Введите e-mail"]', test_email)
        page.fill('input[placeholder="Введите пароль"]', new_password)

        # Нажимаем кнопку входа
        page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)
        page.click('button[type="submit"]')

        # Ожидаем редирект
        page.wait_for_url("https://cicada.develop.apt.lan/monitoring?current_screen=dashboard", timeout=10000)

        # Проверяем наличие элемента, подтверждающего авторизацию
        logging.info("Checking for authorization success")
        expect(page.locator("text=Моя организация")).to_be_visible(timeout=10000)

    except Exception as e:
        # Сохраняем скриншот и HTML страницы при ошибке
        page.screenshot(path="screenshot/error_screenshot.png")
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        logging.error(f"Password recovery and login test failed: {e}")
        pytest.fail(f"Password recovery and login test failed: {e}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])