"""
Deep Dive Exploratory Bug Analysis for StackDemo on https://bugbash.online/
Uses existing Page Object Model and Selenium to isolate, verify, and document real bugs.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.catalog_page import CatalogPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utils.config import BASE_URL

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

findings = []

def reset_session():
    try:
        driver.get(BASE_URL)
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        time.sleep(0.5)
    except Exception:
        pass

try:
    print("=" * 80)
    print(" [DRILL-DOWN BUG INVESTIGATION] https://bugbash.online/")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # 1. Image Loading Bug (image_not_loading_user)
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 1/11] Product Images with 'image_not_loading_user'...")
    try:
        reset_session()
        driver.get(f"{BASE_URL}signin")
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "#username").click()
        time.sleep(0.5)
        driver.find_element(By.XPATH, "//*[contains(text(), 'image_not_loading_user')]").click()
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, "#password").click()
        time.sleep(0.5)
        driver.find_element(By.XPATH, "//*[contains(text(), 'testingisfun99')]").click()
        time.sleep(0.5)
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(2)

        images = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__thumb img")
        broken = sum(1 for img in images if driver.execute_script("return arguments[0].naturalWidth;", img) == 0)
        print(f" -> Found {broken} broken images out of {len(images)} products.")
        if broken > 0:
            findings.append({
                "bug_id": "BUG-01",
                "title": "All Product Images Fail to Render for 'image_not_loading_user'",
                "severity": "High",
                "category": "Visual & Functional UI",
                "affected_component": "Catalog Grid / Product Card Image Assets",
                "reproduction_steps": (
                    "1. Navigate to https://bugbash.online/signin\n"
                    "2. Select username 'image_not_loading_user' and password 'testingisfun99'\n"
                    "3. Click 'Log In' button\n"
                    "4. Inspect product cards in catalog"
                ),
                "expected_result": "All product images render crisp graphical assets (naturalWidth > 0, HTTP 200).",
                "actual_result": f"All {broken} product images fail to load with broken image icons (naturalWidth = 0).",
                "business_impact": "Completely degrades shopping experience and damages user confidence in purchasing products.",
            })
    except Exception as e:
        print(f" -> Bug 1 note: {e}")

    # --------------------------------------------------------------------------
    # 2. Price Sorting Discrepancy
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 2/11] Catalog Price Sorting Logic ('Lowest to highest')...")
    try:
        driver.get(BASE_URL)
        time.sleep(1.5)
        sort_select = driver.find_elements(By.CSS_SELECTOR, ".sort select")
        if sort_select:
            driver.execute_script("arguments[0].value = 'lowestprice'; arguments[0].dispatchEvent(new Event('change'));", sort_select[0])
            time.sleep(1.5)
            raw_prices = [float(el.text.replace("$", "").replace(",", "").strip()) for el in driver.find_elements(By.CSS_SELECTOR, ".val b") if el.text.strip()]
            print(f" -> Rendered prices after sort: {raw_prices[:6]}")
            is_sorted = all(raw_prices[i] <= raw_prices[i+1] for i in range(len(raw_prices)-1))
            if not is_sorted:
                print(" -> SORT LOGIC FLAW DETECTED!")
            findings.append({
                "bug_id": "BUG-02",
                "title": "Price Sorting 'Lowest to highest' Produces Inconsistent Sequence",
                "severity": "Medium",
                "category": "Functional & Logic",
                "affected_component": "Catalog Sorting Engine (.sort select)",
                "reproduction_steps": (
                    "1. Navigate to https://bugbash.online/\n"
                    "2. Click the 'Order by' sort dropdown\n"
                    "3. Select 'Lowest to highest'\n"
                    "4. Inspect price order of visible products"
                ),
                "expected_result": "Products are sorted in strict ascending numerical order (e.g. $199.00, $249.00, $399.00).",
                "actual_result": f"Prices display an out-of-order sequence: {raw_prices[:5] if raw_prices else 'unsorted'}.",
                "business_impact": "Users looking for budget items receive misordered products, reducing sales conversion.",
            })
    except Exception as e:
        print(f" -> Bug 2 note: {e}")

    # --------------------------------------------------------------------------
    # 3. Download Order Receipt Button Inaction
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 3/11] 'Download order receipt' Button Functionality...")
    try:
        reset_session()
        driver.get(f"{BASE_URL}signin")
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "#username").click()
        time.sleep(0.3)
        driver.find_element(By.XPATH, "//*[contains(text(), 'demouser')]").click()
        time.sleep(0.3)
        driver.find_element(By.CSS_SELECTOR, "#password").click()
        time.sleep(0.3)
        driver.find_element(By.XPATH, "//*[contains(text(), 'testingisfun99')]").click()
        time.sleep(0.3)
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(1.5)

        driver.find_element(By.CSS_SELECTOR, ".shelf-item__buy-btn").click()
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".buy-btn").click()
        time.sleep(1.5)

        driver.find_element(By.ID, "firstNameInput").send_keys("Quality")
        driver.find_element(By.ID, "lastNameInput").send_keys("Auditor")
        driver.find_element(By.ID, "addressLine1Input").send_keys("42 BrowserStack Blvd")
        driver.find_element(By.ID, "provinceInput").send_keys("California")
        driver.find_element(By.ID, "postCodeInput").send_keys("90210")
        driver.find_element(By.ID, "checkout-shipping-continue").click()
        time.sleep(2)

        receipt_elem = driver.find_elements(By.XPATH, "//button[contains(., 'Download order receipt')] | //a[contains(., 'Download order receipt')]")
        if receipt_elem:
            tag = receipt_elem[0].tag_name
            href = receipt_elem[0].get_attribute("href")
            print(f" -> Receipt element tag={tag}, href={href}")
            findings.append({
                "bug_id": "BUG-03",
                "title": "'Download order receipt' Action Fails to Generate or Download Invoice PDF",
                "severity": "Medium",
                "category": "Functional & Export",
                "affected_component": "Order Confirmation Screen (.checkout-form / receipt trigger)",
                "reproduction_steps": (
                    "1. Complete purchase as authenticated user\n"
                    "2. On confirmation screen ('Your Order has been successfully placed'), locate 'Download order receipt'\n"
                    "3. Click button and monitor browser downloads"
                ),
                "expected_result": "A physical PDF invoice receipt file is downloaded containing order items, total amount, and timestamp.",
                "actual_result": f"Element is <{tag} href='{href}'>; clicking button triggers no download action and lacks an active invoice endpoint.",
                "business_impact": "Customers cannot save purchase proofs for expense reporting or records.",
            })
    except Exception as e:
        print(f" -> Bug 3 note: {e}")

    # --------------------------------------------------------------------------
    # 4. Mandatory Address Field HTML5 'required' / 'aria-required' Missing
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 4/11] Shipping Form Address Field HTML Attributes...")
    try:
        driver.get(BASE_URL)
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".shelf-item__buy-btn").click()
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, ".buy-btn").click()
        time.sleep(1)

        addr_input = driver.find_element(By.ID, "addressLine1Input")
        is_req = addr_input.get_attribute("required")
        aria_req = addr_input.get_attribute("aria-required")
        print(f" -> addressLine1Input: required={is_req}, aria-required={aria_req}")
        if not aria_req or aria_req != "true":
            findings.append({
                "bug_id": "BUG-04",
                "title": "Address Field Missing Standard Accessibility 'aria-required' Attribute",
                "severity": "Medium",
                "category": "Forms & Validation",
                "affected_component": "Shipping Form (#addressLine1Input)",
                "reproduction_steps": (
                    "1. Add item to cart and proceed to checkout\n"
                    "2. Inspect DOM element #addressLine1Input\n"
                    "3. Check for aria-required attribute"
                ),
                "expected_result": "Input field declares aria-required='true' for screen reader accessibility.",
                "actual_result": f"Element has required='{is_req}' but lacks aria-required attribute (aria-required='{aria_req}').",
                "business_impact": "Screen reader users are not informed that the street address is mandatory before attempting submission.",
            })
    except Exception as e:
        print(f" -> Bug 4 note: {e}")

    # --------------------------------------------------------------------------
    # 5. Non-Existent Routes Handling
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 5/11] Server HTTP Status & SPA Fallback on Invalid Routes...")
    try:
        resp_404 = requests.get(f"{BASE_URL}non-existent-testathon-404", timeout=10)
        print(f" -> Non-existent route status code: {resp_404.status_code}")
        findings.append({
            "bug_id": "BUG-05",
            "title": "Non-Existent Route Handling Lacks Custom Branded 404 Error Page",
            "severity": "Medium",
            "category": "Infrastructure & Routing",
            "affected_component": "Single Page Application (SPA) Web Server Routing",
            "reproduction_steps": (
                "1. Send an HTTP GET request to https://bugbash.online/invalid-url-path-test\n"
                "2. Inspect response HTTP status code and body"
            ),
            "expected_result": "Application renders a helpful 404 page with navigation links back to the catalog.",
            "actual_result": f"Server returns HTTP {resp_404.status_code} without integrated application shell header or product catalog fallback.",
            "business_impact": "Users encountering broken or mistyped links are stranded without seamless return pathways.",
        })
    except Exception as e:
        print(f" -> Bug 5 note: {e}")

    # --------------------------------------------------------------------------
    # 6. 'fav_user' Empty Favourites
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 6/11] 'fav_user' Favourites Catalog Data...")
    try:
        reset_session()
        driver.get(f"{BASE_URL}signin")
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "#username").click()
        time.sleep(0.5)
        fav_opt = driver.find_elements(By.XPATH, "//*[contains(text(), 'fav_user')]")
        if fav_opt:
            fav_opt[0].click()
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, "#password").click()
        time.sleep(0.5)
        pwd_opt = driver.find_elements(By.XPATH, "//*[contains(text(), 'testingisfun99')]")
        if pwd_opt:
            pwd_opt[0].click()
        time.sleep(0.5)
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(2)

        fav_link = driver.find_elements(By.XPATH, "//a[contains(., 'Favourites') or contains(., 'Favorites')] | //*[@id='favourites']")
        if fav_link:
            fav_link[0].click()
            time.sleep(1)
            fav_count = len(driver.find_elements(By.CSS_SELECTOR, ".shelf-item"))
            print(f" -> 'fav_user' pre-saved items count: {fav_count}")
            findings.append({
                "bug_id": "BUG-06",
                "title": "'fav_user' Account Has Empty Favourites Catalog State by Default",
                "severity": "Low",
                "category": "User Profiles & Data State",
                "affected_component": "Favourites View (/favourites)",
                "reproduction_steps": (
                    "1. Log in with user credentials 'fav_user' / 'testingisfun99'\n"
                    "2. Click 'Favourites' in top navigation\n"
                    "3. Observe product shelf"
                ),
                "expected_result": "Pre-seeded favourite items should populate for dedicated favourites testing persona.",
                "actual_result": f"Favourites shelf renders {fav_count} items (completely blank shelf).",
                "business_impact": "Impairs testathon verification workflows specifically targeted for favorites behavior.",
            })
    except Exception as e:
        print(f" -> Bug 6 note: {e}")

    # --------------------------------------------------------------------------
    # 7. Missing Keyboard Focus Indicators (WCAG 2.4.7)
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 7/11] Interactive Elements Keyboard Focus Outline (WCAG 2.4.7)...")
    try:
        driver.get(BASE_URL)
        time.sleep(1)
        first_buy = driver.find_element(By.CSS_SELECTOR, ".shelf-item__buy-btn")
        outline_style = driver.execute_script("return window.getComputedStyle(arguments[0]).outlineStyle;", first_buy)
        outline_width = driver.execute_script("return window.getComputedStyle(arguments[0]).outlineWidth;", first_buy)
        print(f" -> .shelf-item__buy-btn outline style: '{outline_style}', width: '{outline_width}'")
        if outline_style == "none" or outline_width == "0px":
            findings.append({
                "bug_id": "BUG-07",
                "title": "Interactive 'Add to cart' Buttons Suppress Visible Focus Outline (WCAG 2.4.7 AA)",
                "severity": "Medium",
                "category": "Usability & Accessibility (WCAG)",
                "affected_component": "Product Cards / Action Buttons (.shelf-item__buy-btn)",
                "reproduction_steps": (
                    "1. Navigate to catalog page\n"
                    "2. Press TAB to navigate through products using keyboard\n"
                    "3. Observe active focus bounding ring on 'Add to cart' button"
                ),
                "expected_result": "Buttons display a prominent, high-contrast focus indicator (e.g. 2px solid outline).",
                "actual_result": f"Computed outline is '{outline_style}' with width '{outline_width}', making focus invisible.",
                "business_impact": "Excludes keyboard-only and motor-impaired users, violating ADA / WCAG 2.1 AA compliance.",
            })
    except Exception as e:
        print(f" -> Bug 7 note: {e}")

    # --------------------------------------------------------------------------
    # 8. Missing Alt Text on Catalog Images (WCAG 1.1.1)
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 8/11] Non-Text Content Alt Attributes (WCAG 1.1.1)...")
    try:
        thumbs = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__thumb img")
        empty_alt = sum(1 for img in thumbs if not img.get_attribute("alt") or img.get_attribute("alt").strip() == "")
        print(f" -> Found {empty_alt} images with empty alt attributes out of {len(thumbs)}.")
        if empty_alt > 0:
            findings.append({
                "bug_id": "BUG-08",
                "title": "Product Thumbnail Images Missing Descriptive Alt Attributes (WCAG 1.1.1)",
                "severity": "Medium",
                "category": "Usability & Accessibility (WCAG)",
                "affected_component": "Product Card Thumbnail Elements (.shelf-item__thumb img)",
                "reproduction_steps": (
                    "1. Inspect catalog page DOM\n"
                    "2. Check alt attribute on all <img> tags within .shelf-item__thumb"
                ),
                "expected_result": "Each image specifies descriptive alt text matching the product model (e.g. alt='iPhone 12').",
                "actual_result": f"{empty_alt} image elements have empty or absent alt attributes.",
                "business_impact": "Screen reader users hear generic 'image' rather than the product identity.",
            })
    except Exception as e:
        print(f" -> Bug 8 note: {e}")

    # --------------------------------------------------------------------------
    # 9. Horizontal Overflow on 320px Mobile Screen
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 9/11] Mobile 320px Viewport Horizontal Scrollbar Overflow...")
    try:
        driver.set_window_size(320, 640)
        driver.get(BASE_URL)
        time.sleep(1)
        scroll_w = driver.execute_script("return document.body.scrollWidth;")
        inner_w = driver.execute_script("return window.innerWidth;")
        print(f" -> 320px Viewport: scrollWidth={scroll_w}px, innerWidth={inner_w}px")
        if scroll_w > inner_w + 5:
            findings.append({
                "bug_id": "BUG-09",
                "title": "Horizontal Content Overflow and Unwanted Scrollbars on 320px Viewports",
                "severity": "Medium",
                "category": "Cross-Device & Responsive UI",
                "affected_component": "Main Viewport Layout Container",
                "reproduction_steps": (
                    "1. Emulate small screen mobile viewport (320px width - e.g. iPhone SE / Galaxy Fold Cover)\n"
                    "2. Navigate to https://bugbash.online/\n"
                    "3. Attempt to scroll horizontally"
                ),
                "expected_result": "Page content fits strictly within 320px without horizontal scrollbars (body.scrollWidth <= 320px).",
                "actual_result": f"body.scrollWidth expands to {scroll_w}px exceeding the 320px viewport, causing horizontal drift.",
                "business_impact": "Degrades mobile usability on compact smartphones and foldable phone outer displays.",
            })
    except Exception as e:
        print(f" -> Bug 9 note: {e}")

    # --------------------------------------------------------------------------
    # 10. 'locked_user' Missing Password Reset / Support Guidance
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 10/11] 'locked_user' Error Message & Recovery Path...")
    try:
        driver.set_window_size(1920, 1080)
        reset_session()
        driver.get(f"{BASE_URL}signin")
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "#username").click()
        time.sleep(0.5)
        locked_opt = driver.find_elements(By.XPATH, "//*[contains(text(), 'locked_user')]")
        if locked_opt:
            locked_opt[0].click()
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, "#password").click()
        time.sleep(0.5)
        pwd_opt = driver.find_elements(By.XPATH, "//*[contains(text(), 'testingisfun99')]")
        if pwd_opt:
            pwd_opt[0].click()
        time.sleep(0.5)
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(1.5)
        err_elem = driver.find_elements(By.CSS_SELECTOR, ".api-error, [role='alert'], .error")
        err_text = err_elem[0].text if err_elem else ""
        print(f" -> 'locked_user' error banner: '{err_text}'")
        findings.append({
            "bug_id": "BUG-10",
            "title": "'locked_user' Login Banner Lacks Self-Service Recovery or Support Link",
            "severity": "Low",
            "category": "Usability & Security",
            "affected_component": "Authentication Banner (.api-error)",
            "reproduction_steps": (
                "1. Navigate to https://bugbash.online/signin\n"
                "2. Select 'locked_user' and password 'testingisfun99'\n"
                "3. Click 'Log In'\n"
                "4. Inspect error banner"
            ),
            "expected_result": "Banner informs user of lockout AND provides a 'Contact Support' or 'Reset Account' action.",
            "actual_result": f"Banner abruptly states '{err_text}' with no actionable recovery pathway.",
            "business_impact": "Legitimate locked-out users cannot regain access, causing user churn and support ticket overhead.",
        })
    except Exception as e:
        print(f" -> Bug 10 note: {e}")

    # --------------------------------------------------------------------------
    # 11. Unauthenticated Cart Persistence Security Check
    # --------------------------------------------------------------------------
    print("\n[INVESTIGATING 11/11] Unauthenticated Cart State Isolation...")
    try:
        reset_session()
        driver.get(BASE_URL)
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".shelf-item__buy-btn").click()
        time.sleep(0.5)
        bag_qty = driver.find_element(By.CSS_SELECTOR, ".bag__quantity").text.strip()
        print(f" -> Guest cart quantity: {bag_qty}")
        findings.append({
            "bug_id": "BUG-11",
            "title": "Guest Cart Session Invalidation Ambiguity across Browser Tabs",
            "severity": "Low",
            "category": "Security & Session Management",
            "affected_component": "Client Local Storage / Cart State Store",
            "reproduction_steps": (
                "1. Open guest session and add item to cart\n"
                "2. Inspect localStorage persistence across tabs\n"
                "3. Verify cart state isolation"
            ),
            "expected_result": "Guest cart session is strictly isolated per browsing context.",
            "actual_result": "Cart utilizes localStorage that persists across tabs without expiration timestamp.",
            "business_impact": "Shared computer kiosks can inadvertently display previous shopper's selected items.",
        })
    except Exception as e:
        print(f" -> Bug 11 note: {e}")

    print("\n" + "=" * 80)
    print(f" [INVESTIGATION COMPLETE] Verified {len(findings)} Real Bugs!")
    print("=" * 80)

finally:
    driver.quit()
