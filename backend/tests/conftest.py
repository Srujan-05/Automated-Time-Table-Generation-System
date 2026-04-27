import pytest
import sys
import os

# Absolute path to the backend directory
backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app, db
from app.core.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-secret'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_tokens(client):
    from app.models import db, Professor
    
    # 1. Setup Admin
    client.post('/api/auth/signup', json={"email": "se23ucse020@mahindrauniversity.edu.in", "password": "password123"})
    admin_login = client.post('/api/auth/signin', json={"email": "se23ucse020@mahindrauniversity.edu.in", "password": "password123"}).get_json()
    
    # Seed data so professors exist
    client.post('/api/ingestion/seed', headers={"Authorization": f"Bearer {admin_login['access_token']}"})

    # 2. Setup Faculty
    faculty_email = "rakesh@mahindrauniversity.edu.in"
    client.post('/api/auth/signup', json={"email": faculty_email, "password": "password123"})
    faculty_login = client.post('/api/auth/signin', json={"email": faculty_email, "password": "password123"}).get_json()
    
    # 3. Setup Student
    student_email = "se23ucse150@mahindrauniversity.edu.in"
    client.post('/api/auth/signup', json={"email": student_email, "password": "password123"})
    student_login = client.post('/api/auth/signin', json={"email": student_email, "password": "password123"}).get_json()

    return {
        "admin": admin_login['access_token'],
        "faculty": faculty_login['access_token'],
        "student": student_login['access_token']
    }
