#!/bin/bash
set -e

echo "=============================================================================="
echo " BrowserStack Testathon - Automated Test Execution Runner (Linux/macOS)"
echo " Project: webghzyt | Target: https://bugbash.online/"
echo "=============================================================================="

# 1. Virtual Environment Setup
if [ ! -f ".venv/bin/python" ]; then
    echo "[INFO] Creating Python virtual environment in .venv..."
    python3 -m venv .venv
fi

echo "[INFO] Activating virtual environment..."
source .venv/bin/activate

# 2. Install Dependencies
echo "[INFO] Verifying / Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

# 3. Execute Pytest Suite via BrowserStack SDK
echo "=============================================================================="
echo " Launching Pytest Suite"
echo "=============================================================================="
browserstack-sdk pytest tests/ -v || echo "[WARN] Pytest completed with issues."

# 4. Generate & Verify Reports
echo "=============================================================================="
echo " Exporting Excel and PDF Reports"
echo "=============================================================================="
python -m utils.report_utils

echo ""
echo "=============================================================================="
echo " Execution Complete!"
echo " Reports available at:"
echo "   - Excel: reports/test_execution_report.xlsx"
echo "   - PDF:   reports/test_execution_report.pdf"
echo "=============================================================================="
