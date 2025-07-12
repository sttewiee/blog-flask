import pytest
from app import create_app, db, User, Post
from werkzeug.security import generate_password_hash
import os

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def test_home_page(client):
    """Test that home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    # Проверяем русский текст "Блог"
    assert b'\xd0\x91\xd0\xbb\xd0\xbe\xd0\xb3' in response.data

def test_register_page(client):
    """Test that register page loads."""
    response = client.get('/register')
    assert response.status_code == 200
    # Проверяем русский текст "Регистрация"
    assert b'\xd0\xa0\xd0\xb5\xd0\xb3\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f' in response.data

def test_login_page(client):
    """Test that login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    # Проверяем русский текст "Вход"
    assert b'\xd0\x92\xd1\x85\xd0\xbe\xd0\xb4' in response.data

def test_create_post_requires_auth(client):
    """Test that creating a post requires authentication."""
    response = client.get('/create')
    assert response.status_code == 302  # Redirect to login

def test_user_registration(client, app):
    """Test user registration."""
    with app.app_context():
        response = client.post('/register', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        user = User.query.filter_by(username='testuser').first()
        assert user is not None

def test_user_login(client, app):
    """Test user login."""
    with app.app_context():
        # Create a user first with hashed password
        hashed_password = generate_password_hash('testpass')
        user = User(username='testuser', password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        
        assert response.status_code == 200

def test_logout(client):
    """Test logout functionality."""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

if __name__ == '__main__':
    pytest.main([__file__]) 