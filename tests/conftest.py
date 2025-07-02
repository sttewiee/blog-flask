# tests/conftest.py
import pytest
import os
import threading
import time
from werkzeug.serving import make_server
from app import create_app, db as _db


# --- Фикстура для запуска Flask-приложения в отдельном потоке ---
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
    """Запускает Flask-приложение в отдельном потоке на время тестов в модуле."""
    server = ServerThread(app)
    server.start()
    time.sleep(1) # Даем серверу секунду на запуск
    yield
    server.shutdown()


# --- Главная фикстура для создания тестового приложения ---
@pytest.fixture(scope='session')
def app():
    """
    Создает и конфигурирует экземпляр Flask-приложения для всей тестовой сессии.
    Эта фикстура выполняется один раз за запуск pytest.
    """
    # -------------------------------------------------------------------
    # 1. Установка переменных окружения для тестового режима.
    #    Этот блок делает фикстуру универсальной для локального и CI запуска.
    # -------------------------------------------------------------------

    # Берем DATABASE_URL из окружения (для CI), если он там есть.
    # Если нет (при локальном запуске), используем стандартное значение для локального Docker.
    database_url = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/postgres'
    )
    os.environ['DATABASE_URL'] = database_url

    os.environ['SECRET_KEY'] = 'test_secret_key_for_pytest'
    os.environ['TESTING'] = 'True'
    os.environ['WTF_CSRF_ENABLED'] = 'False' # Отключаем CSRF для простоты тестов

    # -------------------------------------------------------------------
    # 2. Создание экземпляра приложения с помощью фабрики.
    # -------------------------------------------------------------------
    _app = create_app()

    # -------------------------------------------------------------------
    # 3. Подготовка базы данных в контексте приложения.
    # -------------------------------------------------------------------
    with _app.app_context():
        # Создаем все таблицы, описанные в моделях (user, post).
        _db.create_all()

    # `yield` передает готовое приложение в тесты.
    yield _app

    # -------------------------------------------------------------------
    # 4. Очистка после завершения всех тестов.
    # -------------------------------------------------------------------
    with _app.app_context():
        # Удаляем все таблицы, чтобы не загрязнять базу данных.
        _db.drop_all()


# --- Вспомогательные фикстуры ---
@pytest.fixture()
def client(app):
    """Предоставляет тестовый клиент для отправки запросов к приложению."""
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    """Предоставляет доступ к экземпляру SQLAlchemy для работы с БД в тестах."""
    with app.app_context():
        yield _db