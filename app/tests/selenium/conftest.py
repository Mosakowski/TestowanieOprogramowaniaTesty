import pytest
import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app import create_app, db
from config import Config


# Konfiguracja pod testy E2E - używamy pliku bazy danych, a nie pamięci RAM,
# żeby wątek serwera i wątek testu widziały te same dane.
class SeleniumConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///selenium_test.db'
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope='session')
def app_server():
    """
    Uruchamia serwer Flask w osobnym wątku.
    Dzięki temu testy mogą łączyć się z localhost:5000.
    """
    app = create_app(SeleniumConfig)

    # Tworzymy czystą bazę pod testy
    with app.app_context():
        db.create_all()

    # Funkcja uruchamiająca serwer
    def run_server():
        # Uruchamiamy na porcie 5000, wyłączamy reloader (ważne przy wątkach)
        app.run(port=5000, use_reloader=False)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Dajemy chwilę na start serwera (opcjonalne, ale bezpieczne)
    import time
    time.sleep(1)

    yield app

    # Po testach sprzątamy plik bazy danych
    if os.path.exists('selenium_test.db'):
        os.remove('selenium_test.db')


@pytest.fixture(scope='function')
def driver():
    """
    Uruchamia przeglądarkę Chrome.
    """
    options = Options()
    # options.add_argument("--headless") # Odkomentuj, jeśli nie chcesz widzieć okna
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)  # Czekaj max 5 sekund na elementy

    yield driver

    driver.quit()


@pytest.fixture
def base_url(app_server):
    return "http://localhost:5000"