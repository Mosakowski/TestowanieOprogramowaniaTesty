import pytest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Post
from datetime import datetime


def test_post_success_creation(app):
    """
    sprawdzamy poprawne stworzenie posta i relację z autorem
    """
    with app.app_context():
        u = User(username='blogger', email='blog@example.com')
        # Tworzymy post przypisany do usera
        post = Post(body='hello world', author=u, language='pl')

        db.session.add_all([u, post])
        db.session.commit()

        # sprawdzenie czy post ma autora
        assert post.author == u
        assert post.author.username == 'blogger'

        assert post.author_id == u.id
        assert post.id is not None


def test_post_success_attributes(app):
    """
    testowanie atrybutów posta takich jak czas (timestamp)
    """
    with app.app_context():
        u = User(username='tester', email='t@ex.com')
        p = Post(body='Testowanko', author=u)
        db.session.add(p)
        db.session.commit()

        assert p.id is not None
        assert isinstance(p.timestamp, datetime)
        assert '<Post' in str(p)


def test_post_fail_no_author(app):
    """
    próba stworzenia posta bez autora (powinien być błąd bazy)
    """
    with app.app_context():
        p = Post(body="Post sierotka")

        db.session.add(p)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


def test_post_fail_null_body(app):
    """
    Fpróba stworzenia posta z pustą treścią
    """
    with app.app_context():
        u = User(username='cosiek', email='m@ex.com')
        db.session.add(u)
        db.session.commit()

        p = Post(author=u, body=None)  # Brak treści
        db.session.add(p)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()