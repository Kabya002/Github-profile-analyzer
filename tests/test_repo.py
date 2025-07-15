import responses

@responses.activate
def test_repo_detail_page(client, app):
    username = "octocat"
    repo = "test-repo"

    # Mock repo metadata
    responses.add(
        responses.GET,
        f"https://api.github.com/repos/{username}/{repo}",
        json={"name": repo, "language": "Python"},
        status=200
    )

    # Mock languages
    responses.add(
        responses.GET,
        f"https://api.github.com/repos/{username}/{repo}/languages",
        json={"Python": 12345},
        status=200
    )

    # Mock README
    responses.add(
        responses.GET,
        f"https://api.github.com/repos/{username}/{repo}/readme",
        json={"content": "IyBUZXN0IFJFQURNRQ=="},  # base64 for "# Test README"
        status=200
    )

    # Mock file tree
    responses.add(
        responses.GET,
        f"https://api.github.com/repos/{username}/{repo}/contents/",
        json=[],
        status=200
    )

    with app.app_context():
        res = client.get(f"/repo/{username}/{repo}")
        assert res.status_code == 200
        assert b"Test README" in res.data
