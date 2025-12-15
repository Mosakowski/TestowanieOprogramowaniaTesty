import pytest
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def generate_user():
    """helper do generowania unikalnych danych"""
    uid = uuid.uuid4().hex[:6]
    return f"user_{uid}", f"user_{uid}@test.com", "Haslo123!"


def test_full_registration_and_login_flow(driver, base_url):
    """
    scenariusz:
    1 Wejdź na stronę logowania do Kliknij Register
    2 Zarejestruj nowego użytkownika
    3 Zaloguj się nowym kontem
    4 Wyloguj się.
    """
    username, email, password = generate_user()

    # strona logowania
    driver.get(f"{base_url}/auth/login")

    driver.find_element(By.PARTIAL_LINK_TEXT, "Register").click()

    # rejestracja
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password2").send_keys(password)

    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    # logowanie
    WebDriverWait(driver, 5).until(EC.url_contains("/auth/login"))

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Logout"))
    )
    # ----------------------

    assert f"Hi, {username}" in driver.page_source or "Logout" in driver.page_source

    # wylogowanie
    driver.find_element(By.PARTIAL_LINK_TEXT, "Logout").click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    assert "Sign In" in driver.page_source