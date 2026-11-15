"""Fetch all pubs in Greater London + the Greater London boundary from Overpass."""
import json, requests, time

URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "30DayMapChallenge-pub-colors/1.0"}

def run(q, out):
    for attempt in range(4):
        r = requests.post(URL, data={"data": q}, headers=HEADERS, timeout=300)
        if r.status_code == 200:
            open(out, "w", encoding="utf-8").write(r.text)
            print(out, len(r.text) // 1024, "KB")
            return
        print("retry", r.status_code); time.sleep(15 * (attempt + 1))
    r.raise_for_status()

# Greater London = OSM relation 175342 (area id = 3600000000 + rel id)
run("""[out:json][timeout:240];
area(id:3600175342)->.a;
nwr["amenity"="pub"](area.a);
out center tags;""", "pubs_raw.json")

run("""[out:json][timeout:120];
rel(175342);
out geom;""", "london_boundary_raw.json")
