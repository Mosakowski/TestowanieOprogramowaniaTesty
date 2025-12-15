import pytest
from app import db
from app.models import User, Post


def test_register_success(client, app):
    #poprawna rejestracja użytkownika
    response = client.post('/auth/register', data={
        'username': 'nowy_user',
        'email': 'nowy@example.com',
        'password': 'haslo123',
        'password2': 'haslo123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Congratulations' in response.data or b'Sign In' in response.data

    with app.app_context():
        assert User.query.filter_by(username='nowy_user').first() is not None


def test_register_fail_duplicate(client, app):
    #rejestracja użytkownika z zajętą nazwą
    with app.app_context():
        u = User(username='zajety', email='zajety@example.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()

    response = client.post('/auth/register', data={
        'username': 'zajety',  # duplikat
        'email': 'inny@example.com',
        'password': 'pass',
        'password2': 'pass'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'use a different username' in response.data or b'already taken' in response.data


def test_register_fail_password_mismatch(client):
    #hasla sie nie zgadzają
    response = client.post('/auth/register', data={
        'username': 'mis',
        'email': 'mis@example.com',
        'password': 'haslo_A',
        'password2': 'haslo_B'  # różne
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Field must be equal to password' in response.data or b'match' in response.data


def test_login_success(client, app):
    #poprawne logowanie
    with app.app_context():
        u = User(username='login_test', email='l@test.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()

    response = client.post('/auth/login', data={
        'username': 'login_test',
        'password': 'pass'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Logout' in response.data


def test_login_fail_wrong_password(client):
    #blędne hasło
    response = client.post('/auth/login', data={
        'username': 'nieistnieje',
        'password': 'zlehaslo'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_create_post_success(client, app):
    #dodanie posta
    with app.app_context():
        u = User(username='poster', email='post@ex.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()
    client.post('/auth/login', data={'username': 'poster', 'password': 'pass'})

    post_content = "To jest udany post"
    response = client.post('/', data={'post': post_content}, follow_redirects=True)

    assert response.status_code == 200
    assert post_content.encode('utf-8') in response.data

    with app.app_context():
        assert Post.query.filter_by(body=post_content).first() is not None


def test_create_post_fail_empty(client, app):
    #wysłanie pustego posta
    with app.app_context():
        u = User(username='empty_poster', email='e@ex.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()
    client.post('/auth/login', data={'username': 'empty_poster', 'password': 'pass'})

    response = client.post('/', data={'post': ''}, follow_redirects=True)

    assert response.status_code == 200
    assert b'This field is required' in response.data or b'error' in response.data


def test_profile_access_success(client, app):
    #wejscie na profil będąc zalogowanym
    with app.app_context():
        u = User(username='profiler', email='p@ex.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()

    client.post('/auth/login', data={'username': 'profiler', 'password': 'pass'})

    response = client.get('/user/profiler')
    assert response.status_code == 200
    assert b'User: profiler' in response.data


def test_profile_fail_404(client, app):
    #wejscie na profil nieistniejącego usera
    with app.app_context():
        u = User(username='szukacz', email='s@ex.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()
    client.post('/auth/login', data={'username': 'szukacz', 'password': 'pass'})

    response = client.get('/user/niemago')

    assert response.status_code == 404


def test_access_fail_unauthorized(client):
    #wejscie na strone zabezpieczoną bez logowania
    response = client.get('/index', follow_redirects=True)

    assert response.status_code == 200
    assert b'Sign In' in response.data
    assert b'auth/login' in response.request.url.encode('utf-8')

def test_follow_fail_self(client, app):
    #follow dla samego siebie
    with app.app_context():
        u = User(username='cos', email='l@ex.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()

    client.post('/auth/login', data={'username': 'cos', 'password': 'pass'})

    # Próba followowania samego siebie
    response = client.post('/follow/cos', follow_redirects=True)

    assert response.status_code == 200
    assert b'You cannot follow yourself' in response.data