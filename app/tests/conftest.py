import pytest
from app import create_app, db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    # Wyłączamy CSRF w testach, żeby łatwiej wysyłać formularze
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    """
    Ta fixtura tworzy aplikację i konfiguruje bazę danych.
    Używamy jej, gdy w teście potrzebujemy dostępu do 'db' (np. dodawanie Usera).
    """
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app  # Tu testy działają
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Ta fixtura daje nam 'przeglądarkę' do testowania endpointów.
    Korzysta z fixtury 'app' powyżej.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Opcjonalne: runner do testowania komend CLI (jeśli będziesz potrzebował).
    """
    return app.test_cli_runner()