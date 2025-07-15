import pytest
from backend.main import app as flask_app 
from flask_jwt_extended import JWTManager

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret",
        "JWT_COOKIE_CSRF_PROTECT": False,
        "JWT_TOKEN_LOCATION": ["cookies"],
        "MONGO_URI": "mongodb://localhost:27017/test_github_analyzer"
    })
    yield flask_app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
