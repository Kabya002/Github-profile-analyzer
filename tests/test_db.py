import mongomock
from main import db

def test_insert_user():
    test_user = {"email": "test@example.com", "name": "Test"}
    db.users = mongomock.MongoClient().db.collection
    db.users.insert_one(test_user)
    assert db.users.find_one({"email": "test@example.com"})["name"] == "Test"

