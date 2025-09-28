import requests, json, datetime, os, subprocess
from bs4 import BeautifulSoup

# ✅ Headers for all requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

ZIP_CODES = ["32801"]  # Orlando for demo – add more ZIPs if needed

# 🌐 Carriers with all 3 fallback sources
CARRIERS = {
    "Xfinity": {
        "official": "https://www.xfinity.com/support/statusmap",
        "downdetector": "https://downdetector.com/status/xfinity/",
        "outage_report": "https://outage.report/us/xfinity",
        "istheservicedown": "https://istheservicedown.com/problems/xfinity",
    },
    "AT&T": {
        "official": "https://www.att.com/outages/",
        "downdetector": "https://downdetector.com/status/att/",
        "outage_report": "https://outage.report/us/att",
        "istheservicedown": "https://istheservicedown.com/problems/att",
    },
    "Spectrum": {
        "official": "https://www.spectrum.net/support/internet-service-status/",
        "downdetector": "https://downdetector.com/status/spectrum/",
        "outage_report": "https://outage.report/us/spectrum",
        "istheservicedown": "https://istheservicedown.com/problems/spectrum",
    },
    "Verizon": {
        "official": "https://www.verizon.com/support/outage/",
        "downdetector": "https://downdetector.com/status/verizon/",
        "outage_report": "https://outage.report/us/verizon",
        "istheservicedown": "https://istheservicedown.com/problems/verizon",
    },
    "Lumen": {
        "official": "https://www.lumen.com/help/en-us/understanding-service-status.html",
        "downdetector": "https://downdetector.com/status/centurylink/",
        "outage_report": "https://outage.report/us/centurylink",
        "istheservicedown": "https://istheservicedown.com/problems/centurylink",
    },
    "Windstream": {
        "official": "https://www.windstream.com/support/network-status",
        "downdetector": "https://downdetector.com/status/windstream/",
        "outage_report": "https://outage.report/us/windstream",
        "istheservicedown": "https://istheservicedown.com/problems/windstream",
    }
}


def fetch_xfinity_outage(zipcode):
    api_url = f"https://api.xfinity.com/outages-service/v1/location?zip={zipcode}"
    public_url = CARRIERS["Xfinity"]["official"]
    try:
        r = requests.get(api_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return {"summary": "See JSON details", "url": public_url, "raw": r.json()}
        else:
            return {"summary": f"Xfinity API returned {r.status_code}", "url": public_url}
    except Exception as e:
        return {"summary": f"Error: {e}", "url": public_url}


def fetch_att_outage(zipcode):
    url = CARRIERS["AT&T"]["official"]
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return {"summary": "AT&T requires login — showing public outage page preview", "url": url}
    except Exception as e:
        return {"summary": f"Error: {e}", "url": url}


def check_outages():
    results = []
    now = datetime.datetime.now().isoformat()

    # ZIP-based first
    for zipc in ZIP_CODES:
        results.append({
            "carrier": "Xfinity",
            "zip": zipc,
            "time": now,
            "result": fetch_xfinity_outage(zipc)
        })
        results.append({
            "carrier": "AT&T",
            "zip": "N/A",
            "time": now,
            "result": fetch_att_outage(zipc)
        })

    # Nationwide carriers
    for name in ["Spectrum", "Verizon", "Lumen", "Windstream"]:
        results.append({
            "carrier": name,
            "zip": "N/A",
            "time": now,
            "result": {"summary": "See fallback links", "url": CARRIERS[name]["official"]}
        })

    return results


def save_reports(data):
    os.makedirs("public", exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # JSON
    with open("public/us_outages.json", "w") as f:
        json.dump(data, f, indent=2, default=str)

    # HTML
    html_path = "public/index.html"
    html = [
        "<html><head><meta charset='utf-8'><title>US Outage Report</title></head><body>",
        f"<h1>US Outage Report – {now}</h1>",
        "<table border='1' cellpadding='6' cellspacing='0'>",
        "<tr><th>Carrier</th><th>ZIP</th><th>Summary</th><th>Official</th><th>Fallbacks</th></tr>"
    ]

    for entry in data:
        res = entry["result"]
        summary = res.get("summary", "N/A")
        links = CARRIERS[entry["carrier"]]

        official = f"<a href='{links['official']}' target='_blank'>Official</a>"
        fallbacks = (
            f"<a href='{links['downdetector']}' target='_blank'>Downdetector</a> | "
            f"<a href='{links['outage_report']}' target='_blank'>Outage.Report</a> | "
            f"<a href='{links['istheservicedown']}' target='_blank'>IsTheServiceDown</a>"
        )

        html.append(
            f"<tr><td>{entry['carrier']}</td><td>{entry['zip']}</td><td>{summary}</td><td>{official}</td><td>{fallbacks}</td></tr>"
        )

    html.append("</table></body></html>")

    with open(html_path, "w") as f:
        f.write("\n".join(html))

    # Auto-open locally
    abs_path = os.path.abspath(html_path)
    subprocess.run(["open", abs_path])


if __name__ == "__main__":
    outages = check_outages()
    save_reports(outages)
    print("✅ Outage reports saved and browser opened automatically")
