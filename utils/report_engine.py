from datetime import datetime
import json
import os


def generate_json_report(url, console_errors, network_errors, load_time, performance_status, status_code=None):

    now= datetime.now()
    

    if status_code is not None:
        if status_code == 403:
            final_status= "BLOCKED"
        elif status_code >= 500:
            final_status = "FAILED"
        elif status_code >= 400:
            final_status = "ERROR"
        else:
            final_status = "PASS"
    else:
        final_status = "PASS" if not console_errors and not network_errors else "FAIL"                   

    report = {
        "url": url,
        "timestamp": now.strftime("%d %b %Y, %I:%M %p"),
        "status": final_status,
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


    if status_code == 403:
        report.update({
            "protection_layer": "possible_waf_or_cloudflare",
            "reason": "Access forbidden (bot protection / permission issue)",
            "next_steps": [
                "Run test in non-headless mode",
                "Check authentication or login",
                "Whitelist IP in firewall",
                "Test manually in browser"
            ]
        
        })


    os.makedirs("reports", exist_ok=True)

    filename = f"reports/report_{now.strftime("%Y%m%d_%H%M%S")}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
    except Exception as e:
        print(f"Failed to save report: {e}")
        filename=None

    return report, filename


def generate_ai_summary(report):
    status=report.get("status")
    issues = report.get("issues", [])
    
    if not issues:
        return "✅ No issues detected."
    
    summary = "🚨 AI QA Summary:\n"

    if status == "BLOCKED":
        return (
            "🚫 Access Blocked (403 Forbidden)\n\n"
            "🔐 Protection Layer Detected: Possible WAF / Cloudflare\n\n"
            "📌 Reason:\n"
            "- Access forbidden (bot protection / permission issue)\n\n"
            "🛠️ Recommended Actions:\n"
            "- Run test in non-headless mode\n"
            "- Check authentication or login\n"
            "- Whitelist test IP in firewall\n"
            "- Test manually in browser\n"
        )

    for issue in issues[:5]:  # limit noise
        summary += f"- [{issue['type']}] {issue['details'][:100]}\n"

    summary += "\nSuggested Actions:\n"

    if any(i["type"] == "network" for i in issues):
        summary += "- Check API endpoints / server availability\n"

    if any(i["type"] == "console" for i in issues):
        summary += "- Fix JavaScript errors in frontend\n"

    return summary
        
       
def get_summary(report):
    if report["status"] == "PASS":
        return "✅ No major issues detected.\n- No console errors\n- No network failures\n- Page loaded successfully"
    else:
        return generate_ai_summary(report)
