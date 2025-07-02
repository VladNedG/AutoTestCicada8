# Утилита для работы с IMAP-почтой
# Содержит функцию для получения ссылки сброса пароля из письма
# Используется в тестах восстановления пароля (например, test_password_recovery.py)

import imaplib
import email
from email.header import decode_header
import re
import time
from urllib.parse import unquote
import logging

# Создаем логгер для этого модуля
logger = logging.getLogger(__name__)

# Функция декодирует заголовок письма (например, тему) в читаемый текст
def decode_email_subject(subject):
    # Декодируем заголовок, обрабатываем возможные кодировки
    decoded = decode_header(subject)[0][0]
    if isinstance(decoded, bytes):
        return decoded.decode('utf-8', errors='ignore')
    return decoded

# Функция получает ссылку для сброса пароля из письма
# Параметры: email_address (адрес почты), email_password (пароль для входа в почту)
# max_attempts и delay управляют количеством попыток и задержкой между ними
def get_reset_link_from_email(email_address, email_password, max_attempts=10, delay=5):
    try:
        # Подключаемся к IMAP-серверу
        logger.info(f"Connecting to IMAP server for {email_address}")
        mail = imaplib.IMAP4_SSL("mail.cicada8.ru", port=993)
        mail.login(email_address, email_password)
        mail.select("inbox")  # Выбираем папку "Входящие"

        # Проверяем новые письма от info-dev@cicada8.ru
        for _ in range(max_attempts):
            _, data = mail.search(None, 'FROM "no-reply-dev@cicada8.ru" UNSEEN')
            if data[0]:
                # Берем последнее письмо
                latest_email_id = data[0].split()[-1]
                _, msg_data = mail.fetch(latest_email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                # Декодируем тему письма
                subject = decode_email_subject(msg["subject"])
                logger.info(f"Found email with subject: {subject}")

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

                # Ищем ссылку для сброса пароля
                url_pattern = r'(https://cicada\.develop\.apt\.lan/set-password/[\w\-]+/)'
                match = re.search(url_pattern, body)
                if match:
                    reset_link = unquote(match.group(0))
                    logger.info(f"Extracted reset link: {reset_link}")
                    mail.logout()  # Закрываем соединение
                    return reset_link
            logger.info("No email found, retrying...")
            time.sleep(delay)  # Ждем перед следующей попыткой

        mail.logout()
        raise Exception("No email with reset link found within timeout")
    except Exception as e:
        logger.error(f"Failed to retrieve email: {str(e)}")
        raise