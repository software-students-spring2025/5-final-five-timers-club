import pytest
import app
from bson.objectid import ObjectId

def test_home_page_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Home" in res.data

