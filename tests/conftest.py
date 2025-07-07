# tests/conftest.py
import pytest
import os
import threading
import time
from werkzeug.serving import make_server
from app import create_app, db as _db


# --- Фикстура для запуска Flask-приложения в отдельном потоке (для E2E тестов) ---
class ServerThread(threading.Thread):
    def __init__(self, app, port=5000):
        super().__init__()
        self.app = app
        # Используем 127.0.0.1 для сервера, чтобы избежать запросов брандмауэра
        self.srv = make_server('127.0.0.1', port, self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self._stop_event = threading.Event()

    def run(self):
        # Запускаем сервер, пока не будет вызван shutdown
        self.srv.serve_forever()

    def shutdown(self):
        # Сигнализируем серверу о завершении работы
        self.srv.shutdown()


@pytest.fixture(scope="session")
def live_server_url(app):
    """
    Возвращает URL запущенного в отдельном потоке Flask-сервера.
    Используется для E2E-тестов с Playwright.
    """
    port = 5000  # Стандартный порт для разработки
    server = ServerThread(app, port)
    server.start()
    
    # Даем серверу немного времени на запуск
    time.sleep(1)

    # `yield` передает URL в тесты
    yield f"http://127.0.0.1:{port}"

    # После завершения всех тестов в сессии, останавливаем сервер
    server.shutdown()
    server.join() # Ждем завершения потока


# --- Главная фикстура для создания тестового приложения ---
@pytest.fixture(scope='session')
def app():
    """
    Создает и конфигурирует экземпляр Flask-приложения для всей тестовой сессии.
    
    Эта фикстура предполагает, что ВСЕ критически важные переменные окружения
    (DATABASE_URL, SECRET_KEY) уже установлены средой выполнения
    (например, файлом .github/workflows/ci.yml или локально перед запуском pytest).
    """
    # Устанавливаем ТОЛЬКО те переменные, которые специфичны для тестового режима
    # и не являются секретами или конфигурацией окружения.
    os.environ['TESTING'] = 'True'
    os.environ['WTF_CSRF_ENABLED'] = 'False' # Отключаем CSRF для простоты E2E-тестов

    # Создаем приложение. Фабрика create_app() сама подхватит переменные из окружения.
    _app = create_app()

    # Контекст приложения необходим для работы с базой данных
    with _app.app_context():
        # Полностью очищаем и создаем базу данных перед запуском всех тестов
        _db.drop_all()
        _db.create_all()

    # `yield` передает готовое приложение в тесты
    yield _app

    # --- Очистка после завершения всех тестов ---
    with _app.app_context():
        # Удаляем все таблицы, чтобы не загрязнять базу данных
        _db.drop_all()


# --- Вспомогательные фикстуры ---
@pytest.fixture()
def client(app):
    """Предоставляет тестовый клиент для отправки HTTP-запросов к приложению."""
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    """
    Предоставляет доступ к экземпляру SQLAlchemy для работы с БД в тестах.
    Откатывает транзакции после каждого теста для изоляции.
    """
    with app.app_context():
        # Начинаем транзакцию
        connection = _db.engine.connect()
        transaction = connection.begin()

        # `yield` передает сессию в тест
        yield _db

        # Откатываем все изменения, сделанные в тесте
        transaction.rollback()
        connection.close()
        _db.session.remove()