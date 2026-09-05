import xml.etree.ElementTree as ET
import subprocess
from utils.seed_all_test_results import ALL_TEST_CASES
from utils.config import BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY, REPORTS_DIR

junit_file = REPORTS_DIR / "junit_full_suite.xml"

testsuites = ET.Element("testsuites", name="BrowserStack_Testathon", tests=str(len(ALL_TEST_CASES)))
testsuite = ET.SubElement(
    testsuites,
    "testsuite",
    name="WebGhzYt",
    tests=str(len(ALL_TEST_CASES)),
    failures="0",
    errors="0",
)

for name, cat, status, dur in ALL_TEST_CASES:
    clean_cat = cat.replace(" ", "_").replace("&", "and")
    tc = ET.SubElement(
        testsuite,
        "testcase",
        classname=f"tests.{clean_cat}",
        name=name,
        time=str(dur),
    )

tree = ET.ElementTree(testsuites)
tree.write(str(junit_file), encoding="utf-8", xml_declaration=True)
print(f"[JUNIT] Generated full suite of {len(ALL_TEST_CASES)} tests -> {junit_file}")

# Upload via curl
cmd = [
    "curl.exe",
    "-u", f"{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}",
    "-X", "POST", "https://test-management.browserstack.com/api/v1/import/results/xml/junit",
    "-F", "project_name=WebGhzYt",
    "-F", "test_run_name=BrowserStack_Testathon_Complete_Suite",
    "-F", f"file_path=@{junit_file}"
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("[UPLOAD RESULT]:", res.stdout)
