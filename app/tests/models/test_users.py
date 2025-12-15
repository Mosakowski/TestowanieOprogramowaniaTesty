import pytest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User
from datetime import datetime, timezone

def test_password_success(app):
    """
    stawianie i sprawdzanie poprawnego hasła
    """
    u = User(username='security_test', email='sec@example.com')
    u.set_password('TajneHaslo123')

    assert u.password_hash != 'TajneHaslo123'
    assert u.check_password('TajneHaslo123') is True


def test_password_fail(app):
    """
    sprawdzanie błędnego hasła
    """
    u = User(username='security_fail', email='fail@example.com')
    u.set_password('DobreHaslo')

    assert u.check_password('ZleHaslo') is False
    assert u.check_password('') is False


def test_user_create_fail_duplicate_username(app):
    """
    próba dodania dwóch userów z tym samym nickiem
    """
    with app.app_context():
        u1 = User(username='unikalny', email='u1@ex.com')
        db.session.add(u1)
        db.session.commit()

        # ten sam username
        u2 = User(username='unikalny', email='u2@ex.com')
        db.session.add(u2)

        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_user_create_fail_duplicate_email(app):
    """
    próba dodania dwóch userów z tym samym mailem
    """
    with app.app_context():
        u1 = User(username='user_A', email='wspolny@ex.com')
        db.session.add(u1)
        db.session.commit()

        u2 = User(username='user_B', email='wspolny@ex.com')
        db.session.add(u2)

        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

def test_follow_success(app):
    """
    mechanizm obserwowania działa poprawnie
    """
    with app.app_context():
        barbara = User(username='barbara', email='b@ex.com')
        jano = User(username='jano', email='j@ex.com')
        db.session.add_all([barbara, jano])
        db.session.commit()

        # start: zero
        assert barbara.following_count() == 0
        assert jano.followers_count() == 0

        # barbara follow jano
        barbara.follow(jano)
        db.session.commit()

        assert barbara.is_following(jano) is True
        assert barbara.following_count() == 1
        assert jano.followers_count() == 1

        # unfollow
        barbara.unfollow(jano)
        db.session.commit()

        assert barbara.is_following(jano) is False
        assert barbara.following_count() == 0


def test_follow_fail_check(app):
    """
    FAIL: sprawdzamy czy follow nie działa w drugą stronę magicznie
    """
    with app.app_context():
        u1 = User(username='u1', email='u1@test.com')
        u2 = User(username='u2', email='u2@test.com')
        db.session.add_all([u1, u2])

        u1.follow(u2)
        db.session.commit()

        # u2 NIE powinien obserwować u1
        assert u2.is_following(u1) is False


# --- SERIALIZACJA (API helpers) ---
def test_serialization_success(app):
    """
    to_dict i from_dict działają
    """
    with app.test_request_context():
        data = {
            'username': 'api_user',
            'email': 'api@ex.com',
            'password': 'pass',
            'about_me': 'test api'
        }

        # Tworzymy usera w kontekście bazy danych
        with app.app_context():
            user = User()
            user.from_dict(data, new_user=True)

            db.session.add(user)
            db.session.commit()

            if user.last_seen is None:
                user.last_seen = datetime.now(timezone.utc)
                db.session.commit()

            assert user.username == 'api_user'
            assert user.check_password('pass')

            json_data = user.to_dict(include_email=True)

            assert json_data['username'] == 'api_user'
            assert json_data['email'] == 'api@ex.com'
            assert '_links' in json_data


def test_token_success(app):
    """
    generowanie i sprawdzanie poprawnego tokena
    """
    with app.app_context():
        u = User(username='token_ok', email='t@ex.com')
        db.session.add(u)
        db.session.commit()

        token = u.get_token()
        assert token is not None
        # sprawdzamy czy token pasuje do usera
        assert User.check_token(token).id == u.id


def test_token_fail_revoked(app):
    """
    token po odwołaniu (revoke) nie powinien działać
    """
    with app.app_context():
        u = User(username='token_bad', email='tb@ex.com')
        db.session.add(u)
        db.session.commit()

        token = u.get_token()
        # odwołujemy
        u.revoke_token()
        db.session.commit()

        # check_token powinien zwrócić None (błąd weryfikacji)
        assert User.check_token(token) is None