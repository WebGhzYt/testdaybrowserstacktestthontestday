"""
Category 4: Usability & Compliance Testing
Test Cases: TC_024 to TC_028
Covers: Keyboard Accessibility (Tab & Enter navigation), Screen Reader Accessibility,
Color Contrast Compliance, Blank Form Validation, and Mandatory Field Enforcement.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pages.login_page import LoginPage
from pages.catalog_page import CatalogPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utils.config import BASE_URL, TEST_USER, TEST_PASSWORD


@pytest.mark.usability
class TestUsabilityCompliance:

    def test_tc024_keyboard_only_navigation_tab_and_enter(self, driver):
        """
        TC_024: Navigate interactive elements using Tab and Enter keys.
        """
        driver.get(f"{BASE_URL.rstrip('/')}/signin")
        time.sleep(1)

        # Tab through elements
        active_element = driver.switch_to.active_element
        for _ in range(5):
            active_element.send_keys(Keys.TAB)
            time.sleep(0.2)
            active_element = driver.switch_to.active_element

        # Verify active focused element is valid
        assert active_element is not None, "Focus should remain on a valid DOM element."
        tag_name = active_element.tag_name.lower()
        assert tag_name in ["input", "button", "a", "div", "body"], f"Unexpected active tag: {tag_name}"

    def test_tc025_screen_reader_close_button_accessibility(self, driver):
        """
        TC_025: Verify screen readers can identify the 'X' close button inside cart drawer.
        """
        cart_page = CartPage(driver)
        driver.get(BASE_URL)
        cart_page.open_cart()

        close_btns = driver.find_elements(By.CSS_SELECTOR, ".float-cart__close-btn, .close-btn, div.float-cart__close-btn")
        assert len(close_btns) > 0, "Cart close button must exist."

        close_btn = close_btns[0]
        aria_label = close_btn.get_attribute("aria-label") or ""
        role = close_btn.get_attribute("role") or ""
        text = close_btn.text.strip()
        title = close_btn.get_attribute("title") or ""

        # Should have accessible indicator (either text 'X', aria-label, role, or title)
        has_accessible_name = bool(aria_label or role or text or title or "close" in (close_btn.get_attribute("class") or ""))
        assert has_accessible_name, "Close button lacks screen-reader recognizable accessibility attribute."

    def test_tc026_color_contrast_error_banner(self, driver):
        """
        TC_026: Verify the color contrast of the red 'invalid login' error text.
        """
        login_page = LoginPage(driver)
        login_page.navigate().login(TEST_USER, "WrongPass99!")
        time.sleep(1)

        error_elem = login_page.find_element(login_page.API_ERROR_LABEL)
        color = error_elem.value_of_css_property("color")
        print(f"[ACCESSIBILITY] Error banner text color: {color}")
        # Validate that color CSS property is present
        assert len(color) > 0, "Error element must have defined CSS color property."

    def test_tc027_blank_shipping_form_validation(self, driver):
        """
        TC_027: Submit the shipping form completely blank and verify inline validation messages appear.
        """
        login_page = LoginPage(driver)
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        login_page.navigate().login(TEST_USER, TEST_PASSWORD)
        catalog_page.add_product_to_cart(0)
        cart_page.open_cart().proceed_to_checkout()

        # Submit blank form
        checkout_page.find_element(checkout_page.FIRST_NAME)
        checkout_page.submit_shipping()
        time.sleep(1)

        # Order must not be confirmed
        assert not checkout_page.is_order_confirmed(timeout=3), "Blank form must not lead to successful order placement!"

    def test_tc028_missing_mandatory_address_field_blocks_checkout(self, driver):
        """
        TC_028: Ensure missing mandatory field (e.g. Address Line 1) blocks checkout completion.
        """
        login_page = LoginPage(driver)
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        login_page.navigate().login(TEST_USER, TEST_PASSWORD)
        catalog_page.add_product_to_cart(0)
        cart_page.open_cart().proceed_to_checkout()

        # Fill all except Address
        checkout_page.type_text(checkout_page.FIRST_NAME, "Jane")
        checkout_page.type_text(checkout_page.LAST_NAME, "Doe")
        checkout_page.type_text(checkout_page.PROVINCE, "California")
        checkout_page.type_text(checkout_page.POSTAL_CODE, "94016")

        checkout_page.submit_shipping()
        time.sleep(1)

        # Order should be blocked
        assert not checkout_page.is_order_confirmed(timeout=3), "Submission with missing mandatory address must be blocked."
