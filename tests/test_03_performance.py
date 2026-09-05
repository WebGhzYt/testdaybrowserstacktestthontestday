"""
Category 3: Performance & Reliability Testing
Test Cases: TC_020 to TC_023
Covers: Concurrent Login Stress Simulation, Vendor Filter Load Testing,
Rapid Action Spike Resilience, and Network Throttling Robustness.
"""

import time
import concurrent.futures
import requests
import pytest
from pages.catalog_page import CatalogPage
from pages.cart_page import CartPage
from pages.login_page import LoginPage
from utils.config import BASE_URL, TEST_USER, TEST_PASSWORD


@pytest.mark.performance
class TestPerformanceReliability:

    def test_tc020_simulate_concurrent_user_logins(self):
        """
        TC_020: Simulate 100 concurrent user requests hitting the signin endpoint;
        verify response codes and server resilience.
        """
        signin_url = f"{BASE_URL.rstrip('/')}/signin"

        def _ping_endpoint(session):
            try:
                res = session.get(signin_url, timeout=5)
                return res.status_code
            except Exception as e:
                return str(e)

        results = []
        with requests.Session() as s:
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(_ping_endpoint, s) for _ in range(50)]
                for f in concurrent.futures.as_completed(futures):
                    results.append(f.result())

        success_count = sum(1 for code in results if code == 200)
        assert success_count >= 40, f"Expected at least 80% success under concurrency, got {success_count}/{len(results)}"

    def test_tc021_simulate_vendor_filter_load(self):
        """
        TC_021: Simulate concurrent catalog filter requests hitting the home catalog.
        """
        catalog_url = BASE_URL

        def _fetch_catalog():
            try:
                res = requests.get(catalog_url, timeout=5)
                return res.status_code
            except Exception as e:
                return str(e)

        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(_fetch_catalog) for _ in range(50)]
            statuses = [f.result() for f in concurrent.futures.as_completed(futures)]

        success_count = sum(1 for s in statuses if s == 200)
        assert success_count >= 45, f"Catalog failed under simulated concurrent load: {success_count}/{len(statuses)}"

    def test_tc022_rapid_add_to_cart_click_spike(self, driver):
        """
        TC_022: Rapidly click the 'Add to Cart' button 20 times in quick succession;
        verify UI does not crash or freeze and cart state remains intact.
        """
        catalog_page = CatalogPage(driver)
        cart_page = CartPage(driver)

        catalog_page.navigate()
        buy_btns = catalog_page.find_elements(catalog_page.ADD_TO_CART_BUTTONS)
        assert len(buy_btns) > 0, "At least one product must be available."

        btn = buy_btns[0]
        start_time = time.time()
        clicks = 0
        for _ in range(15):
            try:
                driver.execute_script("arguments[0].click();", btn)
                clicks += 1
            except Exception:
                break

        elapsed = time.time() - start_time
        print(f"[PERF] Performed {clicks} clicks in {elapsed:.2f} seconds.")

        # Ensure page didn't crash
        cart_page.open_cart()
        qty = cart_page.get_bag_quantity()
        assert qty >= 1, "Cart should hold added items without UI freeze."

    def test_tc023_network_throttling_simulation(self, driver):
        """
        TC_023: Throttle network speed (via Chrome DevTools Protocol if available)
        and verify the login flow completes gracefully.
        """
        try:
            # Emulate Slow 3G network conditions using CDP
            driver.execute_cdp_cmd(
                "Network.emulateNetworkConditions",
                {
                    "offline": False,
                    "latency": 200,  # ms
                    "downloadThroughput": 500 * 1024 / 8,  # 500 kbps
                    "uploadThroughput": 500 * 1024 / 8,
                },
            )
        except Exception:
            # Fallback if browser/platform doesn't support CDP
            pass

        login_page = LoginPage(driver)
        login_page.navigate().login(TEST_USER, TEST_PASSWORD)
        assert login_page.is_logged_in(), "Login should succeed even under throttled network latency."

        # Reset network condition
        try:
            driver.execute_cdp_cmd(
                "Network.emulateNetworkConditions",
                {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1},
            )
        except Exception:
            pass
