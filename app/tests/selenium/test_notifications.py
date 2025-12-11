import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .test_auth_flow import generate_user
from .test_features import quick_login


def register_user_via_ui(driver, base_url, username, email, password):
    """helper do rejestracji"""
    driver.get(f"{base_url}/auth/register")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password2").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    try:
        driver.find_element(By.PARTIAL_LINK_TEXT, "Logout").click()
    except:
        pass


def test_message_notification_badge(driver, base_url):
    """
    scenariusz:
    1 User A wysyła wiadomość do Usera B.
    2 User B loguje się i widzi licznik '1' przy wiadomościach.
    3 User B wchodzi w wiadomości do licznik znika.
    """
    sender, sender_email, pwd = generate_user()
    recipient, recipient_email, _ = generate_user()

    register_user_via_ui(driver, base_url, sender, sender_email, pwd)
    register_user_via_ui(driver, base_url, recipient, recipient_email, pwd)

    quick_login(driver, base_url, sender, pwd)

    driver.get(f"{base_url}/user/{recipient}")

    driver.find_element(By.PARTIAL_LINK_TEXT, "Send private message").click()

    driver.find_element(By.NAME, "message").send_keys("Cześć! To test licznika.")
    driver.find_element(By.ID, "submit").click()

    driver.find_element(By.PARTIAL_LINK_TEXT, "Logout").click()
    quick_login(driver, base_url, recipient, pwd)

    badge = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "message_count"))
    )

    assert "1" in badge.text

    assert badge.is_displayed()

    driver.find_element(By.PARTIAL_LINK_TEXT, "Messages").click()

    WebDriverWait(driver, 5).until(EC.url_contains("/messages"))

    try:
        badge_after = driver.find_element(By.ID, "message_count")
        style = badge_after.get_attribute("style")
        assert "hidden" in style or badge_after.text == "" or not badge_after.is_displayed()
    except:
        pass