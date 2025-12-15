import pytest
import base64
from app import db
from app.models import User

#helpery

def get_api_headers(token):
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def get_token(client, username, password):
    # do basicAuth
    auth_str = f"{username}:{password}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    response = client.post('/api/tokens', headers={
        'Authorization': f'Basic {b64_auth}'
    })
    if response.status_code == 200:
        return response.json['token']
    return None


def test_get_user_success(client, app):
    # pobieranie istniejącego usera
    with app.app_context():
        u = create_user('janek', 'janek@test.pl', 'haslo')
        user_id = u.id
        token = u.get_token()
        db.session.commit()

    headers = get_api_headers(token)
    response = client.get(f'/api/users/{user_id}', headers=headers)

    assert response.status_code == 200
    assert response.json['username'] == 'janek'


def test_get_user_fail_404(client, app):
    #pobranie usera który nie istnieje
    with app.app_context():
        u = create_user('admin', 'admin@test.pl', 'haslo')
        token = u.get_token()
        db.session.commit()

    headers = get_api_headers(token)
    response = client.get('/api/users/9999', headers=headers)

    assert response.status_code == 404


def test_create_user_success(client, app):
    #poprawna rejestracja przez API
    payload = {
        'username': 'nowy_api',
        'email': 'nowy@api.com',
        'password': 'has4lko'
    }
    response = client.post('/api/users', json=payload)

    assert response.status_code == 201
    assert response.json['username'] == 'nowy_api'

    with app.app_context():
        assert User.query.filter_by(username='nowy_api').first() is not None


def test_create_user_fail_missing_data(client):
    #brak hasla w zapytaniu
    payload = {
        'username': 'bezhasla',
        'email': 'brak@api.com'
    }
    response = client.post('/api/users', json=payload)

    assert response.status_code == 400
    assert 'message' in response.json


def test_create_user_fail_duplicate(client, app):
    #resejstracja z zajętym emailme
    with app.app_context():
        create_user('stary', 'zajety@email.com', 'pass')
    payload = {
        'username': 'inny_nick',
        'email': 'zajety@email.com',
        'password': 'pass'
    }

    response = client.post('/api/users', json=payload)
    assert response.status_code == 400

def test_get_token_success(client, app):
    #pobieranie token z dobrym hasłem
    with app.app_context():
        create_user('tokenowiec', 'tm@test.pl', 'dobre_haslo')

    token = get_token(client, 'tokenowiec', 'dobre_haslo')
    assert token is not None
    assert isinstance(token, str)


def test_get_token_fail_wrong_password(client, app):
    #pobranie tokena z złym hasłem
    with app.app_context():
        create_user('hacker', 'hack@test.pl', 'dobre_haslo')

    auth_str = "hacker:zle_haslo"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    response = client.post('/api/tokens', headers={
        'Authorization': f'Basic {b64_auth}'
    })

    assert response.status_code == 401


def test_update_user_success(client, app):
    #edycja profilu
    with app.app_context():
        u = create_user('edytor', 'edycja@test.pl', 'pass')
        user_id = u.id

    token = get_token(client, 'edytor', 'pass')
    headers = get_api_headers(token)
    response = client.put(f'/api/users/{user_id}', json={'about_me': 'Nowe bio'}, headers=headers)

    assert response.status_code == 200
    assert response.json['about_me'] == 'Nowe bio'


def test_update_user_fail_unauthorized(client, app):
    #edytowanie bez tokena
    with app.app_context():
        u = create_user('bezpieczny', 'bez@test.pl', 'pass')
        user_id = u.id

    response = client.put(f'/api/users/{user_id}', json={'about_me': 'Hacked'})
    assert response.status_code == 401


def test_get_users_list_success(client, app):
    #sprawdzenie listy użytkowników
    with app.app_context():
        u1 = create_user('list_user1', 'l1@test.pl', 'pass')
        create_user('list_user2', 'l2@test.pl', 'pass')
        token = u1.get_token()
        db.session.commit()

    headers = get_api_headers(token)
    response = client.get('/api/users', headers=headers)

    assert response.status_code == 200
    assert 'items' in response.json
    assert len(response.json['items']) >= 2


def test_update_other_user_forbidden(client, app):
    #edytowanie cudzego profilu
    with app.app_context():
        attacker = create_user('hackingman', 'hack@zly.pl', 'pass')
        victim = create_user('hackedman', 'hackerd@ok.pl', 'pass')

        attacker_token = attacker.get_token()
        db.session.commit()
        victim_id = victim.id

    headers = get_api_headers(attacker_token)

    response = client.put(f'/api/users/{victim_id}',
                          json={'about_me': 'HACKED!'},
                          headers=headers)

    assert response.status_code == 403


def test_create_user_empty_json(client):
    #pusty JSON
    response = client.post('/api/users', json={})
    assert response.status_code == 400


def test_wrong_method_405(client):
    #użycie złej metody HTTp
    response = client.delete('/api/users')
    assert response.status_code == 405


def test_get_user_invalid_id_type(client, app):
    #złe ID
    with app.app_context():
        u = create_user('test_id', 'id@test.pl', 'pass')
        token = u.get_token()
        db.session.commit()

    headers = get_api_headers(token)
    response = client.get('/api/users/abc', headers=headers)

    assert response.status_code == 404