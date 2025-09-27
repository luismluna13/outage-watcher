import requests, json, datetime, os, webbrowser

ZIP_CODES = ["32801", "10001", "90001"]  # Orlando, NYC, LA

def fetch_xfinity_outage(zipcode):
    url = f"https://api.xfinity.com/outages-service/v1/location?zip={zipcode}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"Xfinity API returned {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def fetch_att_outage(zipcode):
    url = "https://www.att.com/outages/"
    try:
        r = requests.get(url, timeout=10)
        return {"note": "AT&T requires login, showing public outage page preview only",
                "html_preview": r.text[:300]}
    except Exception as e:
        return {"error": str(e)}

def check_outages():
    results = []
    now = datetime.datetime.now().isoformat()
    for zipc in ZIP_CODES:
        results.append({
            "zip": zipc,
            "time": now,
            "xfinity": fetch_xfinity_outage(zipc),
            "att": fetch_att_outage(zipc),
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
        "<tr><th>ZIP</th><th>Carrier</th><th>Result</th></tr>"
    ]
    for entry in data:
        for carrier, result in [("Xfinity", entry["xfinity"]), ("AT&T", entry["att"])]:
            html.append(f"<tr><td>{entry['zip']}</td><td>{carrier}</td><td><pre>{str(result)[:400]}</pre></td></tr>")
    html.append("</table></body></html>")

    html_path = "public/index.html"
    with open(html_path, "w") as f:
        f.write("\n".join(html))

    # Auto-open in browser
    webbrowser.open(html_path)

if __name__ == "__main__":
    outages = check_outages()
    save_reports(outages)
    print("✅ Outage reports saved and opened in browser")
