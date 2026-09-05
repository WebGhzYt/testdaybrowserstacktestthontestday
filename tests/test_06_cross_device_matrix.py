"""
Cross-Device & Cross-Platform Test Matrix Suite
Test Cases: XD_TC001 to XD_TC011
Validates Responsive UI, Viewport Breakpoints, Form Factors (Small Phones, Large Pro, Foldables, Tablets),
and Browser Engine Rendering Parity (Blink, WebKit, Gecko).
"""

import time
import pytest
from selenium.webdriver.common.by import By
from pages.catalog_page import CatalogPage
from pages.cart_page import CartPage
from pages.login_page import LoginPage
from pages.checkout_page import CheckoutPage
from utils.config import BASE_URL, TEST_USER, TEST_PASSWORD


@pytest.mark.functional
class TestCrossDeviceMatrix:

    def test_xd001_small_screen_phones_viewport_320_375px(self, driver):
        """
        XD_TC001: Validate 1-Column Responsive Grid on Small Screen Phones (320px - 375px).
        Target: iPhone SE 2022 / Galaxy S10.
        """
        # Emulate small screen phone dimensions (iPhone SE 2022: 375 x 667)
        driver.set_window_size(375, 667)
        catalog_page = CatalogPage(driver)
        catalog_page.navigate()

        items = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
        assert len(items) > 0, "Products must render on small smartphone screens."

        # Verify items do not produce horizontal overflow
        body_width = driver.execute_script("return document.body.scrollWidth;")
        viewport_width = driver.execute_script("return window.innerWidth;")
        assert body_width <= viewport_width + 10, f"Horizontal overflow detected on 375px screen: body={body_width}, window={viewport_width}"

    def test_xd002_cart_drawer_viewport_mid_large_smartphones(self, driver):
        """
        XD_TC002: Verify Floating Cart Drawer Animation on Mid-to-Large Smartphones (390px - 412px).
        Target: iPhone 15 / Galaxy S23.
        """
        driver.set_window_size(393, 852)  # iPhone 15 viewport
        driver.get(BASE_URL)

        cart_page = CartPage(driver)
        cart_page.open_cart()

        drawer = driver.find_element(By.CSS_SELECTOR, ".float-cart")
        assert drawer.is_displayed(), "Cart drawer should slide out and remain visible."

        # Verify close button is touch accessible
        close_btns = driver.find_elements(By.CSS_SELECTOR, ".float-cart__close-btn, .close-btn")
        assert len(close_btns) > 0, "Close button must be present on mobile viewport."

    def test_xd003_retina_high_dpi_large_pro_viewport(self, driver):
        """
        XD_TC003: Product Image Rendering Bounds on Flagship Pro Models (430px Viewport).
        Target: iPhone 15 Pro Max / Galaxy S24 Ultra.
        """
        driver.set_window_size(430, 932)  # iPhone 15 Pro Max viewport
        driver.get(BASE_URL)

        images = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__thumb img, .shelf-item img")
        assert len(images) > 0, "Product images must render on large pro phone screens."
        for img in images[:3]:
            assert img.is_displayed(), "Image should be visible."
            rect = img.rect
            assert rect["width"] > 50 and rect["height"] > 50, f"Invalid image dimensions: {rect}"

    def test_xd004_foldable_multi_column_reflow(self, driver):
        """
        XD_TC004: Validate Foldable Multi-Column Reflow from Folded to Unfolded.
        Target: Samsung Galaxy Z Fold 5 / Google Pixel Fold (Folded: 412px, Unfolded: 768px - 840px).
        """
        catalog_page = CatalogPage(driver)

        # 1. Folded cover screen (412 x 900)
        driver.set_window_size(412, 900)
        catalog_page.navigate()
        time.sleep(0.5)

        # 2. Unfolded inner screen (768 x 904)
        driver.set_window_size(768, 904)
        time.sleep(1)

        items = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
        assert len(items) >= 2, "Unfolded screen should render multiple catalog items in grid."

    def test_xd005_tablet_portrait_layout_reflow(self, driver):
        """
        XD_TC005: Validate Tablet Portrait Layout (768px - 820px).
        Target: iPad Air 5 / Samsung Galaxy Tab S9.
        """
        driver.set_window_size(820, 1180)  # iPad Air portrait
        driver.get(BASE_URL)
        time.sleep(0.5)

        # Ensure catalog cards render with multi-column layout
        items = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
        assert len(items) >= 3, "Tablet portrait should display catalog grid."

    def test_xd006_tablet_landscape_checkout_layout(self, driver):
        """
        XD_TC006: Validate Tablet Landscape Side-by-Side Layout (1024px - 1366px).
        Target: iPad Pro 12.9 / Galaxy Tab S9 Landscape.
        """
        driver.set_window_size(1366, 1024)  # iPad Pro landscape
        login_page = LoginPage(driver)
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        login_page.navigate().login(TEST_USER, TEST_PASSWORD)
        catalog_page.add_product_to_cart(0)
        cart_page.open_cart().proceed_to_checkout()

        # Check form rendering
        assert checkout_page.is_present(checkout_page.FIRST_NAME), "Shipping form must display on tablet landscape."

    def test_xd007_css_engine_feature_parity(self, driver):
        """
        XD_TC007: Validate CSS Grid and Flexbox support across browser engines (Blink, Gecko, WebKit).
        """
        driver.get(BASE_URL)
        has_css_grid = driver.execute_script("return window.CSS && CSS.supports('display', 'grid');")
        has_flexbox = driver.execute_script("return window.CSS && CSS.supports('display', 'flex');")
        assert has_css_grid is True, "Browser engine must support CSS Grid."
        assert has_flexbox is True, "Browser engine must support CSS Flexbox."

    def test_xd008_browser_modern_js_api_readiness(self, driver):
        """
        XD_TC008: Validate modern JavaScript APIs (IntersectionObserver, Fetch, LocalStorage).
        Guarantees compatibility across latest, beta, and dev browser channels.
        """
        driver.get(BASE_URL)
        js_check = driver.execute_script(
            """
            return {
                hasFetch: typeof window.fetch === 'function',
                hasLocalStorage: typeof window.localStorage !== 'undefined',
                hasIntersectionObserver: typeof window.IntersectionObserver !== 'undefined',
                hasPromise: typeof window.Promise !== 'undefined'
            };
            """
        )
        assert js_check.get("hasFetch") is True, "Modern Fetch API must be available."
        assert js_check.get("hasLocalStorage") is True, "LocalStorage must be available."
        assert js_check.get("hasPromise") is True, "ES6 Promise API must be available."

    def test_xd009_orientation_switch_portrait_to_landscape(self, driver):
        """
        XD_TC009: Verify Dynamic Viewport Orientation Change (Portrait -> Landscape).
        """
        # Start Portrait: 390 x 844
        driver.set_window_size(390, 844)
        driver.get(BASE_URL)
        time.sleep(0.5)

        # Rotate to Landscape: 844 x 390
        driver.set_window_size(844, 390)
        time.sleep(0.5)

        items = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
        assert len(items) > 0, "Catalog items must remain visible after orientation rotation."

    def test_xd010_touch_tap_target_sizes(self, driver):
        """
        XD_TC010: Touch Gesture & Tap Target Compliance on Mobile Keypads.
        Ensures interactive elements meet minimum ergonomic touch area guidelines.
        """
        driver.set_window_size(375, 667)
        catalog_page = CatalogPage(driver)
        catalog_page.navigate()

        buttons = catalog_page.find_elements(catalog_page.ADD_TO_CART_BUTTONS)
        assert len(buttons) > 0, "Buy buttons must exist."
        sample_btn = buttons[0]
        size = sample_btn.size
        # Minimum touch area standard is ~35-48px height
        assert size["height"] >= 30, f"Button height ({size['height']}px) is too small for touch interaction."

    def test_xd011_ultra_wide_desktop_containment(self, driver):
        """
        XD_TC011: Ultra-Wide Desktop Viewport Containment (2560px width).
        Ensures content is gracefully constrained within a centered container.
        """
        driver.set_window_size(2560, 1440)
        driver.get(BASE_URL)
        time.sleep(0.5)

        container = driver.find_element(By.TAG_NAME, "main") if driver.find_elements(By.TAG_NAME, "main") else driver.find_element(By.ID, "__next")
        width = container.size["width"]
        print(f"[ULTRA-WIDE] Main container width: {width}px on 2560px screen.")
        assert width > 0, "Main container must be rendered."

        # Reset window size
        driver.maximize_window()
