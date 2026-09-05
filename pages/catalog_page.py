"""
Catalog Page Object for StackDemo Product Listing
Handles vendor filtering (Apple, Samsung), product search/inspection, and adding to cart.
"""

import time
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import BASE_URL


class CatalogPage(BasePage):
    # Locators
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".shelf-item")
    PRODUCT_TITLES = (By.CSS_SELECTOR, ".shelf-item__title")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, ".shelf-item__buy-btn, div.shelf-item__buy-btn")
    PRODUCT_PRICES = (By.CSS_SELECTOR, ".val b, .val, .shelf-item__price")

    def navigate(self):
        """Navigate to catalog home page."""
        self.driver.get(BASE_URL)
        self.find_element(self.PRODUCT_CARDS, timeout=12)
        return self

    def get_product_count(self):
        """Returns total visible products count in shelf."""
        return len(self.find_elements(self.PRODUCT_CARDS))

    def get_product_titles(self):
        """Returns list of all visible product names."""
        elements = self.find_elements(self.PRODUCT_TITLES)
        return [el.text.strip() for el in elements if el.text.strip()]

    def filter_by_vendor(self, vendor: str):
        """Clicks vendor filter checkbox (e.g., 'Apple', 'Samsung')."""
        vendor_locator = (
            By.XPATH,
            f"//span[contains(@class, 'checkmark') and text()='{vendor}'] | "
            f"//div[@class='filters']//span[text()='{vendor}'] | "
            f"//label[contains(., '{vendor}')]",
        )
        self.click(vendor_locator, timeout=8)
        time.sleep(1)
        return self

    def add_product_to_cart(self, index: int = 0):
        """Clicks 'Add to cart' on product at given index."""
        buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        if index < len(buttons):
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[index])
            self.driver.execute_script("arguments[0].click();", buttons[index])
            time.sleep(1)
        else:
            raise IndexError(f"Product index {index} out of range (total {len(buttons)})")
        return self

    def add_multiple_products(self, count: int = 2):
        """Adds specified number of distinct products to cart."""
        buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        actual_to_add = min(count, len(buttons))
        for i in range(actual_to_add):
            self.add_product_to_cart(i)
            time.sleep(0.5)
        return self
