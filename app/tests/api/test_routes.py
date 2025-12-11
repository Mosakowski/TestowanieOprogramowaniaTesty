import pytest
from app import db
from app.models import User, Post


def test_auth_workflow(client, app):
    """
    tutaj testujemy ścieżkę użytkowanika: Rejestracja do Logowanie do Wylogowanie
    """
    # rejestracja
    response = client.post('/auth/register', data={
        'username': 'nowy_user',
        'email': 'nowy@example.com',
        'password': 'haslo123',
        'password2': 'haslo123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Congratulations' in response.data or b'Sign In' in response.data

    # sprawdzenie w bazie czy user powstał
    with app.app_context():
        u = User.query.filter_by(username='nowy_user').first()
        assert u is not None

    # logowanie
    response_login = client.post('/auth/login', data={
        'username': 'nowy_user',
        'password': 'haslo123'
    }, follow_redirects=True)

    assert response_login.status_code == 200
    # Po zalogowaniu powinniśmy widzieć opcję wylogowania lub stronę główną
    assert b'Logout' in response_login.data

    # wylogowanie
    response_logout = client.get('/auth/logout', follow_redirects=True)
    assert response_logout.status_code == 200
    assert b'Sign In' in response_logout.data


def test_login_failures(client):
    """
    sprawdzanie błędnych logowan
    """
    # Błędne hasło
    response = client.post('/auth/login', data={
        'username': 'nieistnieje',
        'password': 'zlehaslo'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_posting_on_timeline(client, app):
    """
    testing dodawania posta przez formularz
    """
    with app.app_context():
        u = User(username='blogger', email='blog@ex.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()

    client.post('/auth/login', data={'username': 'blogger', 'password': 'pass'})

    # wysłanie posta
    post_content = "testowy wpisik"
    response = client.post('/', data={'post': post_content}, follow_redirects=True)

    assert response.status_code == 200
    assert post_content.encode('utf-8') in response.data

    # walidacja: Pusty post nie powinien przejść
    response_empty = client.post('/', data={'post': ''}, follow_redirects=True)
    assert response_empty.status_code == 200


def test_user_profile_access(client, app):
    """
    Sprawdza czy strona profilu użytkownika się ładuje
    """
    with app.app_context():
        u = User(username='profiler', email='p@ex.com')
        u.set_password('test_password')
        db.session.add(u)
        db.session.commit()

    client.post('/auth/login', data={
        'username': 'profiler',
        'password': 'test_password'
    })

    response = client.get('/user/profiler')

    assert response.status_code == 200
    assert b'User: profiler' in response.data