import responses

def test_home_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Financia" in res.data


@responses.activate
def test_search_valid_user_redirect(client, app):
    username = "octocat"
    responses.add(
        responses.GET,
        f"https://api.github.com/users/{username}",
        json={"login": username},
        status=200
    )
    with app.app_context():
        res = client.get(f"/search?username={username}")
        assert res.status_code == 302
        assert f"/summary/{username}" in res.headers["Location"]


@responses.activate
def test_summary_page(client, app):
    username = "octocat"
    responses.add(
        responses.GET,
        f"https://api.github.com/users/{username}",
        json={"login": username},
        status=200
    )
    responses.add(
        responses.GET,
        f"https://api.github.com/users/{username}/repos?sort=updated",
        json=[],
        status=200
    )

    with app.app_context():
        res = client.get(f"/summary/{username}")
        assert res.status_code == 200
        assert b"octocat" in res.data
