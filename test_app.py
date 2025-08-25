import pytest
from app import __version__

def test_version():
    """Тест версии приложения"""
    assert __version__ == '2.7.0-dev'

def test_import_app():
    """Тест импорта приложения"""
    from app import create_app
    assert callable(create_app)

def test_health_endpoint_works():
    """Тест что health endpoint существует"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['FLASK_ENV'] = 'testing'
    
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'version' in data
