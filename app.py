import streamlit as st
import os
from datetime import datetime

# Import your existing logic
from utils.report_engine import generate_json_report, get_summary
from utils.html_report import generate_html_report
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="QA SaaS MVP", layout="centered")

st.title("🚀 Website QA Checker")
st.write("Run automated QA checks and generate reports in seconds")

# Input
url = st.text_input("Enter Website URL", "https://example.com")

# Run Test
if st.button("Run QA Test"):
    if not url.startswith("http"):
        st.error("Please enter a valid URL (include http/https)")
    else:
        st.info("Running QA checks... please wait")

        console_errors = []
        network_errors = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Capture console errors
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

                # Capture network errors
                def handle_request_failed(request):
                    error = request.failure.error_text if request.failure else "Unknown"
                    network_errors.append(f"{request.url} -> {error}")

                page.on("requestfailed", handle_request_failed)

                start_time = datetime.now()
                response = page.goto(url, wait_until="load", timeout=30000)
                end_time = datetime.now()

                load_time = round((end_time - start_time).total_seconds(), 2)

                if load_time < 2:
                    performance_status = "FAST"
                elif load_time < 5:
                    performance_status = "AVERAGE"
                else:
                    performance_status = "SLOW"

                # Basic checks
                status = "PASS"
                if not response or response.status >= 400:
                    status = "FAIL"

                title = page.title()

                # Generate report
                report, file_path = generate_json_report(
                    url, console_errors, network_errors, load_time, performance_status
                )

                summary = get_summary(report) or "No summary generated"
                html_file = generate_html_report(report, summary)

                browser.close()

                # UI Output
                st.success("QA Test Completed")

                st.subheader("📊 Results")
                st.write(f"Status: {status}")
                st.write(f"Load Time: {load_time} sec ({performance_status})")
                st.write(f"Page Title: {title}")

                st.subheader("⚠️ Issues Found")
                st.write(f"Console Errors: {len(console_errors)}")
                st.write(f"Network Errors: {len(network_errors)}")

                if console_errors:
                    st.code("\n".join(console_errors[:5]))

                if network_errors:
                    st.code("\n".join(network_errors[:5]))

                st.subheader("🤖 AI Summary")
                st.write(summary)

                # Download buttons
                with open(html_file, "rb") as f:
                    st.download_button("Download HTML Report", f, file_name=os.path.basename(html_file))

                with open(file_path, "rb") as f:
                    st.download_button("Download JSON Report", f, file_name=os.path.basename(file_path))

        except Exception as e:
            st.error(f"Test failed: {e}")
