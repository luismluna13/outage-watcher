import requests, json, datetime
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
    for name, url in CARRIERS.items():
        try:
            text = scrape_downdetector(url)
            results.append({
                "carrier": name,
                "url": url,
                "summary": text,
                "timestamp": datetime.datetime.now().isoformat()
            })
        except Exception as e:
            results.append({
                "carrier": name,
                "url": url,
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            })
    return results

def save_as_html(outages):
    html = ["<html><head><title>US Outage Report</title></head><body>"]
    html.append(f"<h1>US Outage Report – {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>")
    html.append("<table border='1' cellpadding='5' cellspacing='0'>")
    html.append("<tr><th>Carrier</th><th>Summary</th><th>Link</th><th>Time</th></tr>")
    for o in outages:
        summary = o.get("summary") or o.get("error", "N/A")
        html.append(
            f"<tr><td>{o['carrier']}</td>"
            f"<td>{summary}</td>"
            f"<td><a href='{o['url']}'>Status Page</a></td>"
            f"<td>{o['timestamp']}</td></tr>"
        )
    html.append("</table></body></html>")
    with open("us_outages.html", "w") as f:
        f.write("\n".join(html))

if __name__ == "__main__":
    outages = collect_outages()
    with open("us_outages.json", "w") as f:
        json.dump(outages, f, indent=2)
    save_as_html(outages)
    print(f"Saved {len(outages)} outage summaries to us_outages.json and us_outages.html")
