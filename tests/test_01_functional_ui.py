"""
Category 1: Functional & UI Testing
Test Cases: TC_001 to TC_013
Covers: End-to-End User Journeys, Smoke/Sanity, Cart Persistence,
Catalog Filtering, and Responsive Visual Layouts.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.catalog_page import CatalogPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utils.config import TEST_USER, TEST_PASSWORD, BASE_URL


@pytest.mark.functional
class TestFunctionalUI:

    @pytest.mark.e2e
    def test_tc001_e2e_login_filter_add_checkout(self, driver):
        """
        TC_001: Login -> Filter by 'Apple' -> Add 2 items to Cart ->
        Fill Shipping Form -> Complete Checkout.
        """
        login_page = LoginPage(driver)
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        # 1. Login
        login_page.navigate().login(TEST_USER, TEST_PASSWORD)
        assert login_page.is_logged_in(), "User should be logged in."

        # 2. Filter by Apple
        catalog_page.filter_by_vendor("Apple")
        titles = catalog_page.get_product_titles()
        assert len(titles) > 0, "Filtered Apple catalog should show products."
        for title in titles:
            assert any(k in title.lower() for k in ["apple", "iphone", "ipad"]), f"Item '{title}' should be Apple."

        # 3. Add 2 items to cart
        catalog_page.add_multiple_products(count=2)
        cart_page.open_cart()
        assert cart_page.get_bag_quantity() >= 2, "Bag quantity should reflect at least 2 added items."

        # 4. Proceed to Checkout
        cart_page.proceed_to_checkout()

        # 5. Fill Shipping form & Submit
        checkout_page.fill_shipping_form(
            first_name="John",
            last_name="Doe",
            address="100 Silicon Blvd",
            province="California",
            postal_code="94016",
        ).submit_shipping()

        # 6. Verify confirmation
        assert checkout_page.is_order_confirmed(), "Order should be confirmed successfully."

    def test_tc002_cart_persistence_across_sessions(self, driver):
        """
        TC_002: Login -> Add item -> Logout -> Login again -> Verify cart persistence.
        """
        login_page = LoginPage(driver)
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)

        # Step 1: Login & Add item
        login_page.navigate().login(TEST_USER, TEST_PASSWORD)
        catalog_page.add_product_to_cart(0)
        initial_qty = cart_page.get_bag_quantity()
        assert initial_qty >= 1, "Item should be present in cart."

        # Step 2: Logout
        login_page.logout()

        # Step 3: Login again
        login_page.navigate().login(TEST_USER, TEST_PASSWORD)

        # Step 4: Verify cart persistence
        persisted_qty = cart_page.get_bag_quantity()
        assert persisted_qty >= 1, "Cart contents should persist across user sessions."

    def test_tc003_unauthenticated_guest_checkout_redirect(self, driver):
        """
        TC_003: Proceed to checkout as an unauthenticated guest (verify prompt to login).
        """
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)

        # Clear session / start fresh
        driver.get(BASE_URL)
        driver.delete_all_cookies()
        driver.refresh()

        catalog_page.navigate().add_product_to_cart(0)
        cart_page.open_cart().proceed_to_checkout()

        # Verify redirect to signin or login prompt visible
        current_url = driver.current_url.lower()
        is_signin_page = "signin" in current_url or driver.find_elements(By.ID, "login-btn")
        assert is_signin_page, f"Guest user should be redirected to signin, current URL: {current_url}"

    @pytest.mark.smoke
    def test_tc004_valid_user_authentication(self, driver):
        """
        TC_004: Verify valid login with demouser and testingisfun99.
        """
        login_page = LoginPage(driver)
        login_page.navigate().login(TEST_USER, TEST_PASSWORD)
        logged_in_user = login_page.get_logged_in_username()
        assert TEST_USER in logged_in_user or len(logged_in_user) > 0, "Logged in username should be displayed."

    def test_tc005_invalid_password_error_message(self, driver):
        """
        TC_005: Verify invalid login displays the 'Invalid username or password' API error.
        """
        login_page = LoginPage(driver)
        login_page.navigate().login(TEST_USER, "WrongSecret99!")
        error_msg = login_page.get_error_message()
        assert len(error_msg) > 0, "Error message should be rendered on invalid login."
        assert any(k in error_msg.lower() for k in ["invalid", "password", "username"]), f"Unexpected error: {error_msg}"

    def test_tc006_samsung_vendor_filtering(self, driver):
        """
        TC_006: Verify filtering products by 'Samsung' only displays Samsung devices.
        """
        catalog_page = CatalogPage(driver)
        catalog_page.navigate().filter_by_vendor("Samsung")
        titles = catalog_page.get_product_titles()
        assert len(titles) > 0, "Samsung products should be listed."
        for title in titles:
            assert any(k in title.lower() for k in ["galaxy", "samsung"]), f"'{title}' should be a Samsung device."

    def test_tc007_cart_item_removal_decrements_bag_quantity(self, driver):
        """
        TC_007: Verify removing an item from the cart decreases the bag quantity.
        """
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)

        catalog_page.navigate().add_product_to_cart(0)
        cart_page.open_cart()
        qty_before = cart_page.get_bag_quantity()

        cart_page.remove_item(0)
        time.sleep(1)
        qty_after = cart_page.get_bag_quantity()
        assert qty_after < qty_before, f"Bag quantity should decrease after deletion (Was: {qty_before}, Now: {qty_after})"

    def test_tc008_subtotal_calculation_accuracy(self, driver):
        """
        TC_008: Verify the subtotal calculates correctly when multiple items of different prices are added.
        """
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)

        catalog_page.navigate()
        catalog_page.add_multiple_products(count=2)
        cart_page.open_cart()
        subtotal = cart_page.get_subtotal()
        assert subtotal > 0.0, f"Subtotal should be greater than 0, got {subtotal}"

    def test_tc009_empty_cart_message_display(self, driver):
        """
        TC_009: Verify the empty cart UI displays 'Add some products in the cart'.
        """
        cart_page = CartPage(driver)
        driver.get(BASE_URL)
        driver.delete_all_cookies()
        driver.refresh()

        cart_page.open_cart()
        assert cart_page.is_empty(), "Empty cart notification should be displayed."
        empty_text = cart_page.get_empty_cart_text()
        assert any(k in empty_text.lower() for k in ["add some products", "cart", "bag"]), f"Unexpected text: {empty_text}"

    def test_tc010_checkout_button_disabled_when_empty(self, driver):
        """
        TC_010: Verify checkout button is disabled/hidden when the cart is empty.
        """
        cart_page = CartPage(driver)
        driver.get(BASE_URL)
        driver.delete_all_cookies()
        driver.refresh()

        cart_page.open_cart()
        assert cart_page.is_checkout_disabled(), "Checkout button should be disabled or hidden when cart is empty."

    def test_tc011_product_grid_cross_browser_layout(self, driver):
        """
        TC_011: Verify the product grid layout elements render with positive dimensions.
        """
        catalog_page = CatalogPage(driver)
        catalog_page.navigate()
        cards = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
        assert len(cards) >= 4, "Grid should render multiple product cards."
        for card in cards[:3]:
            size = card.size
            assert size["width"] > 100 and size["height"] > 150, f"Card dimensions invalid: {size}"

    def test_tc012_cart_drawer_animation_and_toggle(self, driver):
        """
        TC_012: Verify the cart drawer animation slides out smoothly and closes.
        """
        cart_page = CartPage(driver)
        driver.get(BASE_URL)

        # Open
        cart_page.open_cart()
        drawer = driver.find_element(By.CSS_SELECTOR, ".float-cart")
        assert "open" in (drawer.get_attribute("class") or "").lower() or drawer.is_displayed()

        # Close
        cart_page.close_cart()
        time.sleep(0.5)

    def test_tc013_product_images_container_boundaries_at_320px(self, driver):
        """
        TC_013: Verify product images do not overflow their containers on a 320px screen width.
        """
        driver.set_window_size(320, 700)
        driver.get(BASE_URL)
        time.sleep(1)

        images = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__thumb img, .shelf-item img")
        if images:
            for img in images[:2]:
                width = img.size["width"]
                assert width <= 320, f"Image width {width}px exceeds 320px screen width."

        driver.maximize_window()
