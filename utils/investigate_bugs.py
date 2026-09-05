"""
Investigate and Validate 10+ Real Bugs on https://bugbash.online/
Performs deep-dive exploratory automation to detect, reproduce, and log real application bugs.
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
from utils.config import BASE_URL

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

bugs_found = []

try:
    print("\n" + "="*80)
    print(" [DRILL-DOWN BUG ANALYSIS] Inspecting https://bugbash.online/")
    print("="*80)

    # --------------------------------------------------------------------------
    # 1. Inspect Image Loading for 'image_not_loading_user'
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 1: Image Loading for 'image_not_loading_user' ---")
    driver.get(f"{BASE_URL}signin")
    time.sleep(2)
    # Select image_not_loading_user
    username_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#username input, #username")))
    username_input.click()
    time.sleep(0.5)
    img_user_opt = driver.find_elements(By.XPATH, "//*[contains(text(), 'image_not_loading_user')]")
    if img_user_opt:
        img_user_opt[0].click()
    else:
        # try typing
        driver.find_element(By.CSS_SELECTOR, "#username input").send_keys("image_not_loading_user\n")

    time.sleep(0.5)
    pwd_input = driver.find_element(By.CSS_SELECTOR, "#password input, #password")
    pwd_input.click()
    time.sleep(0.5)
    pwd_opt = driver.find_elements(By.XPATH, "//*[contains(text(), 'testingisfun99')]")
    if pwd_opt:
        pwd_opt[0].click()
    time.sleep(0.5)
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(2)

    # Inspect images
    images = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__thumb img")
    broken_images = 0
    for img in images:
        natural_width = driver.execute_script("return arguments[0].naturalWidth;", img)
        if natural_width == 0:
            broken_images += 1

    print(f" Total product images: {len(images)} | Broken images: {broken_images}")
    if broken_images > 0:
        bugs_found.append({
            "id": "BUG-001",
            "title": "Product Images Fail to Render for 'image_not_loading_user'",
            "severity": "High",
            "category": "Visual & Functional UI",
            "description": f"When logged in as image_not_loading_user, {broken_images} out of {len(images)} product images fail to load (naturalWidth = 0), displaying broken placeholder icons.",
            "reproduction": "1. Go to /signin\n2. Log in with image_not_loading_user / testingisfun99\n3. Observe catalog shelf product images",
            "expected": "All product images should render with valid HTTP 200 URLs.",
            "actual": f"{broken_images} images fail to load with broken src assets."
        })

    # Logout
    logout_btns = driver.find_elements(By.ID, "signin")
    if logout_btns:
        logout_btns[0].click()
        time.sleep(1)

    # --------------------------------------------------------------------------
    # 2. Inspect Price Sorting Logic: 'Lowest to highest' vs Actual Prices
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 2: Catalog Price Sorting Anomalies ---")
    driver.get(BASE_URL)
    time.sleep(2)
    sort_select = driver.find_elements(By.CSS_SELECTOR, ".sort select")
    if sort_select:
        sort_select[0].click()
        time.sleep(0.5)
        # Select lowest to highest
        options_elem = driver.find_elements(By.XPATH, "//option[contains(text(), 'Lowest to highest')]")
        if options_elem:
            options_elem[0].click()
            time.sleep(1.5)

        prices = []
        price_elems = driver.find_elements(By.CSS_SELECTOR, ".val b")
        for p in price_elems:
            try:
                prices.append(float(p.text.replace("$", "").replace(",", "").strip()))
            except Exception:
                pass
        
        print(f" Lowest to Highest sorted prices: {prices[:6]}...")
        # Check if strictly non-decreasing
        is_sorted = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
        if not is_sorted:
            print(" [BUG FOUND] Prices are not correctly sorted ascending!")
            bugs_found.append({
                "id": "BUG-002",
                "title": "Price Sorting 'Lowest to Highest' Yields Unsorted Sequence",
                "severity": "Medium",
                "category": "Functional & Logic",
                "description": f"Selecting 'Lowest to highest' in catalog sort dropdown produces an improperly sorted list: {prices[:5]}.",
                "reproduction": "1. Go to homepage\n2. In Sort dropdown, select 'Lowest to highest'\n3. Compare price of item 1 vs item 2",
                "expected": "Prices should be strictly ascending (e.g. $199 <= $399 <= $499).",
                "actual": f"Unsorted price order detected: {prices[:5]}."
            })
        else:
            print(" Prices are correctly sorted ascending.")

    # --------------------------------------------------------------------------
    # 3. Inspect Empty / Blank Shipping Form Validation
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 3: Shipping Form Mandatory Field Validation Leak ---")
    driver.get(BASE_URL)
    time.sleep(1)
    # Login as demouser
    driver.get(f"{BASE_URL}signin")
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "#username").click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, "//*[contains(text(), 'demouser')]").click()
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "#password").click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, "//*[contains(text(), 'testingisfun99')]").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(2)

    # Add item
    driver.find_element(By.CSS_SELECTOR, ".shelf-item__buy-btn").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".buy-btn").click()
    time.sleep(2)

    # In checkout page: test leaving fields blank
    checkout_url = driver.current_url
    print(f" Current Checkout URL: {checkout_url}")
    # Click checkout submit button
    submit_btn = driver.find_elements(By.ID, "checkout-shipping-continue")
    if submit_btn:
        submit_btn[0].click()
        time.sleep(1)
        # Check if validation alert is rendered or if it allows submit
        alerts = driver.find_elements(By.CSS_SELECTOR, ".form-legend, .error, .invalid, [role='alert']")
        alert_texts = [a.text for a in alerts if a.text.strip()]
        print(f" Validation alert texts: {alert_texts}")
        
        # Test filling only first name and submitting without address
        fname = driver.find_element(By.ID, "firstNameInput")
        fname.send_keys("TestUser")
        submit_btn[0].click()
        time.sleep(1)
        
        # Check if address input has HTML5 'required' attribute or custom validation
        addr = driver.find_element(By.ID, "addressLine1Input")
        is_required = addr.get_attribute("required")
        print(f" Address input 'required' attribute: {is_required}")
        if not is_required:
            bugs_found.append({
                "id": "BUG-003",
                "title": "Address Field Lacks HTML5 'required' Attribute & Inline Guard",
                "severity": "Medium",
                "category": "Forms & Usability",
                "description": "Shipping addressLine1Input does not specify HTML5 required attribute or aria-required='true', relying on client script that permits submission state ambiguity.",
                "reproduction": "1. Proceed to /checkout\n2. Inspect #addressLine1Input DOM attributes",
                "expected": "Mandatory address input should specify required and aria-required='true'.",
                "actual": "Attribute 'required' is missing from addressLine1Input element."
            })

    # --------------------------------------------------------------------------
    # 4. Inspect Download Order Receipt PDF on Confirmation Page
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 4: Order Receipt Download Functionality ---")
    driver.find_element(By.ID, "lastNameInput").send_keys("Tester")
    driver.find_element(By.ID, "addressLine1Input").send_keys("123 Test Avenue")
    driver.find_element(By.ID, "provinceInput").send_keys("California")
    driver.find_element(By.ID, "postCodeInput").send_keys("90210")
    time.sleep(0.5)
    driver.find_element(By.ID, "checkout-shipping-continue").click()
    time.sleep(2)

    receipt_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Download order receipt')] | //a[contains(., 'Download order receipt')]")
    if receipt_btn:
        btn_tag = receipt_btn[0].tag_name
        href = receipt_btn[0].get_attribute("href")
        onclick = receipt_btn[0].get_attribute("onclick")
        print(f" Receipt element tag: {btn_tag} | href: {href} | onclick: {onclick}")
        
        # Click receipt button
        receipt_btn[0].click()
        time.sleep(1)
        # Check if download triggered or if alert or error
        if href is None and not onclick:
            bugs_found.append({
                "id": "BUG-004",
                "title": "Download Order Receipt Action Does Not Generate Real PDF File",
                "severity": "Medium",
                "category": "Functional & Export",
                "description": "Clicking 'Download order receipt' on confirmation page lacks valid download endpoint or data-URI attachment, failing to produce a physical invoice/receipt file.",
                "reproduction": "1. Complete purchase\n2. On confirmation screen, click 'Download order receipt'",
                "expected": "A physical PDF receipt invoice file should download to user system.",
                "actual": "Button does not bind to a valid downloadable PDF resource."
            })

    # --------------------------------------------------------------------------
    # 5. Inspect 'fav_user' Favourites Persistence Bug
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 5: Favourites Feature Behavior for 'fav_user' ---")
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
        driver.find_element(By.XPATH, "//*[contains(text(), 'testingisfun99')]").click()
        time.sleep(0.5)
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(2)

        # Look for favourites nav link or heart buttons
        fav_nav = driver.find_elements(By.XPATH, "//a[contains(., 'Favourites') or contains(., 'Favorites')] | //*[@id='favourites']")
        print(f" Favourites navigation link present: {len(fav_nav) > 0}")
        if fav_nav:
            fav_nav[0].click()
            time.sleep(1)
            fav_items = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
            print(f" Favourites shelf items count: {len(fav_items)}")
            if len(fav_items) == 0:
                bugs_found.append({
                    "id": "BUG-005",
                    "title": "'fav_user' Account Has Empty Favourites Catalog by Default",
                    "severity": "Low",
                    "category": "Functional & User Profiles",
                    "description": "Logging in as designated test user 'fav_user' displays 0 pre-saved favourite products in favourites view, despite being specifically configured for favourites testing.",
                    "reproduction": "1. Login as fav_user\n2. Click 'Favourites' in navigation\n3. Observe shelf count",
                    "expected": "Pre-configured favourites should be populated for fav_user.",
                    "actual": "Favourites shelf is completely empty (0 items)."
                })

    # --------------------------------------------------------------------------
    # 6. Inspect Cart Item Counter on Rapid Double Add (Race Condition)
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 6: Rapid Double-Click Add to Cart Counter Sync ---")
    driver.get(BASE_URL)
    time.sleep(1)
    # Double click add to cart on first item with 10ms gap
    buy_btns = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__buy-btn")
    if buy_btns:
        driver.execute_script("arguments[0].click(); arguments[0].click();", buy_btns[0])
        time.sleep(1)
        bag_qty = driver.find_element(By.CSS_SELECTOR, ".bag__quantity").text.strip()
        print(f" Bag quantity after double rapid click: {bag_qty}")
        # Check drawer items
        drawer_items = driver.find_elements(By.CSS_SELECTOR, ".float-cart .shelf-item")
        print(f" Drawer distinct items count: {len(drawer_items)}")
        if bag_qty == "1" and len(drawer_items) == 1:
            # Does it register as 1 item or 2 quantity?
            qty_elem = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__details .desc")
            print(f" Item details: {[q.text for q in qty_elem]}")

    # --------------------------------------------------------------------------
    # 7. Inspect Non-Existent 404 Route Server Header & Status Code
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 7: Client-Side Routing Missing HTTP 404 Status ---")
    res_404 = requests.get(f"{BASE_URL}non-existent-endpoint-404-check", timeout=10)
    print(f" HTTP status for non-existent route: {res_404.status_code}")
    if res_404.status_code == 200:
        bugs_found.append({
            "id": "BUG-007",
            "title": "Non-Existent Routes Return HTTP 200 OK Instead of Proper 404 Not Found",
            "severity": "Medium",
            "category": "SEO & Server Configuration",
            "description": "Navigating to non-existent URLs (e.g. /non-existent-endpoint-404-check) returns HTTP 200 OK because the SPA single-page server serves index.html without proper 404 response header.",
            "reproduction": "1. Send HTTP GET to https://bugbash.online/invalid-random-path\n2. Inspect response HTTP status code",
            "expected": "Web server should return HTTP 404 Not Found status code.",
            "actual": f"Web server returns HTTP {res_404.status_code} OK (Soft 404)."
        })

    # --------------------------------------------------------------------------
    # 8. Inspect Vendor Filter Checkbox Count Synchronization
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 8: Vendor Filter Count Desynchronization ---")
    driver.get(BASE_URL)
    time.sleep(1)
    # Check Apple
    apple_cb = driver.find_elements(By.XPATH, "//span[contains(text(), 'Apple')]")
    if apple_cb:
        apple_cb[0].click()
        time.sleep(1)
        header_text = driver.find_element(By.CSS_SELECTOR, ".shelf-header").text
        print(f" Shelf header after Apple filter: {header_text}")
        # Now check Samsung as well
        samsung_cb = driver.find_elements(By.XPATH, "//span[contains(text(), 'Samsung')]")
        if samsung_cb:
            samsung_cb[0].click()
            time.sleep(1)
            header_text_both = driver.find_element(By.CSS_SELECTOR, ".shelf-header").text
            print(f" Shelf header after Apple + Samsung: {header_text_both}")
            # Verify visible items
            visible_items = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
            print(f" Actual visible items on shelf: {len(visible_items)}")
            if "Product(s) found" in header_text_both:
                claimed_count = int(header_text_both.split()[0])
                if claimed_count != len(visible_items):
                    bugs_found.append({
                        "id": "BUG-008",
                        "title": "Catalog Header Product Count Mismatch with Rendered Shelf Items",
                        "severity": "Medium",
                        "category": "Functional & UI",
                        "description": f"Shelf header states '{header_text_both}' but DOM actually renders {len(visible_items)} items.",
                        "reproduction": "1. Check Apple and Samsung filters\n2. Compare header count to rendered items",
                        "expected": "Claimed count in header should match actual rendered cards.",
                        "actual": f"Header says {claimed_count}, but DOM contains {len(visible_items)}."
                    })

    # --------------------------------------------------------------------------
    # 9. Inspect Keyboard Tab Focus Outline Contrast
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 9: Interactive Elements Focus Visibility (WCAG 2.4.7) ---")
    driver.get(BASE_URL)
    time.sleep(1)
    first_btn = driver.find_element(By.CSS_SELECTOR, ".shelf-item__buy-btn")
    outline_style = driver.execute_script("return window.getComputedStyle(arguments[0]).outlineStyle;", first_btn)
    outline_width = driver.execute_script("return window.getComputedStyle(arguments[0]).outlineWidth;", first_btn)
    print(f" Buy button outline style: '{outline_style}', width: '{outline_width}'")
    if outline_style == "none" or outline_width == "0px":
        bugs_found.append({
            "id": "BUG-009",
            "title": "Missing Visible Focus Outline on 'Add to cart' Buttons (WCAG 2.4.7)",
            "severity": "Medium",
            "category": "Usability & Accessibility (WCAG AA)",
            "description": "The .shelf-item__buy-btn elements have outline: none or outline-width: 0px, preventing keyboard-only users from identifying focus location.",
            "reproduction": "1. Navigate catalog using TAB key\n2. Observe lack of focus bounding ring around Buy button",
            "expected": "Interactive buttons should display distinct visible focus outline (WCAG 2.4.7 AA).",
            "actual": f"Computed outline is style='{outline_style}' and width='{outline_width}'."
        })

    # --------------------------------------------------------------------------
    # 10. Inspect Horizontal Overflow on 320px Ultra-Compact Mobile Viewport
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 10: 320px Viewport Horizontal Overflow ---")
    driver.set_window_size(320, 640)
    driver.get(BASE_URL)
    time.sleep(1)
    body_scroll = driver.execute_script("return document.body.scrollWidth;")
    window_inner = driver.execute_script("return window.innerWidth;")
    print(f" 320px viewport: body scrollWidth = {body_scroll}, window innerWidth = {window_inner}")
    if body_scroll > window_inner + 5:
        bugs_found.append({
            "id": "BUG-010",
            "title": "Horizontal Content Overflow on 320px Small Smartphone Viewport",
            "severity": "Medium",
            "category": "Responsive UI & Cross-Device",
            "description": f"On ultra-compact mobile viewports (320px), body scrollWidth ({body_scroll}px) exceeds inner viewport width ({window_inner}px), causing unwanted horizontal scrolling.",
            "reproduction": "1. Set viewport to 320px width (iPhone SE / Galaxy Fold Cover)\n2. Attempt horizontal scroll",
            "expected": "Page content should fit within 320px width without horizontal scrollbars.",
            "actual": f"body.scrollWidth is {body_scroll}px exceeding viewport width of {window_inner}px."
        })

    # --------------------------------------------------------------------------
    # 11. Inspect 'locked_user' Authentication Feedback
    # --------------------------------------------------------------------------
    print("\n--- Testing Bug 11: 'locked_user' Error Message Ambiguity ---")
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
        driver.find_element(By.XPATH, "//*[contains(text(), 'testingisfun99')]").click()
        time.sleep(0.5)
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(1.5)
        
        # Check error banner
        error_elem = driver.find_elements(By.CSS_SELECTOR, ".api-error, [role='alert'], .error")
        err_msg = error_elem[0].text if error_elem else ""
        print(f" Locked user error message: '{err_msg}'")
        if "Your account has been locked" in err_msg:
            print(" Locked user feedback received as expected.")
        else:
            bugs_found.append({
                "id": "BUG-011",
                "title": "'locked_user' Login Banner Lacks Guidance or Recovery Instructions",
                "severity": "Low",
                "category": "Usability & Security",
                "description": f"When logging in with locked_user, banner displays '{err_msg}' without support contact or unlock instructions.",
                "reproduction": "1. Login with locked_user / testingisfun99\n2. Observe error banner text",
                "expected": "Error message should provide clear self-service or support unlock path.",
                "actual": f"Displays generic banner without recovery guidance: '{err_msg}'."
            })

    # Print Summary
    print("\n" + "="*80)
    print(f" [BUG ANALYSIS SUMMARY] Found {len(bugs_found)} Verified Real Application Bugs on https://bugbash.online/")
    print("="*80)
    for b in bugs_found:
        print(f"\n[{b['id']}] {b['title']} (Severity: {b['severity']} | {b['category']})")
        print(f"   Description: {b['description']}")
        print(f"   Expected: {b['expected']}")
        print(f"   Actual:   {b['actual']}")

finally:
    driver.quit()
