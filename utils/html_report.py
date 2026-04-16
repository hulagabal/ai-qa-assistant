def generate_html_report(report, ai_summary=None):
    import os
    from datetime import datetime

    os.makedirs("reports", exist_ok=True)

    status_color = "green" if report["status"] == "PASS" else "red"

    # 🎨 Performance color
    perf = report.get("performance", {})
    load_time = perf.get("load_time_sec", "N/A")
    rating = perf.get("rating", "N/A")

    if rating == "FAST":
        perf_color = "green"
    elif rating == "AVERAGE":
        perf_color = "orange"
    else:
        perf_color = "red"

    # 📊 Issues table
    issues_html = ""
    for issue in report["issues"]:
        issues_html += f"""
        <tr>
            <td>{issue['type']}</td>
            <td>{issue['details']}</td>
        </tr>
        """

    html_content = f"""
    <html>
    <head>
        <title>AI QA Report</title>
        <style>
            body {{
                font-family: Arial;
                background: #f4f6f8;
                padding: 20px;
            }}
            .container {{
                max-width: 900px;
                margin: auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                text-align: center;
            }}
            .status {{
                color: {status_color};
                font-weight: bold;
                font-size: 20px;
            }}
            .perf {{
                color: {perf_color};
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                word-break: break-all;
                overflow-wrap: anywhere;
                white-space: normal;
                max-width: 500px;
            }}
            th {{
                background: #f0f0f0;
            }}
            .section {{
                margin-top: 30px;
            }}
            pre {{
                background: #222;
                color: #0f0;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                white-space: pre-wrap;  
                word-break: break-word; 
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <h1>🚀 AI QA Test Report</h1>

            <p><strong>URL:</strong> {report['url']}</p>
            <p><strong>Timestamp:</strong> {report['timestamp']}</p>
            <p class="status">Status: {report['status']}</p>

            <div class="section">
                <h2>⚡ Performance</h2>
                <p>Load Time: <strong>{load_time} sec</strong></p>
                <p class="perf">Rating: {rating}</p>
            </div>

            <div class="section">
                <h2>📊 Issues</h2>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Details</th>
                    </tr>
                    {issues_html if issues_html else "<tr><td colspan='2'>No Issues 🎉</td></tr>"}
                </table>
            </div>

            <div class="section">
                <h2>🤖 Summary</h2>
                <pre>{ai_summary if ai_summary else "No summary available"}</pre>
            </div>

        </div>
    </body>
    </html>
    """

    file_name = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_content)

    return file_name