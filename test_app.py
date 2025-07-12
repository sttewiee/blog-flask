import pytest
from app import create_app, db, User, Post
import os

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
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
    assert b'Blog' in response.data

def test_register_page(client):
    """Test that register page loads."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Registration' in response.data

def test_login_page(client):
    """Test that login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

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
        # Create a user first
        user = User(username='testuser', password='hashed_password')
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        
        assert response.status_code == 200

if __name__ == '__main__':
    pytest.main([__file__]) 