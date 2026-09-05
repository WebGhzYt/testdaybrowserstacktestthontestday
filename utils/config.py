"""
Centralized Configuration Loader
Loads environment variables from .env or system environment.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Project Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

# Application Under Test
BASE_URL = os.getenv("BASE_URL", "https://bugbash.online/")
TEST_USER = os.getenv("TEST_USER", "demouser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testingisfun99")

# BrowserStack Credentials
BROWSERSTACK_USERNAME = os.getenv("BROWSERSTACK_USERNAME", "")
BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY", "")
BROWSERSTACK_LOCAL_IDENTIFIER = os.getenv("BROWSERSTACK_LOCAL_IDENTIFIER", "local_testathon_tunnel")
BROWSERSTACK_LOCAL_URL = os.getenv("BROWSERSTACK_LOCAL_URL", "")

# PostgreSQL Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Admin@123")

# API Testing Configuration
API_TEST_ENDPOINT = os.getenv("API_TEST_ENDPOINT", "https://httpbin.org/post")
API_TEST_USERNAME = os.getenv("API_TEST_USERNAME", "testathon_user")
API_TEST_PASSWORD = os.getenv("API_TEST_PASSWORD", "SecurePassword123!")
API_TEST_ROLL_NUMBER = os.getenv("API_TEST_ROLL_NUMBER", "BST-2026-9042")

# Reports Directory
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
