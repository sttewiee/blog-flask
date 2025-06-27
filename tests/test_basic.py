import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as flask_app

def test_home():
    with flask_app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
