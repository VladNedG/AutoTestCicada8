# Импортируем библиотеки
import pytest  # Фреймворк для написания и запуска автоматических тестов
from playwright.sync_api import Page, BrowserContext, expect  # Инструменты Playwright для управления браузером и проверки условий
import logging  # Модуль для записи логов (информации о действиях программы)
from datetime import datetime  # Модуль для работы с датой и временем, используется для создания временных меток
import os  # Модуль для работы с операционной системой, например, для чтения переменных окружения
from tests.utils.imap_utils import get_reset_link_from_email  # Пользовательская функция для получения ссылки на сброс пароля из email

# Настройка логгера
# Логгер используется для записи информации о ходе выполнения теста в файл или консоль
logger = logging.getLogger(__name__)  # Создаём логгер с именем текущего модуля для записи сообщений

# Тест восстановления пароля
# @pytest.mark.slow — метка, указывающая, что тест может выполняться медленно
@pytest.mark.slow
def test_password_recovery(page: Page, base_url: str, context: BrowserContext):
    # Логируем начало теста для отладки
    logger.info("Starting test_password_recovery")

    # Получаем учетные данные
    # Получаем email из переменной окружения TEST_EMAIL, если не задано — используем значение по умолчанию
    user_email = os.getenv("TEST_EMAIL", "v.nedyukhin@cicada8.ru")
    # Получаем пароль для доступа к почте из переменной окружения EMAIL_PASSWORD
    email_password = os.getenv("EMAIL_PASSWORD")
    # Получаем исходный пароль пользователя из переменной окружения TEST_PASSWORD
    original_password = os.getenv("TEST_PASSWORD")
    # Проверяем, что переменные EMAIL_PASSWORD и TEST_PASSWORD заданы, иначе выбрасываем ошибку
    if not email_password or not original_password:
        raise ValueError("EMAIL_PASSWORD or TEST_PASSWORD not set in .env")

    # Переходим на страницу логина
    login_url = base_url  # Используем базовый URL как адрес страницы логина
    logger.info(f"Navigating to login page: {login_url}")  # Логируем переход на страницу логина
    page.goto(login_url)  # Открываем страницу логина в браузере
    page.wait_for_load_state("load", timeout=10000)  # Ждём полной загрузки страницы (максимум 10 секунд)

    # Проверяем URL
    # Проверяем, что мы находимся на странице логина, сравнивая текущий URL
    logger.info(f"Current URL on login page: {page.url}")  # Логируем текущий URL
    if "login" in page.url.lower() or page.url == base_url:  # Проверяем, содержит ли URL слово "login" или совпадает с базовым URL
        logger.info("On login page")  # Логируем, что мы на странице логина
    else:
        # Если страница не соответствует ожидаемой, сохраняем скриншот и HTML для отладки
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени для имени файлов
        page.screenshot(path=f"screenshot/error_recovery_wrong_login_page_{timestamp}.png")  # Сохраняем скриншот страницы
        with open(f"screenshot/error_recovery_wrong_login_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Expected login page, got: {page.url}")  # Логируем ошибку
        raise ValueError("Not on login page")  # Выбрасываем ошибку, чтобы тест завершился

    # Проверяем наличие поля пароля
    # Убеждаемся, что на странице есть поле для ввода пароля
    password_selector = 'input[placeholder="Введите пароль"]'  # Селектор для поля пароля
    try:
        page.locator(password_selector).wait_for(state="visible", timeout=10000)  # Ждём, пока поле станет видимым (10 секунд)
        logger.info("Password field found")  # Логируем успешное нахождение поля
    except Exception as e:
        # Если поле не найдено, сохраняем скриншот и HTML для отладки
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_no_password_field_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_no_password_field_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Password field not found: {e}")  # Логируем ошибку
        raise ValueError("Password field not found on login page")  # Выбрасываем ошибку

    # Нажимаем «Забыли пароль?»
    # Ищем и кликаем по ссылке для восстановления пароля
    forgot_password_selector = 'a[href="/password-recovery"]'  # Селектор для ссылки «Забыли пароль?»
    logger.info(f"Looking for forgot password link: {forgot_password_selector}")  # Логируем поиск ссылки
    try:
        page.locator(forgot_password_selector).wait_for(state="visible", timeout=10000)  # Ждём, пока ссылка станет видимой
        page.click(forgot_password_selector)  # Кликаем по ссылке
        logger.info("Clicked forgot password link")  # Логируем успешный клик
    except Exception as e:
        # Если ссылка не найдена или не кликается, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_forgot_password_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_forgot_password_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to click forgot password link: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку, чтобы тест завершился

    # Проверяем переход
    # Убеждаемся, что перешли на страницу восстановления пароля
    reset_url = f"{base_url}password-recovery"  # Формируем URL страницы восстановления пароля
    logger.info(f"Waiting for password recovery page: {reset_url}")  # Логируем ожидание страницы
    try:
        page.wait_for_url(reset_url, timeout=10000)  # Ждём перехода на нужный URL (10 секунд)
        logger.info(f"Current URL after clicking forgot password: {page.url}")  # Логируем текущий URL
    except Exception as e:
        # Если переход не удался, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_no_reset_page_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_no_reset_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Did not navigate to password-recovery page: {e}")  # Логируем ошибку
        raise ValueError("Did not navigate to password-recovery page")  # Выбрасываем ошибку

    # Проверяем текст страницы
    # Проверяем наличие текста, подтверждающего, что мы на странице восстановления пароля
    try:
        page.locator("text=Если вы забыли пароль, введите e-mail").wait_for(state="visible", timeout=10000)  # Ждём текст (10 секунд)
        logger.info("Recovery page text found")  # Логируем успешное нахождение текста
    except Exception as e:
        # Если текст не найден, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_text_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_text_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Recovery page text not found: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Заполняем email
    # Вводим email в поле для запроса восстановления пароля
    logger.info(f"Requesting password reset for email: {user_email}")  # Логируем запрос на восстановление
    try:
        email_selector = 'input[placeholder="E-mail"]'  # Селектор для поля ввода email
        page.locator(email_selector).wait_for(state="visible", timeout=10000)  # Ждём, пока поле станет видимым
        page.fill(email_selector, user_email)  # Заполняем поле email
        logger.info("Email field filled successfully")  # Логируем успешное заполнение
    except Exception as e:
        # Если поле не найдено или не заполняется, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_fill_email_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_fill_email_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to fill email field: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Нажимаем кнопку отправки
    # Отправляем запрос на восстановление пароля
    logger.info("Clicking request reset button")  # Логируем клик по кнопке
    try:
        submit_selector = 'button[type="submit"]'  # Селектор для кнопки отправки формы
        page.locator(submit_selector).wait_for(state="visible", timeout=10000)  # Ждём, пока кнопка станет видимой
        page.click(submit_selector)  # Кликаем по кнопке
        logger.info(f"Current URL after clicking reset button: {page.url}")  # Логируем текущий URL
    except Exception as e:
        # Если кнопка не найдена или не кликается, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_submit_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_submit_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to click request reset button: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Ожидаем сообщение
    # Проверяем, что отображается сообщение об успешной отправке инструкций
    success_selector = 'text=Инструкция по восстановлению отправлена на указанную почту'  # Селектор для сообщения об успехе
    logger.info(f"Waiting for success message: {success_selector}")  # Логируем ожидание сообщения
    try:
        page.wait_for_selector(success_selector, state="visible", timeout=15000)  # Ждём сообщение (15 секунд)
        logger.info(f"Page content after reset request: {page.content()[:500]}...")  # Логируем первые 500 символов HTML страницы
    except Exception as e:
        # Если сообщение не появилось, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_request_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_request_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to request password reset: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Получаем ссылку
    # Извлекаем ссылку для сброса пароля из email
    logger.info("Fetching reset link from email")  # Логируем попытку получения ссылки
    try:
        reset_link = get_reset_link_from_email(user_email, email_password)  # Получаем ссылку из email
        logger.info(f"Navigating to reset link: {reset_link}")  # Логируем переход по ссылке
        page.goto(reset_link)  # Переходим по ссылке сброса пароля
        page.wait_for_load_state("load", timeout=10000)  # Ждём полной загрузки страницы
    except Exception as e:
        # Если ссылка не получена, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_link_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_link_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to fetch reset link: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Проверяем страницу сброса
    # Убеждаемся, что страница сброса пароля загрузилась
    try:
        page.locator("text=Новый пароль").wait_for(state="visible", timeout=10000)  # Ждём текст «Новый пароль» (10 секунд)
        logger.info("Reset password page loaded")  # Логируем успешную загрузку
    except Exception as e:
        # Если страница не загрузилась, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_reset_page_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_reset_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Reset password page not loaded: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Устанавливаем новый пароль
    # Вводим и подтверждаем новый пароль
    new_password = "new_temp_password_123"  # Задаём временный новый пароль
    logger.info("Setting new password")  # Логируем установку нового пароля
    try:
        page.fill('input[placeholder="Введите пароль"]', new_password)  # Заполняем поле нового пароля
        page.fill('input[placeholder="Повторите пароль"]', new_password)  # Заполняем поле подтверждения пароля
        page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)  # Ждём кнопку отправки
        page.click('button[type="submit"]')  # Кликаем по кнопке
    except Exception as e:
        # Если не удалось установить пароль, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_confirm_submit_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_confirm_submit_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to set new password: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Ожидаем подтверждение
    # Проверяем, что пароль успешно изменён
    confirm_selector = 'text=Пароль успешно изменен'  # Селектор для сообщения об успешной смене пароля
    logger.info(f"Waiting for confirmation: {confirm_selector}")  # Логируем ожидание подтверждения
    try:
        page.wait_for_selector(confirm_selector, state="visible", timeout=20000)  # Ждём сообщение (20 секунд)
    except Exception as e:
        # Если сообщение не появилось, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_confirm_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_confirm_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to confirm password reset: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Проверяем вход с новым паролем
    # Проверяем, что можем войти с новым паролем
    logger.info("Verifying login with new password")  # Логируем проверку входа
    page.goto(base_url)  # Переходим на страницу логина
    page.wait_for_load_state("load", timeout=10000)  # Ждём полной загрузки
    page.fill('input[placeholder="Введите e-mail"]', user_email)  # Заполняем поле email
    page.fill('input[placeholder="Введите пароль"]', new_password)  # Заполняем поле пароля
    page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)  # Ждём кнопку отправки
    page.click('button[type="submit"]')  # Кликаем по кнопке

    # Ожидаем дашборд
    # Проверяем, что после входа отображается главная страница (дашборд)
    dashboard_selector = 'text=Моя организация'  # Селектор для элемента дашборда
    logger.info(f"Waiting for dashboard element: {dashboard_selector}")  # Логируем ожидание дашборда
    try:
        page.wait_for_selector(dashboard_selector, state="visible", timeout=60000)  # Ждём элемент (60 секунд)
    except Exception as e:
        # Если дашборд не загрузился, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to login with new password: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Перезапускаем контекст браузера для сброса сессии
    # Создаём новый контекст, чтобы начать с чистой сессии
    logger.info("Restarting browser context to access login page")  # Логируем перезапуск контекста
    try:
        context.close()  # Закрываем текущий контекст браузера
        new_context = context.browser.new_context()  # Создаём новый контекст
        page = new_context.new_page()  # Открываем новую страницу
        page.goto(base_url)  # Переходим на страницу логина
        page.wait_for_load_state("load", timeout=10000)  # Ждём полной загрузки
        logger.info(f"New context created, current URL: {page.url}")  # Логируем текущий URL
    except Exception as e:
        # Если не удалось перезапустить контекст, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_restart_context_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_restart_context_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to restart browser context: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Проверяем, что на странице логина
    # Убеждаемся, что после перезапуска контекста мы на странице логина
    logger.info("Verifying login page after context restart")  # Логируем проверку страницы логина
    try:
        page.locator(password_selector).wait_for(state="visible", timeout=10000)  # Ждём поле пароля (10 секунд)
        logger.info("Login page loaded after context restart")  # Логируем успешную загрузку
    except Exception as e:
        # Если страница логина не загрузилась, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_login_page_after_restart_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_login_page_after_restart_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Login page not loaded after context restart: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Сбрасываем пароль к исходному
    # Повторяем процесс восстановления, чтобы вернуть исходный пароль
    logger.info("Resetting password to original value")  # Логируем сброс пароля
    try:
        page.locator(forgot_password_selector).wait_for(state="visible", timeout=10000)  # Ждём ссылку «Забыли пароль?»
        page.click(forgot_password_selector)  # Кликаем по ссылке
        page.wait_for_url(reset_url, timeout=10000)  # Ждём переход на страницу восстановления
        page.locator("text=Если вы забыли пароль, введите e-mail").wait_for(state="visible", timeout=10000)  # Ждём текст страницы
        page.locator(email_selector).wait_for(state="visible", timeout=10000)  # Ждём поле email
        page.fill(email_selector, user_email)  # Заполняем поле email
        page.locator(submit_selector).wait_for(state="visible", timeout=10000)  # Ждём кнопку отправки
        page.click(submit_selector)  # Кликаем по кнопке
        page.wait_for_selector(success_selector, state="visible", timeout=15000)  # Ждём сообщение об успехе
        reset_link = get_reset_link_from_email(user_email, email_password)  # Получаем ссылку из email
        page.goto(reset_link)  # Переходим по ссылке
        page.wait_for_load_state("load", timeout=10000)  # Ждём загрузки страницы
        page.locator("text=Новый пароль").wait_for(state="visible", timeout=10000)  # Ждём текст «Новый пароль»
        page.fill('input[placeholder="Введите пароль"]', original_password)  # Вводим исходный пароль
        page.fill('input[placeholder="Повторите пароль"]', original_password)  # Подтверждаем исходный пароль
        page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)  # Ждём кнопку отправки
        page.click('button[type="submit"]')  # Кликаем по кнопке
        page.wait_for_selector(confirm_selector, state="visible", timeout=20000)  # Ждём подтверждение смены пароля
        logger.info("Password reset to original value")  # Логируем успешный сброс
    except Exception as e:
        # Если не удалось сбросить пароль, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_reset_original_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_reset_original_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to reset password to original: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Проверяем вход с исходным паролем
    # Проверяем, что можем войти с исходным паролем после его восстановления
    logger.info("Verifying login with original password")  # Логируем проверку входа
    page.goto(base_url)  # Переходим на страницу логина
    page.wait_for_load_state("load", timeout=10000)  # Ждём загрузки страницы
    page.fill('input[placeholder="Введите e-mail"]', user_email)  # Заполняем поле email
    page.fill('input[placeholder="Введите пароль"]', original_password)  # Заполняем поле пароля
    page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)  # Ждём кнопку отправки
    page.click('button[type="submit"]')  # Кликаем по кнопке
    try:
        page.wait_for_selector(dashboard_selector, state="visible", timeout=60000)  # Ждём элемент дашборда (60 секунд)
        logger.info("Successfully logged in with original password")  # Логируем успешный вход
    except Exception as e:
        # Если вход не удался, сохраняем скриншот и HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени
        page.screenshot(path=f"screenshot/error_recovery_original_login_{timestamp}.png")  # Сохраняем скриншот
        with open(f"screenshot/error_recovery_original_login_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы
        logger.error(f"Failed to login with original password: {e}")  # Логируем ошибку
        raise  # Выбрасываем ошибку

    # Логируем успешное завершение теста
    logger.info("Password recovery test completed successfully")