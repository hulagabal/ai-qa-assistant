from playwright.sync_api import sync_playwright
import logging

import json
from datetime import datetime
import time
from utils.report_engine import generate_json_report, get_summary  


from pytest_check import check
from utils.html_report import generate_html_report


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def test_website(url="https://secure.netfirms.com/secure/login.bml"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Track issues
        console_errors = []
        network_errors = []

        try:
            page = browser.new_page()

            # Capture console errors
            def handle_console(msg):
                if msg.type == "error":
                    error = f"{msg.text}"
                    console_errors.append(error)
                    # logger.error(f"Console error: {error}")

            page.on("console", handle_console)

            # Capture network failures
            def handle_request_failed(request):
                error = f"{request.url} -> {request.failure}"
                network_errors.append(error)
                # logger.error(f"Network error: {error}")

            page.on("requestfailed", handle_request_failed)

            # Open URL
            logger.info(f"Opening URL: {url}")
            start_time=time.time()
            response = page.goto(url, wait_until="load")
            end_time=time.time()

            load_time= round(end_time- start_time, 2)

            if load_time < 2:
                performance_status = "FAST"
            elif load_time < 5:
                performance_status = "AVERAGE"
            else:
                performance_status = "SLOW" 

            status_code=response.status

            title = page.title()
            logger.info(f"Paga loaded", extra={"title": title, "load_time":load_time})
            assert title.strip() != "", "Title is empty"

            # Links check
            links = page.locator("a")
            count = links.count()
            logger.info(f"Total links found: {count}")
            assert count > 0, "No links found"

            # Safe loop
            for i in range(min(count, 5)):
                text = links.nth(i).inner_text() or ""
                href = links.nth(i).get_attribute("href")
                logger.info(f"Link {i+1}: text='{text}', href='{href}'")

            # FINAL QA ASSERTIONS (IMPORTANT)
            check.is_true(len(console_errors) == 0, f"Console errors found: {console_errors}")
            check.is_true(len(network_errors) == 0, f"Network errors found: {network_errors}")
            

            report, file_path = generate_json_report(url, console_errors, network_errors,load_time, performance_status, status_code)
            logger.info(f"JSON report saved: {file_path}")
            

            summary=get_summary(report) or "No summary generated"

            html_file = generate_html_report(report, summary)
            logger.info(f"HTML report generated: {html_file}")

            logger.info("AI Summary:\n" + summary)

            filename= f"reports/ai_summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w",encoding="utf-8") as f:
                f.write(summary)

            logger.info(f"ai summary report created {filename}")

        except Exception as e:
            logger.error(f"Test failed: {e}")

            # Screenshot on failure
            filename = f"reports/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=filename)
            logger.info(f"Screenshot saved to reports/{filename}")

            raise

        finally:
            browser.close()   
