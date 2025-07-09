#test to verify homepage works
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Understand developer activity" in response.data

#Test protected routes redirect without JWT
def test_dashboard_redirects(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code in (302, 401)
