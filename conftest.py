"""
Pytest Configuration & Fixtures
Manages WebDriver lifecycles, database synchronization (PostgreSQL/SQLite),
and automatic Excel/PDF report generation at session completion.
"""

import os
import sys
import time
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from utils.config import (
    BASE_URL,
    BROWSERSTACK_USERNAME,
    BROWSERSTACK_ACCESS_KEY,
    REPORTS_DIR,
)
from utils.db_utils import init_db, log_test_result, get_all_results
from utils.report_utils import generate_all_reports

# Store test results during execution
_SESSION_TEST_RESULTS = []
_SESSION_START_TIME = datetime.now()


def pytest_configure(config):
    """Initializes Database at beginning of test run."""
    print("\n" + "=" * 75)
    print(" [BROWSERSTACK TESTATHON] Initializing Test Automation Suite")
    print(f" Target Application: {BASE_URL}")
    print("=" * 75)
    active_backend = init_db()
    print(f" [DB SYNC] Database active backend: {active_backend}")


@pytest.fixture(scope="function")
def driver(request):
    """
    Initializes WebDriver instance.
    - When executed via `browserstack-sdk pytest`, the SDK handles cloud routing.
    - When executed locally, initializes a local Chrome browser instance.
    """
    use_bstack = bool(BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY and os.getenv("FORCE_BSTACK"))

    options = ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Headless can be toggled via HEADLESS=1 env var
    if os.getenv("HEADLESS", "0") == "1":
        options.add_argument("--headless=new")

    if use_bstack:
        bstack_options = {
            "os": "Windows",
            "osVersion": "11",
            "browserName": "Chrome",
            "sessionName": request.node.name,
            "buildName": "BrowserStack Testathon Hackathon Build",
            "projectName": "webghzyt",
            "userName": BROWSERSTACK_USERNAME,
            "accessKey": BROWSERSTACK_ACCESS_KEY,
            "debug": "true",
            "networkLogs": "true",
            "consoleLogs": "info",
        }
        options.set_capability("bstack:options", bstack_options)
        _driver = webdriver.Remote(
            command_executor="https://hub-cloud.browserstack.com/wd/hub",
            options=options,
        )
    else:
        _driver = webdriver.Chrome(options=options)

    _driver.implicitly_wait(4)
    request.cls.driver = _driver if request.cls else None

    yield _driver

    try:
        _driver.quit()
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Captures test execution outcome, duration, and error trace."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        test_name = item.name
        # Extract category from parent module name or markers
        module_name = item.module.__name__ if hasattr(item, "module") else ""
        category = "General"
        if "functional" in module_name:
            category = "Functional & UI"
        elif "security" in module_name:
            category = "Security & Vulnerability"
        elif "performance" in module_name:
            category = "Performance & Reliability"
        elif "usability" in module_name:
            category = "Usability & Compliance"
        elif "specialized" in module_name:
            category = "Specialized & Infrastructure"

        status = "PASSED" if report.passed else ("FAILED" if report.failed else "SKIPPED")
        duration = float(report.duration)
        error_msg = str(report.longrepr) if report.failed else None
        if error_msg and len(error_msg) > 500:
            error_msg = error_msg[:500] + "..."

        browser_name = "Chrome (Windows 11)"
        session_id = f"BST-{int(_SESSION_START_TIME.timestamp())}"

        # Sync result to PostgreSQL / SQLite
        log_test_result(
            test_name=test_name,
            category=category,
            status=status,
            duration_seconds=duration,
            error_message=error_msg,
            browser_info=browser_name,
            session_id=session_id,
        )

        _SESSION_TEST_RESULTS.append({
            "test_name": test_name,
            "category": category,
            "status": status,
            "duration": duration,
        })


def pytest_sessionfinish(session, exitstatus):
    """Automatically generates Excel and PDF reports upon session finish."""
    print("\n" + "=" * 75)
    print(" [BROWSERSTACK TESTATHON] Session Finished - Generating Reports")
    print("=" * 75)

    try:
        report_files = generate_all_reports()
        print(f" [EXCEL REPORT] -> {report_files.get('excel')}")
        print(f" [PDF REPORT]   -> {report_files.get('pdf')}")
    except Exception as e:
        print(f" [ERROR] Could not generate reports: {e}")

    # Terminal summary
    total = len(_SESSION_TEST_RESULTS)
    passed = sum(1 for r in _SESSION_TEST_RESULTS if r["status"] == "PASSED")
    failed = sum(1 for r in _SESSION_TEST_RESULTS if r["status"] == "FAILED")
    print(f"\n >>> Summary: {total} Executed | {passed} Passed | {failed} Failed <<< \n")
