import pytest
from app import app as flask_app

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Blog' in response.data 
