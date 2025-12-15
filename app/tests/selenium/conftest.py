import pytest
import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app import create_app, db
from config import Config


class SeleniumConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///selenium_test.db'
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope='session')
def app_server():
    """
    uruchamia serwer Flask w osobnym wątku
    """
    app = create_app(SeleniumConfig)

    with app.app_context():
        db.create_all()

    def run_server():
        app.run(port=5000, use_reloader=False)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    import time
    time.sleep(1)

    yield app

    if os.path.exists('selenium_test.db'):
        os.remove('selenium_test.db')


@pytest.fixture(scope='function')
def driver():
    """
    uruchamia przeglądarkę
    """
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    yield driver

    driver.quit()


@pytest.fixture
def base_url(app_server):
    return "http://localhost:5000"