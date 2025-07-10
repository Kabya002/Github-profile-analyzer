from unittest.mock import patch
from flask_dance.consumer.storage import MemoryStorage
from flask_dance.contrib.github import github

def test_mock_github_oauth(client):
    with patch.object(github, "authorized", return_value=True), \
         patch.object(github, "get", return_value=MockResponse()):
        res = client.get("/github_login/github/authorized")
        assert res.status_code in [200, 302]

class MockResponse:
    def json(self):
        return {"login": "mockuser", "name": "Mock User"}
