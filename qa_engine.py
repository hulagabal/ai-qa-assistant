from playwright.sync_api import sync_playwright
import logging
import subprocess
import os

if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    subprocess.run(["playwright", "install", "chromium"])

logger = logging.getLogger(__name__)

def run_qa(url):
    console_errors = []
    network_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"])

        page = browser.new_page()

        # Console errors
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # Network errors
        page.on("requestfailed", lambda req: network_errors.append(f"{req.url} -> {req.failure}"))

        page.goto(url)

        title = page.title()
        links = page.locator("a").count()

        browser.close()

    report = {
        "url": url,
        "status": "PASS" if not console_errors and not network_errors else "FAIL",
        "issues": []
    }

    for err in console_errors:
        report["issues"].append({"type": "console", "details": err})

    for err in network_errors:
        report["issues"].append({"type": "network", "details": err})

    summary = f"{len(console_errors)} console errors, {len(network_errors)} network errors"

    return report, summary