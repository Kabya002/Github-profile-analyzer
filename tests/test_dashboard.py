from flask_jwt_extended import create_access_token

def test_dashboard_requires_auth(client):
    res = client.get("/dashboard/octocat", follow_redirects=True)
    assert b"Please log in to access this page." in res.data

#Test protected routes redirect without JWT
def test_dashboard_redirects(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code in (302, 401)

def test_settings_page_requires_login(client):
    res = client.get("/settings", follow_redirects=True)
    assert b"Please log in to access this page." in res.data
