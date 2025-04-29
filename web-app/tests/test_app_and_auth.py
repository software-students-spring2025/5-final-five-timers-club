from flask import url_for
import pytest
from werkzeug.security import generate_password_hash
from unittest.mock import patch, MagicMock

# testing home page
def test_home_page(client):
    resp = client.get(url_for('home'))
    assert resp.status_code == 200
    assert b'Emotify' in resp.data

# testing unauthorized access to protected endpoints
def test_protected_endpoints_redirect(client):
    resp1 = client.post('/submit-video', json={'image': 'data:test'})
    assert resp1.status_code == 302
    resp2 = client.get(url_for('my_songs'))
    assert resp2.status_code == 302

# testing login and register pages render
def test_login_register_pages(client):
    resp_login = client.get(url_for('auth.login'))
    assert resp_login.status_code == 200
    assert b'Log In' in resp_login.data

    resp_reg = client.get(url_for('auth.register'))
    assert resp_reg.status_code == 200
    assert b'Register' in resp_reg.data

# testing registration POST
def test_register_post_success(client, monkeypatch):
    # simulating username not taken
    monkeypatch.setattr('auth.users_coll.find_one', lambda q: None)
    inserted = []
    def fake_insert(doc): inserted.append(doc)
    monkeypatch.setattr('auth.users_coll.insert_one', fake_insert)

    resp = client.post(url_for('auth.register'), data={
        'username': 'newuser', 'password': 'pass123'
    }, follow_redirects=True)

    assert b'Account created' in resp.data
    assert len(inserted) == 1

# testing registration POST failure when username exists
def test_register_post_taken(client, monkeypatch):
    monkeypatch.setattr('auth.users_coll.find_one', lambda q: {'_id': 1})
    resp = client.post(url_for('auth.register'), data={
        'username': 'taken', 'password': 'pw'
    }, follow_redirects=True)
    assert b'Username already taken' in resp.data

# testing login POST
def test_login_post_success(client, monkeypatch):
    # creating a fake user dict for this 
    fake_user = {'_id': 1, 'username': 'u', 'password_hash': generate_password_hash('pw')}
    monkeypatch.setattr('auth.users_coll.find_one', lambda q: fake_user)

    resp = client.post(url_for('auth.login'), data={
        'username': 'u', 'password': 'pw'
    }, follow_redirects=True)

    # should redirect to home
    assert b'Emotify' in resp.data

# testing login POST failure
def test_login_post_fail(client, monkeypatch):
    monkeypatch.setattr('auth.users_coll.find_one', lambda q: None)
    resp = client.post(url_for('auth.login'), data={
        'username': 'x', 'password': 'y'
    }, follow_redirects=True)
    assert b'Invalid credentials' in resp.data