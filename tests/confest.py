import pytest
from main import app
from flask_jwt_extended import JWTManager, create_access_token
import mongomock
import os

@pytest.fixture
def app():
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "JWT_COOKIE_CSRF_PROTECT": False,
        "JWT_TOKEN_LOCATION": ["cookies"],
        "MONGO_URI": "mongodb://localhost:27017/test_github_analyzer"
    })
    JWTManager(app)
    yield app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["MONGO_URI"] = "mongodb://localhost:27017/"
    with app.test_client() as client:
        yield client
