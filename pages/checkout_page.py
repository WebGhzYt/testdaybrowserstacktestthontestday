"""
Checkout Page Object for Shipping Details & Order Confirmation
Handles shipping form input, mandatory field validation, and order placement verification.
"""

import time
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    # Locators
    FIRST_NAME = (By.ID, "firstNameInput")
    LAST_NAME = (By.ID, "lastNameInput")
    ADDRESS = (By.ID, "addressLine1Input")
    PROVINCE = (By.ID, "provinceInput")
    POSTAL_CODE = (By.ID, "postCodeInput")
    SUBMIT_BUTTON = (By.ID, "checkout-shipping-continue")
    CONFIRMATION_MSG = (
        By.XPATH,
        "//*[contains(text(), 'Your Order has been successfully placed') or "
        "contains(@id, 'confirmation-message') or contains(@class, 'form-legend')]",
    )
    INLINE_ERRORS = (By.CSS_SELECTOR, ".error, .invalid-feedback, span[class*='error'], .field-error")
    DOWNLOAD_ORDER_PDF = (By.XPATH, "//button[contains(text(), 'Download Order Receipt')] | #downloadpdf")

    def fill_shipping_form(
        self,
        first_name: str = "Testathon",
        last_name: str = "Engineer",
        address: str = "100 Innovation Way",
        province: str = "California",
        postal_code: str = "94016",
    ):
        """Fills out shipping address form."""
        self.find_element(self.FIRST_NAME, timeout=12)
        self.type_text(self.FIRST_NAME, first_name)
        self.type_text(self.LAST_NAME, last_name)
        self.type_text(self.ADDRESS, address)
        self.type_text(self.PROVINCE, province)
        self.type_text(self.POSTAL_CODE, postal_code)
        return self

    def submit_shipping(self):
        """Clicks continue / submit button on shipping form."""
        self.click(self.SUBMIT_BUTTON)
        time.sleep(1)
        return self

    def is_order_confirmed(self, timeout=15):
        """Verifies if order confirmation banner is visible."""
        return self.is_visible(self.CONFIRMATION_MSG, timeout=timeout)

    def get_confirmation_text(self):
        """Returns confirmation text message."""
        return self.get_text(self.CONFIRMATION_MSG, timeout=10)

    def get_inline_errors(self):
        """Returns list of visible validation error texts."""
        elements = self.find_elements(self.INLINE_ERRORS)
        return [el.text.strip() for el in elements if el.is_displayed() and el.text.strip()]
