import requests, json, datetime, os, webbrowser
from bs4 import BeautifulSoup

CARRIERS = {
    "Comcast": "https://downdetector.com/status/xfinity/",
    "AT&T": "https://downdetector.com/status/att/",
    "Spectrum": "https://downdetector.com/status/spectrum/",
    "Verizon": "https://downdetector.com/status/verizon/",
    "Lumen": "https://downdetector.com/status/centurylink/",
    "Windstream": "https://downdetector.com/status/windstream/"
}

def scrape_downdetector(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    summary = soup.find("div", {"class": "entry-content"})
    return summary.get_text(" ", strip=True) if summary else "No summary found"

def collect_outages():
    results = []
    now = datetime.datetime.now().isoformat()
    for name, url in CARRIERS.items():
        try:
            text = scrape_downdetector(url)
            results.append({"carrier": name, "url": url, "summary": text, "timestamp": now})
        except Exception as e:
            results.append({"carrier": name, "url": url, "error": str(e), "timestamp": now})
    return results

def save_json_and_html(outages):
    os.makedirs("public", exist_ok=True)

    with open("public/us_outages.json", "w") as f:
        json.dump(outages, f, indent=2)

    html = ["<html><head><meta charset='utf-8'><title>US Outage Report</title></head><body>"]
    html.append(f"<h1>US Outage Report – {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>")
    html.append("<table border='1' cellpadding='6' cellspacing='0'><tr><th>Carrier</th><th>Summary</th><th>Link</th><th>Time</th></tr>")
    for o in outages:
        summary = o.get("summary") or o.get("error", "N/A")
        html.append(
            f"<tr><td>{o['carrier']}</td>"
            f"<td>{summary}</td>"
            f"<td><a href='{o['url']}'>Status Page</a></td>"
            f"<td>{o['timestamp']}</td></tr>"
        )
    html.append("</table></body></html>")
    with open("public/index.html", "w") as f:
        f.write("\n".join(html))

if __name__ == "__main__":
    outages = collect_outages()
    save_json_and_html(outages)
    print("Saved public/us_outages.json and public/index.html")
    # Auto-open in your default browser (Mac)
    webbrowser.open("public/index.html")
