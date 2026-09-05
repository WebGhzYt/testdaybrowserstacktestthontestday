"""
BrowserStack Test Management Integration Utility
1. Generates CSV for 1-Click Import into Test Management Web UI (folders, test cases, steps)
2. Syncs JUnit XML execution results directly to BrowserStack Test Management REST API
"""

import os
import csv
import json
import requests
from pathlib import Path
from utils.config import (
    BROWSERSTACK_USERNAME,
    BROWSERSTACK_ACCESS_KEY,
    REPORTS_DIR,
    BASE_DIR,
)

CSV_PATH = BASE_DIR / "browserstack_test_management_cases.csv"
JUNIT_PATH = REPORTS_DIR / "junit_report.xml"


def generate_junit_xml():
    """
    Generates JUnit XML from test records in database for BrowserStack Test Management.
    """
    from utils.db_utils import get_all_results
    import xml.etree.ElementTree as ET

    records = get_all_results()
    testsuites = ET.Element("testsuites", name="BrowserStack_Testathon", tests=str(len(records)))
    testsuite = ET.SubElement(
        testsuites,
        "testsuite",
        name="webghzyt",
        tests=str(len(records)),
        failures=str(sum(1 for r in records if r.get("status") == "FAILED")),
        errors="0",
        time=str(sum(r.get("duration_seconds", 0.0) for r in records)),
    )

    for r in records:
        tc = ET.SubElement(
            testsuite,
            "testcase",
            classname=f"tests.{r.get('category', 'General').replace(' ', '_')}",
            name=r.get("test_name", "test"),
            time=f"{r.get('duration_seconds', 0.0):.2f}",
        )
        if r.get("status") == "FAILED":
            fail = ET.SubElement(tc, "failure", message="Test Failed")
            fail.text = r.get("error_message", "AssertionError")

    tree = ET.ElementTree(testsuites)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    tree.write(str(JUNIT_PATH), encoding="utf-8", xml_declaration=True)
    print(f"[JUNIT] Generated XML report -> {JUNIT_PATH}")
    return str(JUNIT_PATH)


def generate_test_management_csv():
    """
    Generates a standardized CSV formatted specifically for BrowserStack Test Management
    importing into project 4102200.
    """
    fieldnames = [
        "Folder",
        "Title",
        "Description",
        "Preconditions",
        "Steps",
        "Expected Result",
        "Priority",
        "Type",
    ]

    test_cases = [
        # Functional & UI
        {
            "Folder": "Functional & UI/End-to-End",
            "Title": "TC_001: End-to-End User Purchase Journey",
            "Description": "Login -> Filter by Apple -> Add 2 items to Cart -> Fill Shipping Form -> Complete Checkout.",
            "Preconditions": "User credentials demouser / testingisfun99 exist. Catalog has Apple products.",
            "Steps": "1. Navigate to /signin and login.\n2. Select 'Apple' vendor filter.\n3. Add 2 products to cart.\n4. Click Checkout.\n5. Fill shipping form.\n6. Click continue.",
            "Expected Result": "Order confirmation banner 'Your Order has been successfully placed' is displayed.",
            "Priority": "High",
            "Type": "Functional",
        },
        {
            "Folder": "Functional & UI/End-to-End",
            "Title": "TC_002: Cart Persistence across Sessions",
            "Description": "Verify cart items persist after user logs out and logs back in.",
            "Preconditions": "User is registered and logged in.",
            "Steps": "1. Login as demouser.\n2. Add item to cart.\n3. Click logout.\n4. Re-login.\n5. Open cart drawer.",
            "Expected Result": "Cart drawer retains the previously added item with correct bag quantity.",
            "Priority": "High",
            "Type": "Functional",
        },
        {
            "Folder": "Functional & UI/End-to-End",
            "Title": "TC_003: Unauthenticated Guest Checkout Prompt",
            "Description": "Proceed to checkout as an unauthenticated guest and verify prompt to login.",
            "Preconditions": "No active user session (cookies cleared).",
            "Steps": "1. Navigate to catalog.\n2. Add product to cart.\n3. Open cart and click Checkout.",
            "Expected Result": "User is redirected to /signin with a prompt to authenticate before checkout.",
            "Priority": "Medium",
            "Type": "Functional",
        },
        {
            "Folder": "Functional & UI/Smoke & Sanity",
            "Title": "TC_004: Valid User Authentication",
            "Description": "Verify login with valid credentials (demouser / testingisfun99).",
            "Preconditions": "Application is online at https://bugbash.online/.",
            "Steps": "1. Go to /signin.\n2. Select demouser in Username.\n3. Select testingisfun99 in Password.\n4. Click Login.",
            "Expected Result": "User identifier label is displayed in header.",
            "Priority": "High",
            "Type": "Smoke",
        },
        {
            "Folder": "Functional & UI/Smoke & Sanity",
            "Title": "TC_005: Invalid Password API Error Verification",
            "Description": "Verify invalid login displays 'Invalid username or password' API error.",
            "Preconditions": "User enters incorrect password.",
            "Steps": "1. Go to /signin.\n2. Select demouser.\n3. Type incorrect password.\n4. Click Login.",
            "Expected Result": "API error banner appears displaying invalid credentials message.",
            "Priority": "High",
            "Type": "Negative",
        },
        {
            "Folder": "Functional & UI/Catalog & Cart",
            "Title": "TC_006: Samsung Vendor Catalog Filtering",
            "Description": "Verify filtering products by 'Samsung' only displays Samsung devices.",
            "Preconditions": "Catalog is loaded with all products.",
            "Steps": "1. Click Samsung filter checkmark in left sidebar.\n2. Inspect visible product titles.",
            "Expected Result": "All rendered shelf items contain 'Galaxy' or 'Samsung' in their title.",
            "Priority": "Medium",
            "Type": "Functional",
        },
        {
            "Folder": "Functional & UI/Catalog & Cart",
            "Title": "TC_007: Cart Item Removal Decrements Bag Quantity",
            "Description": "Verify removing an item from the cart decreases the bag quantity counter.",
            "Preconditions": "At least one item added to cart drawer.",
            "Steps": "1. Add product to cart.\n2. Open cart drawer.\n3. Click 'X' delete button on item.",
            "Expected Result": "Item is removed and bag quantity counter decrements.",
            "Priority": "Medium",
            "Type": "Functional",
        },
        {
            "Folder": "Functional & UI/Catalog & Cart",
            "Title": "TC_008: Mathematical Subtotal Calculation",
            "Description": "Verify subtotal calculates correctly when multiple items are added.",
            "Preconditions": "Products with different price points in catalog.",
            "Steps": "1. Add 2 distinct items to cart.\n2. Open cart drawer.\n3. Verify subtotal price.",
            "Expected Result": "Subtotal equals exact sum of item prices.",
            "Priority": "High",
            "Type": "Functional",
        },
        {
            "Folder": "Functional & UI/Catalog & Cart",
            "Title": "TC_009: Empty Cart Notification Display",
            "Description": "Verify empty cart displays 'Add some products in the cart'.",
            "Preconditions": "Cart is empty (new session).",
            "Steps": "1. Open cart drawer without adding any items.",
            "Expected Result": "Empty cart illustration/text 'Add some products in the cart' is visible.",
            "Priority": "Low",
            "Type": "Edge Case",
        },
        {
            "Folder": "Functional & UI/Catalog & Cart",
            "Title": "TC_010: Checkout Button Disabled in Empty Cart",
            "Description": "Verify checkout button is disabled or hidden when the cart is empty.",
            "Preconditions": "Cart is empty.",
            "Steps": "1. Open cart drawer.",
            "Expected Result": "Checkout button is either hidden or has disabled attribute.",
            "Priority": "Medium",
            "Type": "Edge Case",
        },
        {
            "Folder": "Functional & UI/Visual & Responsive",
            "Title": "TC_011: Product Grid Layout Cross-Browser Parity",
            "Description": "Verify product grid layout renders with proper bounding boxes across platforms.",
            "Preconditions": "Browser window open at 1920x1080.",
            "Steps": "1. Load catalog page.\n2. Measure card height and width dimensions.",
            "Expected Result": "Cards render with non-zero dimensions and equal spacing.",
            "Priority": "Medium",
            "Type": "Visual",
        },
        {
            "Folder": "Functional & UI/Visual & Responsive",
            "Title": "TC_012: Cart Drawer Animation & Transition",
            "Description": "Verify cart drawer animation slides out smoothly and toggles open state.",
            "Preconditions": "Catalog loaded.",
            "Steps": "1. Click floating bag icon.\n2. Verify .float-cart--open class.",
            "Expected Result": "Cart slides into view smoothly.",
            "Priority": "Low",
            "Type": "Visual",
        },
        {
            "Folder": "Functional & UI/Visual & Responsive",
            "Title": "TC_013: 320px Viewport Image Boundary Containment",
            "Description": "Verify product images do not overflow their containers on a 320px screen width.",
            "Preconditions": "Window resized to 320px.",
            "Steps": "1. Resize viewport to 320px width.\n2. Inspect product image bounding widths.",
            "Expected Result": "Image width does not exceed 320px.",
            "Priority": "Medium",
            "Type": "Visual",
        },
        # Security & Vulnerability
        {
            "Folder": "Security & Vulnerability/Authentication",
            "Title": "TC_014: SQL Injection Rejection in Login",
            "Description": "Attempt SQL Injection (' OR 1=1 --) in username field; ensure rejection.",
            "Preconditions": "Login page loaded.",
            "Steps": "1. Inject SQL payload in username.\n2. Click Login.",
            "Expected Result": "Authentication is rejected; no unauthorized access granted.",
            "Priority": "Critical",
            "Type": "Security",
        },
        {
            "Folder": "Security & Vulnerability/Authentication",
            "Title": "TC_015: Direct /checkout URL Access Bypass Guard",
            "Description": "Attempt to bypass login by directly navigating to /checkout.",
            "Preconditions": "No active session.",
            "Steps": "1. Navigate directly to /checkout.",
            "Expected Result": "Application guards the checkout route and redirects to /signin.",
            "Priority": "Critical",
            "Type": "Security",
        },
        {
            "Folder": "Security & Vulnerability/Authentication",
            "Title": "TC_016: Session Invalidation upon Logout",
            "Description": "Verify session token is invalidated upon clicking logout.",
            "Preconditions": "User logged in.",
            "Steps": "1. Click logout.\n2. Click browser back button.",
            "Expected Result": "User session is not resurrected.",
            "Priority": "High",
            "Type": "Security",
        },
        {
            "Folder": "Security & Vulnerability/Injection & Fuzzing",
            "Title": "TC_017: XSS Payload Escaping in Shipping Form",
            "Description": "Inject malicious JavaScript (<script>alert('xss')</script>) into First Name.",
            "Preconditions": "Checkout page loaded.",
            "Steps": "1. Enter XSS script in First Name field.\n2. Inspect DOM and document title.",
            "Expected Result": "Payload is escaped as text; script does not execute.",
            "Priority": "Critical",
            "Type": "Security",
        },
        {
            "Folder": "Security & Vulnerability/Injection & Fuzzing",
            "Title": "TC_018: Postal Code Boundary & Fuzzing Resilience",
            "Description": "Submit negative values and oversized 255+ char strings in postal code.",
            "Preconditions": "Shipping form open.",
            "Steps": "1. Fill oversized postal code string.\n2. Click continue.",
            "Expected Result": "Application handles input safely without dumping raw server tracebacks.",
            "Priority": "Medium",
            "Type": "Security",
        },
        {
            "Folder": "Security & Vulnerability/Injection & Fuzzing",
            "Title": "TC_019: Client DOM Price Tampering Inspection",
            "Description": "Tamper with DOM price payload to $0.00 and verify price integrity.",
            "Preconditions": "Item in cart drawer.",
            "Steps": "1. Tamper client-side price.\n2. Verify system records original product value.",
            "Expected Result": "True server price remains intact.",
            "Priority": "High",
            "Type": "Security",
        },
        # Performance & Reliability
        {
            "Folder": "Performance & Reliability/Stress & Load",
            "Title": "TC_020: 50 Concurrent User Login Simulation",
            "Description": "Simulate 50 concurrent login requests hitting authentication endpoint.",
            "Preconditions": "Connection pool with 20 workers.",
            "Steps": "1. Dispatch concurrent HTTP requests.\n2. Measure response codes.",
            "Expected Result": "High success rate without server 500 crashes.",
            "Priority": "High",
            "Type": "Performance",
        },
        {
            "Folder": "Performance & Reliability/Stress & Load",
            "Title": "TC_021: Catalog Vendor Filter Load Simulation",
            "Description": "Simulate concurrent requests hitting catalog endpoint under load.",
            "Preconditions": "Connection pool with 25 workers.",
            "Steps": "1. Dispatch parallel requests to catalog.",
            "Expected Result": "Catalog returns 200 OK across requests.",
            "Priority": "High",
            "Type": "Performance",
        },
        {
            "Folder": "Performance & Reliability/Spike & Resilience",
            "Title": "TC_022: Rapid Add-to-Cart Click Spike Resilience",
            "Description": "Rapidly click Add to Cart 15+ times in < 0.5s; verify UI stability.",
            "Preconditions": "Catalog loaded.",
            "Steps": "1. Perform 15 clicks rapidly.\n2. Open cart.",
            "Expected Result": "UI does not freeze; cart retains added products.",
            "Priority": "Medium",
            "Type": "Performance",
        },
        {
            "Folder": "Performance & Reliability/Spike & Resilience",
            "Title": "TC_023: Slow 3G Network Latency Throttling",
            "Description": "Simulate high latency (Slow 3G) and verify login completes gracefully.",
            "Preconditions": "Network conditions emulated via CDP.",
            "Steps": "1. Set 200ms latency.\n2. Execute login flow.",
            "Expected Result": "Login completes without premature timeout.",
            "Priority": "Medium",
            "Type": "Performance",
        },
        # Usability & Compliance
        {
            "Folder": "Usability & Compliance/Accessibility",
            "Title": "TC_024: Keyboard-Only Form Navigation (Tab & Enter)",
            "Description": "Navigate from login inputs to submit using exclusively Tab and Enter.",
            "Preconditions": "Login page loaded.",
            "Steps": "1. Send TAB keystrokes to cycle focus.\n2. Verify activeElement.",
            "Expected Result": "Focus visibly highlights interactive input controls.",
            "Priority": "Medium",
            "Type": "Accessibility",
        },
        {
            "Folder": "Usability & Compliance/Accessibility",
            "Title": "TC_025: Screen Reader Accessibility for Cart Close Button",
            "Description": "Verify screen readers can announce the 'X' button inside cart drawer.",
            "Preconditions": "Cart drawer open.",
            "Steps": "1. Inspect close button attributes for aria-label, role, or text.",
            "Expected Result": "Close button has accessible identifier attribute.",
            "Priority": "High",
            "Type": "Accessibility",
        },
        {
            "Folder": "Usability & Compliance/Accessibility",
            "Title": "TC_026: Error Banner Color Contrast Verification",
            "Description": "Verify color contrast CSS property on red invalid login error text.",
            "Preconditions": "Error banner visible.",
            "Steps": "1. Read computed CSS color property on error element.",
            "Expected Result": "Defined high-contrast color property is present.",
            "Priority": "Low",
            "Type": "Accessibility",
        },
        {
            "Folder": "Usability & Compliance/Form Validation",
            "Title": "TC_027: Blank Shipping Form Inline Validation",
            "Description": "Submit shipping form completely blank and verify submission is blocked.",
            "Preconditions": "Checkout page loaded.",
            "Steps": "1. Click continue without typing fields.",
            "Expected Result": "Order placement is blocked; inline validation triggers.",
            "Priority": "High",
            "Type": "Functional",
        },
        {
            "Folder": "Usability & Compliance/Form Validation",
            "Title": "TC_028: Mandatory Address Field Enforcement",
            "Description": "Ensure missing mandatory Address Line 1 blocks checkout completion.",
            "Preconditions": "All fields filled except address.",
            "Steps": "1. Submit form with missing address.",
            "Expected Result": "Submission is prevented.",
            "Priority": "High",
            "Type": "Functional",
        },
        # Specialized & Infrastructure
        {
            "Folder": "Specialized & Infrastructure/Mobile & Web",
            "Title": "TC_029: Mobile Viewport Floating Cart Accessibility",
            "Description": "Verify floating cart icon is accessible on mobile (375x812 iPhone dimension).",
            "Preconditions": "Window set to 375x812.",
            "Steps": "1. Click cart icon on mobile viewport.",
            "Expected Result": "Drawer opens and covers viewport responsively.",
            "Priority": "High",
            "Type": "Compatibility",
        },
        {
            "Folder": "Specialized & Infrastructure/Mobile & Web",
            "Title": "TC_030: Mobile Postal Code Keypad Input Attribute",
            "Description": "Verify shipping postal code input attributes for mobile keypad invocation.",
            "Preconditions": "Checkout page loaded.",
            "Steps": "1. Inspect postal code input element attributes.",
            "Expected Result": "Element is visible with appropriate type/inputmode.",
            "Priority": "Medium",
            "Type": "Compatibility",
        },
        {
            "Folder": "Specialized & Infrastructure/API Integrity",
            "Title": "TC_031: Graceful 404 Route Fallback Handling",
            "Description": "Verify non-existent routes render a clean fallback without raw server traces.",
            "Preconditions": "Navigate to /non-existent-endpoint.",
            "Steps": "1. Open 404 URL.\n2. Inspect page body.",
            "Expected Result": "No internal 500 server dumps or unhandled Python/Node tracebacks.",
            "Priority": "Medium",
            "Type": "Reliability",
        },
        {
            "Folder": "Specialized & Infrastructure/API Integrity",
            "Title": "TC_032: Local Storage and Cookie Cart State Reset",
            "Description": "Verify clearing Local Storage and Cookies resets unauthenticated cart state.",
            "Preconditions": "Item in cart.",
            "Steps": "1. Clear localStorage, sessionStorage, and cookies.\n2. Refresh page.",
            "Expected Result": "Cart resets to 0 items immediately.",
            "Priority": "High",
            "Type": "Functional",
        },
    ]

    with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tc in test_cases:
            writer.writerow(tc)

    print(f"[TEST MANAGEMENT CSV] Generated {len(test_cases)} cases -> {CSV_PATH}")
    return str(CSV_PATH)


def sync_junit_results_to_browserstack(project_name="webghzyt"):
    """
    POSTs JUnit XML results to BrowserStack Test Management API endpoint.
    """
    if not JUNIT_PATH.exists():
        print(f"[WARN] JUnit file {JUNIT_PATH} not found.")
        return False

    url = "https://test-management.browserstack.com/api/v1/import/results/xml/junit"
    auth = (BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY)

    try:
        with open(JUNIT_PATH, "rb") as f:
            files = {"file": ("junit_report.xml", f, "application/xml")}
            data = {"project_name": project_name}
            res = requests.post(url, auth=auth, files=files, data=data, timeout=15)
            print(f"[API SYNC] BrowserStack Test Management response: {res.status_code}")
            print(f"         {res.text}")
            return res.status_code in [200, 201]
    except Exception as e:
        print(f"[ERROR] Syncing JUnit to BrowserStack failed: {e}")
        return False


if __name__ == "__main__":
    generate_test_management_csv()
