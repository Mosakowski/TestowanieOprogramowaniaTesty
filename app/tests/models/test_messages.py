import pytest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Message


def test_message_success(app):
    #działające wysyłanie wiadomosci, wszystko gra
    with app.app_context():
        sender = User(username='nadawca', email='n@ex.com')
        recipient = User(username='odbiorca', email='o@ex.com')
        db.session.add_all([sender, recipient])
        db.session.commit()

        # tworzymy wiadomość
        msg = Message(author=sender, recipient=recipient, body='Cześć!')
        db.session.add(msg)
        db.session.commit()

        # sprawdzenia czy wszystko się zapisało
        assert msg.sender_id == sender.id
        assert msg.recipient_id == recipient.id
        assert msg.body == 'Cześć!'

        # czy widać w relacjach?
        received = db.session.scalars(recipient.messages_received.select()).all()
        assert msg in received

        sent = db.session.scalars(sender.messages_sent.select()).all()
        assert msg in sent


def test_message_fail_no_recipient(app):
    #wysylanie wiadomosci bez odbiorcy
    with app.app_context():
        u = User(username='leeee', email='s@ex.com')
        db.session.add(u)
        db.session.commit()

        # tworzymy wiadomość BEZ recipienta
        msg = Message(author=u, body='no_recipietno')
        db.session.add(msg)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


def test_message_fail_no_body(app):
    #wysyłamy pustą wiadomosc
    with app.app_context():
        sender = User(username='n2', email='n2@ex.com')
        recipient = User(username='o2', email='o2@ex.com')
        db.session.add_all([sender, recipient])
        db.session.commit()

        msg = Message(author=sender, recipient=recipient, body=None)
        db.session.add(msg)

        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()