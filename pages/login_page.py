"""
Login Page Object for StackDemo Authentication
Handles React-Select dropdowns, credential entry, error banner extraction, and logout.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pages.base_page import BasePage
from utils.config import BASE_URL


class LoginPage(BasePage):
    # Locators
    SIGNIN_NAV_LINK = (By.CSS_SELECTOR, "#signin, a[href*='signin'], #Sign-in")
    USERNAME_DROPDOWN = (By.ID, "username")
    PASSWORD_DROPDOWN = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")
    LOGGED_IN_USER_LABEL = (By.CSS_SELECTOR, ".username, span.username")
    API_ERROR_LABEL = (By.CSS_SELECTOR, ".api-error, h3.api-error, div[class*='api-error'], .form-error")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "#logout, a[href*='logout']")

    def navigate(self):
        """Navigate to login page directly or via header link."""
        self.driver.get(BASE_URL)
        if self.is_present(self.SIGNIN_NAV_LINK, timeout=5):
            self.click(self.SIGNIN_NAV_LINK)
        else:
            self.driver.get(f"{BASE_URL.rstrip('/')}/signin")
        self.find_element(self.LOGIN_BUTTON)
        return self

    def login(self, username: str, password: str):
        """Selects username and password in React-Select dropdowns and clicks Login."""
        # 1. Select Username
        user_container = self.find_element(self.USERNAME_DROPDOWN)
        user_container.click()
        time.sleep(0.3)

        try:
            user_opt = self.driver.find_element(
                By.XPATH, f"//*[contains(@id, 'react-select') and text()='{username}']"
            )
            user_opt.click()
        except NoSuchElementException:
            try:
                user_input = user_container.find_element(By.TAG_NAME, "input")
                user_input.send_keys(username)
                user_input.send_keys(Keys.ENTER)
            except Exception:
                # Direct injection fallback
                self.driver.execute_script(
                    "arguments[0].innerText = arguments[1];", user_container, username
                )

        time.sleep(0.3)

        # 2. Select Password
        pwd_container = self.find_element(self.PASSWORD_DROPDOWN)
        pwd_container.click()
        time.sleep(0.3)

        try:
            pwd_opt = self.driver.find_element(
                By.XPATH, f"//*[contains(@id, 'react-select') and text()='{password}']"
            )
            pwd_opt.click()
        except NoSuchElementException:
            try:
                pwd_input = pwd_container.find_element(By.TAG_NAME, "input")
                pwd_input.send_keys(password)
                pwd_input.send_keys(Keys.ENTER)
            except Exception:
                self.driver.execute_script(
                    "arguments[0].innerText = arguments[1];", pwd_container, password
                )

        time.sleep(0.3)

        # 3. Click Login Button
        self.click(self.LOGIN_BUTTON)
        time.sleep(1)
        return self

    def get_logged_in_username(self):
        """Returns the username displayed after successful login."""
        return self.get_text(self.LOGGED_IN_USER_LABEL, timeout=10)

    def is_logged_in(self):
        """Checks if a user is currently logged in."""
        return self.is_visible(self.LOGGED_IN_USER_LABEL, timeout=8)

    def get_error_message(self):
        """Extracts the API error banner on invalid login."""
        return self.get_text(self.API_ERROR_LABEL, timeout=8)

    def logout(self):
        """Logs out current user."""
        if self.is_present(self.LOGOUT_BUTTON, timeout=5):
            self.click(self.LOGOUT_BUTTON)
            time.sleep(1)
