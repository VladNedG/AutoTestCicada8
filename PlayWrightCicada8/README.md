# AutoTestCicada8

Проект автотестов для веб-приложения Cicada8 (https://cicada.develop.apt.lan/).

## Описание
Проект содержит тесты для проверки авторизации и восстановления пароля, будет дополняться другими тестами.
Тесты используют Playwright для автоматизации браузера и pytest для запуска.
Фикстуры в `conftest.py` минимизируют дублирование кода (например, авторизация).
Логи сохраняются в `test_logs.log`, а скриншоты и HTML — в `screenshot/`.

## Структура
- `tests/auth/happy_pass/`: Тесты успешной авторизации (например, `test_login.py`).
- `tests/auth/negative/`: Негативные тесты авторизации (например, без пароля).
- `tests/auth/recovery/`: Тесты восстановления пароля через email.
- `tests/dashboard/`: Плейсхолдер для тестов дашборда (пока пусто).
- `tests/utils/`: Утилиты, например, `imap_utils.py` для работы с почтой.
- `conftest.py`: Фикстуры для браузера, страницы и авторизации.
- `.env`: Переменные окружения (не коммитится).
- `requirements.txt`: Зависимости проекта.

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/VladNedG/AutoTestCicada8.git
   cd AutoTestCicada8


Установите зависимости:pip install -r requirements.txt
playwright install


Создайте файл .env в корне проекта: TEST_EMAIL=your-email@cicada8.ru
TEST_PASSWORD=your-password
EMAIL_PASSWORD=your-email-password



## Запуск тестов

Все тесты:pytest -v


Только авторизация:pytest tests/auth/ -v


Smoke-тесты (быстрые):pytest -m smoke -v


Параллельный запуск (ускоряет выполнение):pytest -n auto -v



## Отладка

Логи: test_logs.log содержит шаги выполнения тестов.
Ошибки: Скриншоты (screenshot/error_screenshot_*.png) и HTML (screenshot/error_page_*.html).
Визуальная отладка: В conftest.py измените headless=True на headless=False:browser = p.chromium.launch(headless=False, slow_mo=500)


Проверьте селекторы в DevTools:document.querySelector('input[placeholder="Введите e-mail"]')
document.querySelector('button[type="submit"]')



## Добавление новых тестов

Создайте файл в нужной папке (например, tests/dashboard/test_dashboard.py).
Используйте фикстуры из conftest.py:
page: Новая страница на базовом URL.
logged_in_page: Страница после авторизации.
base_url: Базовый URL приложения.


Пример: @pytest.mark.smoke
def test_dashboard(logged_in_page: Page):
    expect(logged_in_page.locator("text=Widget Title")).to_be_visible()



## CI/CD
Для автоматического запуска тестов добавьте в .github/workflows/test.yml:
name: Run Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: |
          pip install -r requirements.txt
          playwright install
      - run: pytest -v -n auto