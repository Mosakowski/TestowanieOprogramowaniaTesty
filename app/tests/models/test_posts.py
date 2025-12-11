import pytest
from app import db
from app.models import User, Post
from datetime import datetime, timezone


# app/tests/models/test_posts.py

def test_post_creation_and_relationship(app):
    """
    sprawdzamy stworzenie posta oraz jego przypisywanie do autora
    """
    with app.app_context():
        u = User(username='blogger', email='blog@example.com')
        post = Post(body='heelo world', author=u, language='pl')

        db.session.add_all([u, post])
        db.session.commit()

        # sprawdzenie czy post ma autora
        assert post.author == u
        assert post.author.username == 'blogger'

        # sprawdzenie czy user ma post
        posts_query = u.posts.select()
        user_posts = db.session.scalars(posts_query).all()

        assert post in user_posts
        assert len(user_posts) == 1


def test_post_attributes(app):
    """
    testowanie atrybótów posta takich jak czas labo język
    """
    with app.app_context():
        u = User(username='tester', email='t@ex.com')
        p = Post(body='Testowanko', author=u)
        db.session.add(p)
        db.session.commit()

        assert p.id is not None
        assert isinstance(p.timestamp, datetime)
        assert '<Post' in str(p)