"""
Cart Page Object for StackDemo Slide-out Drawer
Handles cart drawer operations, quantity counters, subtotal verification, and checkout trigger.
"""

import time
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CartPage(BasePage):
    # Locators
    BAG_ICON = (By.CSS_SELECTOR, ".bag, span.bag")
    CART_DRAWER = (By.CSS_SELECTOR, ".float-cart")
    CART_DRAWER_OPEN = (By.CSS_SELECTOR, ".float-cart.float-cart--open, .float-cart--open")
    BAG_QUANTITY = (By.CSS_SELECTOR, ".bag__quantity, span.bag__quantity")
    SUBTOTAL_VAL = (By.CSS_SELECTOR, ".sub-price__val, p.sub-price__val")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, ".buy-btn, .float-cart .buy-btn")
    EMPTY_CART_MESSAGE = (
        By.XPATH,
        "//*[contains(@class, 'shelf-empty') or contains(text(), 'Add some products in the cart') or contains(text(), 'Add some products in the bag')]",
    )
    CLOSE_BUTTON = (By.CSS_SELECTOR, ".float-cart__close-btn, .close-btn, div.float-cart__close-btn")
    DELETE_ITEM_BUTTONS = (By.CSS_SELECTOR, ".shelf-item__del, button.shelf-item__del")
    CART_ITEMS = (By.CSS_SELECTOR, ".float-cart .shelf-item")

    def open_cart(self):
        """Opens cart drawer by clicking floating bag icon."""
        self.click(self.BAG_ICON)
        time.sleep(0.5)
        return self

    def close_cart(self):
        """Closes cart drawer."""
        if self.is_present(self.CLOSE_BUTTON, timeout=3):
            self.click(self.CLOSE_BUTTON)
            time.sleep(0.5)
        return self

    def get_bag_quantity(self):
        """Returns integer quantity shown on the bag icon."""
        text = self.get_text(self.BAG_QUANTITY, timeout=5)
        try:
            return int(text)
        except ValueError:
            return 0

    def get_subtotal(self):
        """Returns subtotal float value (e.g. 1599.00)."""
        text = self.get_text(self.SUBTOTAL_VAL, timeout=5)
        clean = text.replace("$", "").replace(",", "").strip()
        try:
            return float(clean)
        except ValueError:
            return 0.0

    def is_empty(self):
        """Checks if cart drawer displays the empty message."""
        return self.is_visible(self.EMPTY_CART_MESSAGE, timeout=4)

    def get_empty_cart_text(self):
        """Returns empty cart notification text."""
        return self.get_text(self.EMPTY_CART_MESSAGE, timeout=5)

    def is_checkout_disabled(self):
        """Checks if checkout button is disabled or not present."""
        if not self.is_present(self.CHECKOUT_BUTTON, timeout=3):
            return True
        btn = self.find_element(self.CHECKOUT_BUTTON)
        is_disabled = (
            btn.get_attribute("disabled") is not None
            or not btn.is_enabled()
            or "disabled" in (btn.get_attribute("class") or "")
        )
        return is_disabled

    def proceed_to_checkout(self):
        """Clicks checkout button inside cart drawer."""
        self.click(self.CHECKOUT_BUTTON, timeout=10)
        time.sleep(1)
        return self

    def remove_item(self, index: int = 0):
        """Clicks delete icon on item in cart drawer."""
        del_buttons = self.find_elements(self.DELETE_ITEM_BUTTONS)
        if index < len(del_buttons):
            self.driver.execute_script("arguments[0].click();", del_buttons[index])
            time.sleep(1)
        return self
