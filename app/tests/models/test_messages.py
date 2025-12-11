import pytest
from app import db
from app.models import User, Message


def test_private_message_flow(app):
    """
    Testuje przesyłanie wiadomości między użytkownikami.
    Poprawione dla SQLAlchemy WriteOnly configuration.
    """
    with app.app_context():
        sender = User(username='nadawca', email='n@ex.com')
        recipient = User(username='odbiorca', email='o@ex.com')
        db.session.add_all([sender, recipient])
        db.session.commit()

        msg = Message(author=sender, recipient=recipient, body='Cześć!')
        db.session.add(msg)
        db.session.commit()

        # Sprawdzenia kluczy obcych
        assert msg.sender_id == sender.id
        assert msg.recipient_id == recipient.id

        # POPRAWKA: Pobieramy wiadomości z bazy zamiast sprawdzać "in" bezpośrednio

        # 1. Sprawdzamy skrzynkę odbiorczą odbiorcy
        received_msgs = db.session.scalars(recipient.messages_received.select()).all()
        assert msg in received_msgs

        # 2. Sprawdzamy element wysłane u nadawcy
        sent_msgs = db.session.scalars(sender.messages_sent.select()).all()
        assert msg in sent_msgs