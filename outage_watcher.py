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

if __name__ == "__main__":
    outages = collect_outages()
    with open("us_outages.json", "w") as f:
        json.dump(outages, f, indent=2)
    print(f"Saved {len(outages)} outage summaries to us_outages.json")

