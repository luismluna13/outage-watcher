import requests, json, datetime, os, subprocess
from bs4 import BeautifulSoup

ZIP_CODES = ["32801", "10001", "90001"]  # Orlando, NYC, LA

# Fallback Downdetector URLs
DOWNTIME_SITES = {
    "Spectrum": "https://downdetector.com/status/spectrum/",
    "Verizon": "https://downdetector.com/status/verizon/",
    "Lumen": "https://downdetector.com/status/centurylink/",
    "Windstream": "https://downdetector.com/status/windstream/"
}


def fetch_xfinity_outage(zipcode):
    api_url = f"https://api.xfinity.com/outages-service/v1/location?zip={zipcode}"
    public_url = "https://www.xfinity.com/support/statusmap"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    try:
        r = requests.get(api_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return {
                "summary": "See JSON details",
                "url": public_url,   # ✅ always link to official status page
                "raw": r.json()
            }
        else:
            return {"summary": f"Xfinity API returned {r.status_code}", "url": public_url}
    except Exception as e:
        return {"summary": f"Error: {e}", "url": public_url}



def fetch_att_outage(zipcode):
    url = "https://www.att.com/outages/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return {
            "summary": "AT&T requires login — showing public outage page preview",
            "url": url,
            "raw": r.text[:200]
        }
    except Exception as e:
        return {"summary": f"Error: {e}", "url": url}


def scrape_downdetector(name, url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)  # ✅ use headers
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        summary = soup.find("div", {"class": "entry-content"})
        return {
            "summary": summary.get_text(" ", strip=True) if summary else "No summary found",
            "url": url
        }
    except Exception as e:
        return {"summary": f"Error: {e}", "url": url}



def check_outages():
    results = []
    now = datetime.datetime.now().isoformat()

    # Zip-based carriers
    for zipc in ZIP_CODES:
        results.append({
            "zip": zipc,
            "carrier": "Xfinity",
            "time": now,
            "result": fetch_xfinity_outage(zipc)
        })
        results.append({
            "zip": zipc,
            "carrier": "AT&T",
            "time": now,
            "result": fetch_att_outage(zipc)
        })

    # Nationwide carriers (Downdetector)
    for name, url in DOWNTIME_SITES.items():
        results.append({
            "zip": "N/A",
            "carrier": name,
            "time": now,
            "result": scrape_downdetector(name, url)
        })

    return results


def save_reports(data):
    os.makedirs("public", exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # JSON
    with open("public/us_outages.json", "w") as f:
        json.dump(data, f, indent=2, default=str)

    # HTML
    html = [
        "<html><head><meta charset='utf-8'><title>US Outage Report</title></head><body>",
        f"<h1>US Outage Report – {now}</h1>",
        "<table border='1' cellpadding='6' cellspacing='0'>",
        "<tr><th>ZIP</th><th>Carrier</th><th>Result</th><th>Link</th></tr>"
    ]

    for entry in data:
        res = entry["result"]
        summary = res.get("summary", "N/A")
        link = f"<a href='{res['url']}' target='_blank'>Check Page</a>" if "url" in res else "N/A"
        html.append(
            f"<tr><td>{entry['zip']}</td><td>{entry['carrier']}</td><td>{summary}</td><td>{link}</td></tr>"
        )

    html.append("</table></body></html>")

    # Save HTML
    html_path = "public/index.html"
    with open(html_path, "w") as f:
        f.write("\n".join(html))

    # ✅ Guaranteed auto-open on macOS
    abs_path = os.path.abspath(html_path)
    subprocess.run(["open", abs_path])  # macOS native open


if __name__ == "__main__":
    outages = check_outages()
    save_reports(outages)
    print("✅ Outage reports saved and browser opened automatically")
