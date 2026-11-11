import math
import time
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "JalRakshak-student-project/1.0 (final-year project, Odisha)"}


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def find_shelters(lat, lon, radius_m=15000, top_n=5):
    """OpenStreetMap se nearby schools, hospitals, shelters. Ye OSM data hai, official OSDMA list nahi."""
    q = f"""
    [out:json][timeout:25];
    (
      nwr["amenity"="shelter"](around:{radius_m},{lat},{lon});
      nwr["emergency"="assembly_point"](around:{radius_m},{lat},{lon});
      nwr["amenity"="hospital"](around:{radius_m},{lat},{lon});
      nwr["amenity"="school"](around:{radius_m},{lat},{lon});
    );
    out center;
    """
    r = None
    for attempt in range(3):
        r = requests.post(OVERPASS_URL, data={"data": q}, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            break
        time.sleep(3 * (attempt + 1))
    r.raise_for_status()

    out = []
    for el in r.json().get("elements", []):
        c = el.get("center") or {"lat": el.get("lat"), "lon": el.get("lon")}
        if c["lat"] is None:
            continue
        tags = el.get("tags", {})
        out.append({
            "name": tags.get("name", "(naam nahi)"),
            "type": tags.get("amenity") or tags.get("emergency") or "place",
            "lat": c["lat"], "lon": c["lon"],
            "dist_km": round(_haversine_km(lat, lon, c["lat"], c["lon"]), 2),
        })
    out.sort(key=lambda s: s["dist_km"])
    return out[:top_n]