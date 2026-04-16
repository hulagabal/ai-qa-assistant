from playwright.sync_api import sync_playwright
import logging

import json
from datetime import datetime
import time
import os

from pytest_check import check
from utils.html_report import generate_html_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def test_website(url="https://secure.netfirms.com/secure/login.html"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 🔥 Track issues
        console_errors = []
        network_errors = []

        try:
            page = browser.new_page()

            # ✅ Capture console errors
            def handle_console(msg):
                if msg.type == "error":
                    error = f"{msg.text}"
                    console_errors.append(error)
                    # logger.error(f"Console error: {error}")

            page.on("console", handle_console)

            # ✅ Capture network failures
            def handle_request_failed(request):
                error = f"{request.url} -> {request.failure}"
                network_errors.append(error)
                # logger.error(f"Network error: {error}")

            page.on("requestfailed", handle_request_failed)

            # 🌐 Open URL
            logger.info(f"Opening URL: {url}")
            start_time=time.time()
            response = page.goto(url)
            end_time=time.time()

            load_time= round(end_time- start_time, 2)
            logger.info(f" Page Load Time: {load_time} seconds")

            if load_time < 2:
                performance_status = "FAST"
            elif load_time < 5:
                performance_status = "AVERAGE"
            else:
                performance_status = "SLOW" 


            # ✅ Basic checks
            assert response is not None, "No response received"
            assert response.status == 200, f"Bad status: {response.status}"

            title = page.title()
            logger.info(f"Page title: {title}")
            assert title.strip() != "", "Title is empty"

            # ✅ Links check
            links = page.locator("a")
            count = links.count()
            logger.info(f"Total links found: {count}")
            assert count > 0, "No links found"

            # ✅ Safe loop
            for i in range(min(count, 5)):
                text = links.nth(i).inner_text()
                href = links.nth(i).get_attribute("href")
                logger.info(f"Link {i+1}: text='{text}', href='{href}'")

            # 🔥 FINAL QA ASSERTIONS (IMPORTANT)
            check.is_true(len(console_errors) == 0, f"Console errors found: {console_errors}")
            check.is_true(len(network_errors) == 0, f"Network errors found: {network_errors}")
            

            report, file_path = generate_json_report(url, console_errors, network_errors, load_time, performance_status)
            logger.info(f"JSON report saved: {file_path}")
            

            summary=get_summary(report)

            html_file = generate_html_report(report, summary)
            logger.info(f"HTML report generated: {html_file}")

            logger.info("AI Summary:\n" + summary)

            with open("reports/ai_summary.txt", "w",encoding="utf-8") as f:
                f.write(summary)

        except Exception as e:
            logger.error(f"Test failed: {e}")

            # 📸 Screenshot on failure
            page.screenshot(path="reports/error.png")
            logger.info("Screenshot saved to reports/error.png")

            raise

        finally:
            browser.close()   



def generate_json_report(url, console_errors, network_errors, load_time, performance_status):
    report = {
        "url": url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "PASS" if not console_errors and not network_errors else "FAIL",
        "performance": {
            "load_time_sec": load_time,
            "rating": performance_status
        },
        "issues": []
    }

    for err in console_errors:
        report["issues"].append({
            "type": "console",
            "details": err
        })

    for err in network_errors:
        report["issues"].append({
            "type": "network",
            "details": err
        })

    os.makedirs("reports", exist_ok=True)

    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report, filename


def generate_ai_summary(report):
    try:
        from openai import OpenAI

        client = OpenAI(api_key="openai_key")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Analyze this QA report:\n{report}"
            }]
        )

        return response.choices[0].message.content

    except Exception as e:

        if "quota" in str(e).lower():
            return "AI summary unavailable (quota exceeded)"
       
def get_summary(report):
    if report["status"] == "PASS":
        return "✅ No major issues detected.\n- No console errors\n- No network failures\n- Page loaded successfully"
    else:
        return generate_ai_summary(report)       

            