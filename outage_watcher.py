import requests, json, datetime, os, subprocess
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

ZIP_CODES = ["32801"]  # Orlando for demo – you can add more

CARRIERS = {
    "Xfinity": {
        "official": "https://www.xfinity.com/support/statusmap",
        "api": "https://api.xfinity.com/outages-service/v1/location?zip={zip}",
        "fallback": {
            "Downdetector": "https://downdetector.com/status/xfinity/",
            "Outage.Report": "https://outage.report/us/xfinity",
            "IsTheServiceDown": "https://istheservicedown.com/problems/xfinity"
        }
    },
    "AT&T": {
        "official": "https://www.att.com/outages/",
        "fallback": {
            "Downdetector": "https://downdetector.com/status/att/",
            "Outage.Report": "https://outage.report/us/att",
            "IsTheServiceDown": "https://istheservicedown.com/problems/att"
        }
    },
    "Spectrum": {
        "official": "https://www.spectrum.net/support/internet-service-status/",
        "fallback": {
            "Downdetector": "https://downdetector.com/status/spectrum/",
            "Outage.Report": "https://outage.report/us/spectrum",
            "IsTheServiceDown": "https://istheservicedown.com/problems/spectrum"
        }
    },
    "Verizon": {
        "official": "https://www.verizon.com/support/outage/",
        "fallback": {
            "Downdetector": "https://downdetector.com/status/verizon/",
            "Outage.Report": "https://outage.report/us/verizon",
            "IsTheServiceDown": "https://istheservicedown.com/problems/verizon"
        }
    },
    "Lumen": {
        "official": "https://www.lumen.com/help/en-us/understanding-service-status.html",
        "fallback": {
            "Downdetector": "https://downdetector.com/status/centurylink/",
            "Outage.Report": "https://outage.report/us/centurylink",
            "IsTheServiceDown": "https://istheservicedown.com/problems/centurylink"
        }
    },
    "Windstream": {
        "official": "https://www.windstream.com/support/network-status",
        "fallback": {
            "Downdetector": "https://downdetector.com/status/windstream/",
            "Outage.Report": "https://outage.report/us/windstream",
            "IsTheServiceDown": "https://istheservicedown.com/problems/windstream"
        }
    }
}


def fetch_xfinity(zipc):
    url = CARRIERS["Xfinity"]["api"].format(zip=zipc)
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return f"See JSON details for {zipc}", CARRIERS["Xfinity"]["official"]
        else:
            return f"API returned {r.status_code}", CARRIERS["Xfinity"]["official"]
    except Exception as e:
        return f"Error: {e}", CARRIERS["Xfinity"]["official"]


def fetch_att():
    try:
        r = requests.get(CARRIERS["AT&T"]["official"], headers=HEADERS, timeout=10)
        return "AT&T requires login — showing public outage page preview", CARRIERS["AT&T"]["official"]
    except Exception as e:
        return f"Error: {e}", CARRIERS["AT&T"]["official"]


def scrape_fallback(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        summary = soup.find("div", {"class": "entry-content"})
        return summary.get_text(" ", strip=True) if summary else "No summary found"
    except Exception as e:
        return f"Error: {e}"


def check_outages():
    results = []
    now = datetime.datetime.now().isoformat()

    for zipc in ZIP_CODES:
        # Xfinity API
        summary, official = fetch_xfinity(zipc)
        results.append({
            "carrier": "Xfinity",
            "zip": zipc,
            "time": now,
            "summary": summary,
            "official": official,
            "fallback": CARRIERS["Xfinity"]["fallback"]
        })

    # AT&T (static)
    summary, official = fetch_att()
    results.append({
        "carrier": "AT&T",
        "zip": "N/A",
        "time": now,
        "summary": summary,
        "official": official,
        "fallback": CARRIERS["AT&T"]["fallback"]
    })

    # The rest (Spectrum, Verizon, Lumen, Windstream) via fallbacks only
    for name, data in CARRIERS.items():
        if name in ["Xfinity", "AT&T"]:
            continue
        results.append({
            "carrier": name,
            "zip": "N/A",
            "time": now,
            "summary": "See fallback links",
            "official": data["official"],
            "fallback": data["fallback"]
        })

    return results


def save_reports(data):
    os.makedirs("public", exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # JSON
    with open("public/us_outages.json", "w") as f:
        json.dump(data, f, indent=2)

    # HTML
    html = [
        "<html><head><meta charset='utf-8'><title>US Outage Report</title></head><body>",
        f"<h1>US Outage Report – {now}</h1>",
        "<table border='1' cellpadding='6' cellspacing='0'>",
        "<tr><th>Carrier</th><th>ZIP</th><th>Summary</th><th>Official</th><th>Fallbacks</th></tr>"
    ]

    for entry in data:
        fallbacks = " | ".join([f"<a href='{url}' target='_blank'>{name}</a>" for name, url in entry["fallback"].items()])
        html.append(
            f"<tr><td>{entry['carrier']}</td><td>{entry['zip']}</td>"
            f"<td>{entry['summary']}</td>"
            f"<td><a href='{entry['official']}' target='_blank'>Official</a></td>"
            f"<td>{fallbacks}</td></tr>"
        )

    html.append("</table></body></html>")

    html_path = "public/index.html"
    with open(html_path, "w") as f:
        f.write("\n".join(html))

    subprocess.run(["open", os.path.abspath(html_path)])  # macOS auto-open


if __name__ == "__main__":
    outages = check_outages()
    save_reports(outages)
    print("✅ Outage reports saved and browser opened automatically")
