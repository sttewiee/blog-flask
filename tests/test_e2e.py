# tests/test_e2e.py
import re
import pytest
from playwright.sync_api import Page, expect
from datetime import datetime
import threading
import time
from werkzeug.serving import make_server

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


@pytest.fixture(scope="module")
def live_app(app):
    """Запускает Flask приложение в отдельном потоке на время тестов в модуле."""
    server = ServerThread(app)
    server.start()
    time.sleep(1)
    yield
    server.shutdown()


def test_full_user_journey(page: Page, live_app):
    """
    Тестирует полный путь пользователя в браузере.
    """
    base_url = "http://127.0.0.1:5000"

    # --- 1. Открываем главную страницу и проверяем заголовок ---
    page.goto(base_url)
    expect(page).to_have_title(re.compile("Мой блог"))

    # --- 2. Переходим на страницу регистрации ---
    page.get_by_role("link", name="Регистрация").click()
    # ПРОВЕРЯЕМ, что мы на странице /register
    expect(page).to_have_url(f"{base_url}/register")

    # --- 3. Регистрируем нового уникального пользователя ---
    username = f"e2e_user_{int(datetime.now().timestamp())}"
    password = "supersecretpassword123"

    page.get_by_placeholder("Имя пользователя").fill(username)
    page.get_by_placeholder("Пароль").fill(password)
    page.get_by_role("button", name="Зарегистрироваться").click()

    # --- 4. Логинимся под новым пользователем ---
    expect(page.locator("text=Регистрация успешна. Войдите.")).to_be_visible()
    page.get_by_placeholder("Имя пользователя").fill(username)
    page.get_by_placeholder("Пароль").fill(password)
    page.get_by_role("button", name="Войти").click()

    # --- 5. Создаем новый пост ---
    expect(page.locator(f"text=Вы вошли как {username}")).to_be_visible()
    page.get_by_role("link", name="Создать пост").click()
    expect(page).to_have_url(f"{base_url}/create")

    post_title = "Мой первый E2E пост"
    post_content = "Этот пост был создан автоматически."
    page.get_by_placeholder("Заголовок").fill(post_title)
    page.get_by_placeholder("Текст").fill(post_content)
    page.get_by_role("button", name="Опубликовать").click()

    # --- 6. Проверяем пост на главной странице ---
    # ПРОВЕРЯЕМ, что мы вернулись на главную страницу (с опциональным слешем)
    expect(page).to_have_url(re.compile(f"^{base_url}/?$"))
    expect(page.locator(f"h5:has-text('{post_title}')")).to_be_visible() # было h2, но в index.html у вас h5
    expect(page.locator(f"p:has-text('{post_content}')")).to_be_visible()
    expect(page.locator(f"small:has-text('Автор: {username}')")).to_be_visible()

    # --- 7. Выходим из системы ---
    page.get_by_role("link", name="Выйти").click()
    expect(page.locator("text=Вы вышли из аккаунта")).to_be_visible()
    expect(page.get_by_role("link", name="Войти")).to_be_visible()