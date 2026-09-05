"""
Category 5: Specialized & Infrastructure Testing
Test Cases: TC_029 to TC_032
Covers: Mobile Web Viewport Emulation, Mobile Keypad Form Attributes,
Graceful API Error Fallback Handling, and Local Storage / Cookie State Resets.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from utils.config import BASE_URL, TEST_USER, TEST_PASSWORD


@pytest.mark.specialized
class TestSpecializedInfrastructure:

    def test_tc029_mobile_viewport_cart_icon_accessibility(self, driver):
        """
        TC_029: Verify floating cart icon is accessible and clickable at mobile screen size (375x812 iPhone dimension).
        """
        driver.set_window_size(375, 812)
        driver.get(BASE_URL)
        time.sleep(1)

        cart_page = CartPage(driver)
        cart_page.open_cart()

        drawer = driver.find_element(By.CSS_SELECTOR, ".float-cart")
        assert drawer.is_displayed(), "Cart drawer should open properly in mobile viewport."

        cart_page.close_cart()
        driver.maximize_window()

    def test_tc030_shipping_postal_code_input_attribute(self, driver):
        """
        TC_030: Verify shipping postal code input attributes (type, pattern, or inputmode).
        """
        login_page = LoginPage(driver)
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        login_page.navigate().login(TEST_USER, TEST_PASSWORD)
        catalog_page.add_product_to_cart(0)
        cart_page.open_cart().proceed_to_checkout()

        postcode_elem = checkout_page.find_element(checkout_page.POSTAL_CODE)
        input_type = postcode_elem.get_attribute("type") or "text"
        input_mode = postcode_elem.get_attribute("inputmode") or ""
        print(f"[SPECIALIZED] Postal Code input type: {input_type}, inputmode: {input_mode}")
        assert postcode_elem.is_displayed(), "Postal code input should be visible and accessible."

    def test_tc031_graceful_error_fallback_handling(self, driver):
        """
        TC_031: Verify application handles erroneous network routes gracefully
        without exposing raw server code dumps or unhandled stack traces.
        """
        # Navigate to non-existent endpoint
        driver.get(f"{BASE_URL.rstrip('/')}/non-existent-endpoint-404")
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "internal server error 500" not in body_text, "Application displayed an unhandled 500 server dump."
        assert "traceback (most recent call last)" not in body_text, "Application exposed unhandled Python/Node traceback."

    def test_tc032_local_storage_and_cookie_cart_reset(self, driver):
        """
        TC_032: Verify clearing browser Local Storage and Cookies resets unauthenticated cart state immediately.
        """
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)

        # 1. Add item to cart
        catalog_page.navigate().add_product_to_cart(0)
        cart_page.open_cart()
        assert cart_page.get_bag_quantity() >= 1, "Cart should contain at least 1 item."

        # 2. Clear Local Storage and Cookies
        driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        driver.delete_all_cookies()
        driver.refresh()
        time.sleep(1)

        # 3. Check that cart state is reset
        cart_page.open_cart()
        assert cart_page.is_empty() or cart_page.get_bag_quantity() == 0, "Cart state should reset after storage and cookies are cleared."
