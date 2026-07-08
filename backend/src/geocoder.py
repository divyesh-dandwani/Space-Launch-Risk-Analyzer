import os
import csv
import time
import urllib.request
import urllib.parse
import json
import sys
import pandas as pd

# Ensure sibling src/ modules are in the Python search path regardless of startup cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RAW_DATA_PATH, SITES_MAPPING_PATH, SPACEPORT_COORDINATES

# Set stdout to UTF-8 to handle non-ASCII character logging on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def geocode_osm(location):
    """
    Fallback geocoder calling OpenStreetMap Nominatim.
    Tries the whole string, then strips off specific pad details if it fails.
    """
    queries = [location]
    if "," in location:
        parts = location.split(",")
        queries.append(",".join(parts[1:]))  # Remove pad details
        queries.append(",".join(parts[2:]))  # Keep only country/major region if still failing
        
    for query in queries:
        query = query.strip()
        if not query:
            continue
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "SpaceLaunchRiskAnalyzer/1.0 (antigravity-agent)"}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
                if data:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    print(f"OSM Geocoded: '{query}' -> ({lat}, {lon})")
                    return lat, lon
        except Exception as e:
            print(f"OSM Geocode error for '{query}': {e}")
        time.sleep(1.0)  # Rate limiting compliance
    return None

def build_sites_mapping():
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found at {RAW_DATA_PATH}. Please run downloader.py first.")

    print(f"Reading launch sites from: {RAW_DATA_PATH}")
    df = pd.read_csv(RAW_DATA_PATH)
    unique_sites = df["Location"].dropna().unique()
    print(f"Found {len(unique_sites)} unique launch sites.")

    mapping = []
    resolved_count = 0

    for site in unique_sites:
        site_lower = site.lower()
        coords = None

        # 1. Try specific pads first
        for pad in ["lc-39a", "slc-40", "slc-41", "slc-4e"]:
            if pad in site_lower:
                coords = SPACEPORT_COORDINATES[pad]
                break

        # 2. Try general spaceport keywords in config
        if not coords:
            for key, val in SPACEPORT_COORDINATES.items():
                if key in site_lower:
                    coords = val
                    break

        # 3. Fallback to OSM geocoding
        if not coords:
            print(f"Lookup failed for '{site}'. Falling back to OSM Geocoding...")
            coords = geocode_osm(site)

        if coords:
            mapping.append({
                "Location": site,
                "Latitude": coords[0],
                "Longitude": coords[1]
            })
            resolved_count += 1
        else:
            print(f"WARNING: Could not geocode site: '{site}'")
            # Default to (0.0, 0.0) or seasonal average, but let's log it
            mapping.append({
                "Location": site,
                "Latitude": 0.0,
                "Longitude": 0.0
            })

    print(f"Resolved {resolved_count}/{len(unique_sites)} launch sites.")

    # Save to CSV
    mapping_df = pd.DataFrame(mapping)
    mapping_df.to_csv(SITES_MAPPING_PATH, index=False)
    print(f"Saved site mappings to: {SITES_MAPPING_PATH}")

if __name__ == "__main__":
    build_sites_mapping()
