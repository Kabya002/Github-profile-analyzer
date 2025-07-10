import responses
from main import HEADERS

@responses.activate
def test_github_api_call(client):
    username = "octocat"
    responses.add(
        responses.GET,
        f"https://api.github.com/users/{username}",
        json={"login": username, "public_repos": 10},
        status=200,
    )

    res = client.get(f"/api/github/{username}")
    assert res.status_code == 200
    assert res.json["login"] == username
