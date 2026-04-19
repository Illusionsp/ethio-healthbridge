"""
Nearest Health Facility Finder using OpenStreetMap Overpass API.
No API key required — completely free.
"""
import httpx
from typing import List, Dict

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEALTH_AMENITIES = ["hospital", "clinic", "health_post", "doctors", "pharmacy"]


async def find_nearby_facilities(lat: float, lon: float, radius_m: int = 5000) -> List[Dict]:
    amenity_filter = "|".join(HEALTH_AMENITIES)

    # Compact single-line query — Overpass is picky about whitespace in GET params
    query = (
        f"[out:json][timeout:20];"
        f"("
        f'node["amenity"~"{amenity_filter}"](around:{radius_m},{lat},{lon});'
        f'way["amenity"~"{amenity_filter}"](around:{radius_m},{lat},{lon});'
        f");"
        f"out center 15;"
    )

    headers = {
        "User-Agent": "EthioHealthBridge/1.0 (health assistant app)",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            # Use GET with query as a URL parameter — most reliable for Overpass
            response = await client.get(
                OVERPASS_URL,
                params={"data": query},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

        facilities = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})

            # Prefer Amharic name, fall back to English, then generic label
            name = (
                tags.get("name:am")
                or tags.get("name")
                or tags.get("name:en")
                or "Unknown Facility"
            )
            amenity = tags.get("amenity", "health facility")

            # Nodes have lat/lon directly; ways expose a center point
            if element["type"] == "node":
                f_lat = element.get("lat")
                f_lon = element.get("lon")
            else:
                center = element.get("center", {})
                f_lat = center.get("lat")
                f_lon = center.get("lon")

            if f_lat is None or f_lon is None:
                continue

            dist_km = _haversine(lat, lon, f_lat, f_lon)

            facilities.append({
                "name": name,
                "type": _label(amenity),
                "lat": f_lat,
                "lon": f_lon,
                "distance_km": round(dist_km, 2),
                "maps_url": (
                    f"https://www.openstreetmap.org/"
                    f"?mlat={f_lat}&mlon={f_lon}#map=17/{f_lat}/{f_lon}"
                ),
            })

        facilities.sort(key=lambda x: x["distance_km"])
        return facilities[:8]

    except httpx.HTTPStatusError as e:
        print(f"Overpass HTTP error {e.response.status_code}: {e.response.text[:200]}")
        return []
    except Exception as e:
        print(f"Overpass API error: {e}")
        return []


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _label(amenity: str) -> str:
    return {
        "hospital": "Hospital",
        "clinic": "Clinic",
        "health_post": "Health Post",
        "doctors": "Doctor",
        "pharmacy": "Pharmacy",
    }.get(amenity, "Health Facility")
