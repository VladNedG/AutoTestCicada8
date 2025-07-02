# Импортируем библиотеки
import os  # Модуль для работы с операционной системой, например, для чтения переменных окружения
import pytest  # Фреймворк для написания и запуска автоматических тестов
from playwright.sync_api import sync_playwright, Page, \
    BrowserContext  # Инструменты Playwright для управления браузером в синхронном режиме
import logging  # Модуль для записи логов (информации о действиях программы)
from dotenv import load_dotenv  # Модуль для загрузки переменных окружения из файла .env
from datetime import datetime  # Модуль для работы с датой и временем, нужен для создания временных меток

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Устанавливаем уровень логов INFO: записываем только важные сообщения
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # Формат логов: время, имя логгера, уровень, сообщение
    filename='test_logs.log'  # Все логи будут сохраняться в файл test_logs.log
)
logger = logging.getLogger(__name__)  # Создаём логгер с именем текущего модуля для записи сообщений

# Загружаем .env
# Файл .env хранит конфиденциальные данные, такие как логины и пароли
load_dotenv()  # Загружаем переменные из файла .env, чтобы использовать их в коде


# Фикстура для Playwright
@pytest.fixture(scope="session")  # scope="session" означает, что фикстура создаётся один раз для всей тестовой сессии
def playwright():
    with sync_playwright() as p:  # Запускаем Playwright в синхронном режиме (для управления браузером)
        yield p  # Возвращаем объект Playwright для использования в других фикстурах


# Фикстура для браузера
# Эта фикстура запускает браузер Chromium для выполнения тестов
@pytest.fixture
def browser(playwright):  # Зависит от фикстуры playwright
    browser = playwright.chromium.launch(headless=True)  # Запускаем браузер Chromium в фоновом режиме (без интерфейса)
    yield browser  # Возвращаем объект браузера для использования в тестах
    browser.close()  # Закрываем браузер после завершения тестов, чтобы освободить ресурсы


# Фикстура для контекста
@pytest.fixture
def context(browser):  # Зависит от фикстуры browser
    context = browser.new_context()  # Создаём новый контекст браузера (аналог новой сессии)
    yield context  # Возвращаем контекст для использования в тестах
    context.close()  # Закрываем контекст после завершения тестов


# Фикстура для страницы
# Эта фикстура открывает новую страницу в браузере и переходит по указанному URL
@pytest.fixture
def page(context, base_url):  # Зависит от фикстур context и base_url
    page = context.new_page()  # Создаём новую страницу в контексте
    page.goto(base_url)  # Переходим на указанный базовый URL
    yield page  # Возвращаем объект страницы для использования в тестах
    page.close()  # Закрываем страницу после завершения тестов


# Фикстура для базового URL
# Определяем базовый URL, который будет использоваться во всех тестах
@pytest.fixture(scope="session")  # scope="session" — URL общий для всех тестов
def base_url():
    return "https://cicada.develop.apt.lan/"  # Возвращаем строку с адресом тестируемого сайта


# Фикстура для авторизованной страницы
# Эта фикстура открывает страницу, выполняет авторизацию и возвращает авторизованную страницу
@pytest.fixture
def logged_in_page(context, base_url):  # Зависит от фикстур context и base_url
    logger.info("Performing login")  # Логируем начало процесса авторизации
    page = context.new_page()  # Открываем новую страницу в контексте
    page.goto(base_url)  # Переходим на базовый URL
    page.wait_for_load_state("load", timeout=10000)  # Ждём полной загрузки страницы (максимум 10 секунд)

    # Получаем email из переменной окружения TEST_EMAIL, если она не задана — используем значение по умолчанию
    user_email = os.getenv("TEST_EMAIL", "v.nedyukhin@cicada8.ru")
    # Получаем пароль из переменной окружения TEST_PASSWORD
    user_password = os.getenv("TEST_PASSWORD")
    # Проверяем, задан ли пароль, если нет — выбрасываем ошибку
    if not user_password:
        raise ValueError("TEST_PASSWORD not set in .env")

    logger.info(f"Filling email: {user_email}")  # Логируем, что заполняем поле email
    page.fill('input[placeholder="Введите e-mail"]', user_email)  # Вводим email в поле с указанным placeholder
    logger.info("Filling password")  # Логируем, что заполняем поле пароля
    page.fill('input[placeholder="Введите пароль"]', user_password)  # Вводим пароль в поле с указанным placeholder

    logger.info("Waiting for submit button")  # Логируем ожидание кнопки отправки формы
    # Ждём, пока кнопка отправки станет видимой (максимум 10 секунд)
    page.locator('button[type="submit"]').wait_for(state="visible", timeout=10000)
    logger.info("Clicking submit button")  # Логируем клик по кнопке
    page.click('button[type="submit"]')  # Кликаем по кнопке отправки формы

    # Определяем селектор для элемента, который подтверждает успешную авторизацию
    dashboard_selector = 'text=Моя организация'
    logger.info(f"Waiting for dashboard element: {dashboard_selector}")  # Логируем ожидание элемента дашборда
    try:
        # Ждём, пока элемент "Моя организация" появится на странице (максимум 60 секунд)
        page.wait_for_selector(dashboard_selector, state="visible", timeout=60000)
    except Exception as e:
        # Если элемент не найден (ошибка авторизации), сохраняем скриншот и HTML страницы для отладки
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Создаём метку времени для имени файлов
        page.screenshot(path=f"screenshot/error_login_{timestamp}.png")  # Сохраняем скриншот страницы
        with open(f"screenshot/error_login_page_{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(page.content())  # Сохраняем HTML-код страницы в файл
        logger.error(f"Failed to find dashboard element: {e}")  # Логируем ошибку
        raise  # Повторно выбрасываем ошибку, чтобы тест завершился с ошибкой

    logger.info(f"Current URL after login: {page.url}")  # Логируем текущий URL после авторизации
    yield page  # Возвращаем авторизованную страницу для использования в тестах
    page.close()  # Закрываем страницу после завершения тестов