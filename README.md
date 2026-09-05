# testdaybrowserstacktestthontestday
# BrowserStack Testathon - End-to-End Test Automation Framework

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.x-green.svg)
![Pytest](https://img.shields.io/badge/Pytest-8.x-orange.svg)
![BrowserStack](https://img.shields.io/badge/BrowserStack-SDK-brightgreen.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20SQLite-336791.svg)

A complete, enterprise-grade test automation framework built for the **BrowserStack Testathon** hackathon, targeting the **StackDemo E-Commerce** platform at [https://bugbash.online/](https://bugbash.online/).

---

## 📱 Comprehensive Device & OS Matrix Workbook

This repository includes the dedicated Excel workbook: **`BrowserStack_Device_Matrix_and_Test_Cases.xlsx`** containing two distinct sheets:
1. **Device & OS Matrix**: Comprehensive list detailing BrowserStack's supported Desktop environments (Windows 11, 10, 8.1, 7; macOS Sequoia, Sonoma, Ventura, Monterey, Big Sur), Smartphones (ranging from legacy small screens to modern large Pro models and foldables), and Tablets.
   - **Microsoft Edge**: 152 (latest), 153 (beta), 154 (dev)
   - **Mozilla Firefox**: 154 (latest), 156 (beta)
   - **Google Chrome**: 152 (latest), 153 (beta), 154 (dev)
   - **Opera**: 135 (latest), 136 (dev)
   - **Yandex**: 14.12 (latest)
   - **Safari**: 18.0 (latest), 17.0, 16.5, 14.1
2. **Cross-Device Test Cases**: A focused list of test scenarios specifically designed to validate responsive UI, browser engines, form factors, and interactions across the devices listed in the matrix (`tests/test_06_cross_device_matrix.py`).

---

## 🔗 Key Links & Deliverables

- **GitHub Repository**: [https://github.com/WebGhzYt/testdaybrowserstacktestthontestday](https://github.com/WebGhzYt/testdaybrowserstacktestthontestday)
- **Target Application**: [https://bugbash.online/](https://bugbash.online/)
- **BrowserStack Project Name**: `webghzyt`
- **BrowserStack Test Management Project**: [https://test-management.browserstack.com/projects/4102200/folder](https://test-management.browserstack.com/projects/4102200/folder)
- **BrowserStack Automate Dashboard**: [https://automate.browserstack.com/dashboard](https://automate.browserstack.com/dashboard)
- **BrowserStack Test Observability**: [https://observability.browserstack.com/](https://observability.browserstack.com/)

---

## 🏛 Framework Architecture

The framework is architected using the **Page Object Model (POM)** design pattern, decoupling test logic from UI locators and interactions:

```
testdaybrowserstacktestthontestday/
│
├── .env                           # Environment configuration (BrowserStack, PostgreSQL, API)
├── browserstack.yml               # BrowserStack SDK config (webghzyt, platforms, Test Management)
├── requirements.txt               # Pinned project dependencies
├── pytest.ini                     # Pytest runner configuration and test markers
├── conftest.py                    # Driver fixtures, PostgreSQL database sync & auto-reporting hooks
│
├── pages/                         # Page Object Model (POM) Layer
│   ├── base_page.py               # Robust explicit waits, safe click/type, JS click fallback, scroll
│   ├── login_page.py              # React-Select dropdown authentication & error handling
│   ├── catalog_page.py            # Vendor filtering (Apple, Samsung), product cards, prices
│   ├── cart_page.py               # Cart drawer verification, quantity checks, subtotal, deletion
│   └── checkout_page.py           # Shipping form submission & order confirmation
│
├── utils/                         # Infrastructure & Utility Layer
│   ├── config.py                  # Configuration loader with .env support
│   ├── db_utils.py                # PostgreSQL sync utility with automatic SQLite fallback
│   └── report_utils.py            # Automated Excel (.xlsx) and Executive PDF (.pdf) export engine
│
├── tests/                         # Test Suite (32 Comprehensive Scenarios)
│   ├── test_01_functional_ui.py   # TC_001 to TC_013: E2E, Smoke, Sanity, Cross Browser & Visual
│   ├── test_02_security.py        # TC_014 to TC_019: SQLi, Route Bypass, Session Invalid, XSS, Fuzzing
│   ├── test_03_performance.py     # TC_020 to TC_023: Concurrency, Filter Stress, Spike Clicks, Throttling
│   ├── test_04_usability.py       # TC_024 to TC_028: Keyboard navigation, Accessibility, Contrast, Validation
│   └── test_05_specialized.py     # TC_029 to TC_032: Mobile Viewport, Keypad Types, Fallbacks, Cookie Reset
│
├── reports/                       # Generated Execution Artifacts
│   ├── test_execution_report.xlsx # Excel spreadsheet with summary metrics and test breakdown
│   ├── test_execution_report.pdf  # Professional executive PDF report with styled tables
│   └── test_execution_results.db  # Local SQLite database fallback (if PostgreSQL is offline)
│
├── run_tests.bat                  # Single-click Windows runner
└── run_tests.sh                   # Single-click Linux/macOS runner
```

---

## 📋 Comprehensive Test Coverage Matrix (32 Scenarios)

### 1. Functional & UI Testing (`tests/test_01_functional_ui.py`)
- **TC_001**: End-to-End User Journey: Login (`demouser`/`testingisfun99`) $\to$ Filter by "Apple" $\to$ Add 2 items $\to$ Shipping Form $\to$ Order Confirmation.
- **TC_002**: Cart Persistence across sessions: Login $\to$ Add item $\to$ Logout $\to$ Login again $\to$ Verify cart retention.
- **TC_003**: Unauthenticated Guest Checkout: Attempt checkout without logging in $\to$ verify prompt/redirect to signin.
- **TC_004**: Valid User Authentication: Verify login with valid credentials displays user identifier.
- **TC_005**: Invalid Password Handling: Verify invalid login displays "Invalid username or password" API error banner.
- **TC_006**: Vendor Filtering: Verify filtering by "Samsung" renders exclusively Samsung devices.
- **TC_007**: Bag Quantity Verification: Verify removing an item from cart drawer decrements the bag counter.
- **TC_008**: Subtotal Mathematical Calculation: Verify cart subtotal accurately aggregates prices of added items.
- **TC_009**: Empty Cart UI: Verify empty cart displays "Add some products in the cart".
- **TC_010**: Checkout Button State: Verify checkout button is disabled or hidden when cart is empty.
- **TC_011**: Cross Browser Layout: Verify product grid elements maintain proper bounding dimensions.
- **TC_012**: Cart Drawer Slideout: Verify cart drawer open/close animation and element toggle.
- **TC_013**: Responsive Boundaries: Verify product images do not overflow containers at 320px viewport.

### 2. Security & Vulnerability Testing (`tests/test_02_security.py`)
- **TC_014**: SQL Injection (SQLi): Attempt `' OR 1=1 --` injection in username field; verify rejection.
- **TC_015**: Authorization Bypass: Attempt direct URL access to `/checkout` without active session.
- **TC_016**: Session Invalidation: Verify session token/cookies are invalidated upon logout and browser back button.
- **TC_017**: Cross-Site Scripting (XSS): Inject `<script>alert('xss')</script>` payload in shipping form; verify escaping.
- **TC_018**: Boundary Fuzzing: Submit negative or oversized string payloads in postal code; ensure no unhandled crashes.
- **TC_019**: Price Tampering Inspection: Inspect client-side DOM price tampering resilience.

### 3. Performance & Reliability Testing (`tests/test_03_performance.py`)
- **TC_020**: Concurrent User Logins: Simulate 50 concurrent requests hitting authentication route.
- **TC_021**: Vendor Filter Load: Simulate concurrent catalog filter requests hitting the home catalog.
- **TC_022**: Rapid Click Spike: Rapidly click "Add to Cart" button 15+ times; verify UI stability without freeze.
- **TC_023**: Network Throttling Simulation: Emulate high latency / Slow 3G network conditions on login.

### 4. Usability & Compliance Testing (`tests/test_04_usability.py`)
- **TC_024**: Keyboard-Only Navigation: Navigate interactive form elements solely via `Tab` and `Enter` keys.
- **TC_025**: Screen Reader Accessibility: Verify cart drawer close button possesses accessible aria-label or role.
- **TC_026**: Color Contrast: Verify CSS color property presence on error alert banner.
- **TC_027**: Blank Form Validation: Submit blank shipping form; verify inline validation blocks completion.
- **TC_028**: Mandatory Field Enforcement: Verify omitting mandatory Address Line 1 blocks checkout.

### 5. Specialized & Infrastructure Testing (`tests/test_05_specialized.py`)
- **TC_029**: Mobile Viewport Compatibility: Verify floating cart icon visibility at 375x812 iPhone dimension.
- **TC_030**: Mobile Keypad Optimization: Verify postal code input attributes (`type`, `pattern`, `inputmode`).
- **TC_031**: Graceful Error Fallback: Verify 404/500 routes do not dump raw server stack traces.
- **TC_032**: Cookie & Local Storage Reset: Verify clearing browser storage resets unauthenticated cart state immediately.

---

## 🗄 Database Synchronization (PostgreSQL & Resilient Fallback)

All test executions are logged automatically via Pytest hooks in `conftest.py` into the `test_execution_results` table:

```sql
CREATE TABLE IF NOT EXISTS test_execution_results (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    status VARCHAR(50) NOT NULL,
    duration_seconds NUMERIC(10, 3),
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    browser_info VARCHAR(255),
    session_id VARCHAR(255)
);
```

> **Resilience Guarantee**: If PostgreSQL is temporarily stopped or unavailable, the framework automatically switches to an embedded SQLite database (`reports/test_execution_results.db`) with identical schema, ensuring tests and reporting **never crash**.

---

## 📊 Executive Reporting (Excel & PDF)

At the conclusion of each test run, `utils/report_utils.py` automatically generates:
1. **Excel Report (`reports/test_execution_report.xlsx`)**:
   - **Execution Summary Sheet**: High-level KPI metrics (Total Executed, Passed, Failed, Pass Rate %, Duration).
   - **Test Details Sheet**: Full breakdown of each test case with conditional color formatting (Green for PASS, Red for FAIL).
2. **Executive PDF Report (`reports/test_execution_report.pdf`)**:
   - Branded header for project `webghzyt` and BrowserStack Testathon.
   - Summary KPI statistics table.
   - Detailed status matrix with error snippets.

---

## 🚀 Single-Click Execution

### On Windows
Double-click or run:
```cmd
run_tests.bat
```
*This script automatically creates `.venv`, installs `requirements.txt`, executes tests via `browserstack-sdk pytest`, and exports reports.*

### On Linux / macOS
Run:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

## ⚙ Manual Setup & Execution

### 1. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run with BrowserStack Cloud SDK (Cross-Browser)
```bash
browserstack-sdk pytest tests/ -v
```

### 4. Run Locally (Chrome)
```bash
pytest tests/ -v
```

### 5. Run Specific Category or Scenarios
```bash
# Run Hackathon E2E Scenario 1
pytest tests/test_01_functional_ui.py -k "test_tc001" -v

# Run Security Suite
pytest -m security -v

# Run Smoke Tests
pytest -m smoke -v
```

### 6. Generate Reports On-Demand
```bash
python -m utils.report_utils
```

---

## 🏆 Hackathon Judging Criteria Alignment

| Criteria | Implementation in this Framework |
| :--- | :--- |
| **1. Thought-through Test Coverage** | **32 Test Cases** spanning Functional, UI, Negative, Edge Cases, Security (SQLi, XSS), Performance (concurrency, spikes), Usability (WCAG, keyboard), and Mobile. |
| **2. Quality of Automation** | Full **Page Object Model (POM)**, explicit `WebDriverWait` synchronization, JavaScript click fallbacks, clean separation of concerns. |
| **3. BrowserStack Integration** | Full `browserstack.yml` configured for project `webghzyt`, Test Management project `4102200`, cross-platform matrices (Windows, macOS, Android, iOS). |
| **4. Database & Infrastructure** | Automated PostgreSQL test syncing (`db_utils.py`) with SQLite failover and automatic Excel + PDF report generation. |
| **5. Portability & Ease of Use** | Single-click `run_tests.bat` / `run_tests.sh`, reproducible `.venv`, comprehensive `requirements.txt`. |
