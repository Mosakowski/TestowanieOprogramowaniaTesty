import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.tests.selenium.test_auth_flow import generate_user


# helper do szybkiego logowania w testach
def quick_login(driver, base_url, username, password):
    driver.get(f"{base_url}/auth/login")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Logout"))
    )


def test_create_post(driver, base_url):
    """
    testowanie dodawanie posta na stronie głównej.
    """
    user, email, pwd = generate_user()

    # rejestracja
    driver.get(f"{base_url}/auth/register")
    driver.find_element(By.NAME, "username").send_keys(user)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(pwd)
    driver.find_element(By.NAME, "password2").send_keys(pwd)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    # logowanie
    quick_login(driver, base_url, user, pwd)

    # dodawanie posta
    post_text = "tescik selenium hello world!"
    driver.find_element(By.NAME, "post").send_keys(post_text)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    # asercja. Czy post pojawił się na stronie?
    WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), post_text))
    assert post_text in driver.page_source


def test_edit_profile(driver, base_url):
    """
    Testuje edycję profilu
    """
    user, email, pwd = generate_user()

    # Setup użytkownika
    driver.get(f"{base_url}/auth/register")
    driver.find_element(By.NAME, "username").send_keys(user)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(pwd)
    driver.find_element(By.NAME, "password2").send_keys(pwd)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    quick_login(driver, base_url, user, pwd)

    # wejście w profil do Edytuj
    driver.get(f"{base_url}/user/{user}")
    driver.find_element(By.PARTIAL_LINK_TEXT, "Edit your profile").click()

    new_bio = "nowiutke bio."
    bio_field = driver.find_element(By.NAME, "about_me")
    bio_field.clear()
    bio_field.send_keys(new_bio)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), new_bio)
    )

    assert new_bio in driver.page_source


def test_follow_mechanism(driver, base_url):
    """
    test w którym user A obserwuje Usera B.
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # tworzenie Usera A
    user_a, email_a, pwd = generate_user()
    driver.get(f"{base_url}/auth/register")

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").send_keys(user_a)
    driver.find_element(By.NAME, "email").send_keys(email_a)
    driver.find_element(By.NAME, "password").send_keys(pwd)
    driver.find_element(By.NAME, "password2").send_keys(pwd)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(driver, 10).until(EC.url_contains("/auth/login"))
    #Tworzymy Usera B
    user_b, email_b, _ = generate_user()
    driver.get(f"{base_url}/auth/register")

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").send_keys(user_b)
    driver.find_element(By.NAME, "email").send_keys(email_b)
    driver.find_element(By.NAME, "password").send_keys(pwd)
    driver.find_element(By.NAME, "password2").send_keys(pwd)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(driver, 10).until(EC.url_contains("/auth/login"))

    quick_login(driver, base_url, user_a, pwd)

    driver.get(f"{base_url}/user/{user_b}")

    follow_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Follow']"))
    )
    follow_btn.click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//input[@value='Unfollow']"))
    )
    assert "Unfollow" in driver.page_source