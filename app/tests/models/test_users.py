import pytest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User


def test_password_security(app):
    """
    sprawdzenie haszowania haseł
    """
    u = User(username='security_test', email='sec@example.com')
    u.set_password('TajneHaslo123')

    # hasło nie może być trzymane jawnym tekstem
    assert u.password_hash != 'TajneHaslo123'
    assert u.check_password('TajneHaslo123') is True
    assert u.check_password('ZleHaslo') is False
    # edge cases
    assert u.check_password('') is False


def test_user_duplicates(app):
    """
    czy baza zablokuje dwa takie same maile/nicki
    """
    with app.app_context():
        u1 = User(username='unikalny', email='unikalny@example.com')
        db.session.add(u1)
        db.session.commit()

        #  dodanie tego samego username
        u2 = User(username='unikalny', email='inny@example.com')
        db.session.add(u2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_follow_mechanism(app):
    """
    testy operacji followingu
    """
    with app.app_context():
        barbara = User(username='barbara', email='barbara@example.com')
        jano = User(username='jano', email='jano@example.com')
        db.session.add_all([barbara, jano])
        db.session.commit()

        assert barbara.following_count() == 0
        assert jano.followers_count() == 0

        barbara.follow(jano)
        db.session.commit()

        assert barbara.is_following(jano) is True
        assert barbara.following_count() == 1
        assert jano.followers_count() == 1

        # jano nie powinien automatycznie obserwować barbary
        assert jano.is_following(barbara) is False

        # barbara przestaje obserwować janosa
        barbara.unfollow(jano)
        db.session.commit()

        assert barbara.is_following(jano) is False
        assert barbara.following_count() == 0
        assert jano.followers_count() == 0


def test_user_serialization(app):
    """
    testing metody to_dict i from_dict
    """
    with app.test_request_context():
        # from_dict (tworzenie usera z JSONa)
        data = {
            'username': 'api_user',
            'email': 'api@example.com',
            'password': 'strong_password',
            'about_me': 'test API'
        }
        user = User()
        user.from_dict(data, new_user=True)
        db.session.add(user)
        db.session.commit()

        assert user.username == 'api_user'
        assert user.check_password('strong_password')

        # test to_dict (zamiana usera na JSON)
        user_json = user.to_dict(include_email=True)

        assert user_json['username'] == 'api_user'
        assert user_json['email'] == 'api@example.com'
        assert '/api/' in user_json['_links']['self']

def test_token_generation(app):
    """
    generowanie tokenów autoryzacyjnych
    """
    with app.app_context():
        u = User(username='token_tester', email='token@example.com')
        db.session.add(u)
        db.session.commit()

        token = u.get_token()
        assert token is not None

        # czy token poprawnie identyfikuje usera
        assert User.check_token(token).id == u.id

        # sprawdź odwoływanie tokena
        u.revoke_token()
        db.session.commit()
        assert User.check_token(token) is None