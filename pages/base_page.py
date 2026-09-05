"""
Base Page Object Model Class
Provides robust element interactions, explicit waits, and JavaScript fallbacks.
"""

import logging
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from utils.config import REPORTS_DIR

logger = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def find_element(self, locator, timeout=None):
        """Wait for element presence and return it."""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def find_visible_element(self, locator, timeout=None):
        """Wait for element visibility and return it."""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def find_elements(self, locator, timeout=None):
        """Wait for at least one element presence and return list."""
        try:
            wait = WebDriverWait(self.driver, timeout or self.timeout)
            wait.until(EC.presence_of_element_located(locator))
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def click(self, locator, timeout=None):
        """Clicks element with scroll-into-view and JavaScript fallback."""
        element = self.find_element(locator, timeout)
        self.scroll_to_element(element)
        try:
            clickable = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(locator)
            )
            clickable.click()
        except (ElementClickInterceptedException, TimeoutException, StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", element)
        return element

    def type_text(self, locator, text, clear=True, timeout=None):
        """Types text into an input field with optional clearing."""
        element = self.find_element(locator, timeout)
        if clear:
            try:
                element.clear()
            except Exception:
                pass
        element.send_keys(text)
        return element

    def get_text(self, locator, timeout=None):
        """Returns visible text of an element."""
        try:
            element = self.find_element(locator, timeout)
            return element.text.strip()
        except TimeoutException:
            return ""

    def is_visible(self, locator, timeout=5):
        """Checks if an element is visible on screen within timeout."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def is_present(self, locator, timeout=3):
        """Checks if element is present in DOM."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def scroll_to_element(self, element):
        """Scrolls element into center of viewport."""
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
                element,
            )
        except Exception:
            pass

    def take_screenshot(self, name="screenshot"):
        """Saves screenshot to reports/screenshots/."""
        screenshots_dir = REPORTS_DIR / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        file_path = screenshots_dir / f"{name}.png"
        self.driver.save_screenshot(str(file_path))
        return str(file_path)
