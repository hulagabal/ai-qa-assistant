import streamlit as st
from qa_engine import run_qa
from utils.html_report import generate_html_report

st.set_page_config(page_title="AI QA Assistant", layout="centered")

st.title("🚀 AI QA Assistant")
st.write("Enter a website URL and get QA + Performance report")

# Input

url = st.text_input("Enter URL", "https://example.com")

# Run button

if st.button("Run Test"):
st.info("Running QA checks... please wait ⏳")

try:
    # Run QA Engine
    report, summary = run_qa(url)

    # ✅ Status
    if report["status"] == "PASS":
        st.success("✅ Status: PASS")
    elif report["status"] == "BLOCKED":
        st.warning("🟡 Status: BLOCKED (Bot protection detected)")
    else:
        st.error("❌ Status: FAIL")

    # ⚡ Performance
    if "performance" in report:
        st.subheader("⚡ Performance")

        perf = report["performance"]

        st.metric(
            label="Page Load Time",
            value=f"{perf['load_time_sec']} sec"
        )

        if perf["rating"] == "FAST":
            st.success("🟢 Fast")
        elif perf["rating"] == "AVERAGE":
            st.warning("🟡 Average")
        else:
            st.error("🔴 Slow")

    # 📊 Issues
    st.subheader("📊 Issues")

    if report["issues"]:
        for issue in report["issues"]:
            if issue["type"] == "console":
                st.error(f"🖥️ Console → {issue['details']}")
            elif issue["type"] == "network":
                st.error(f"🌐 Network → {issue['details']}")
            elif issue["type"] == "security":
                st.warning(f"🛡️ Security → {issue['details']}")
            else:
                st.write(f"{issue['type']} → {issue['details']}")
    else:
        st.success("No issues found 🎉")

    # 🤖 Summary
    st.subheader("🤖 Summary")

    if not summary:
        summary = "No summary available"

    st.code(summary)

    # 📄 Generate HTML Report
    html_file = generate_html_report(report, summary)

    # Download button
    with open(html_file, "rb") as f:
        st.download_button(
            label="📄 Download HTML Report",
            data=f,
            file_name="qa_report.html",
            mime="text/html"
        )

except Exception as e:
    st.error(f"Test failed: {e}")
