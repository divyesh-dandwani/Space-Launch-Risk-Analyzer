import os
import time
import sys
import pandas as pd
import requests
import concurrent.futures
from threading import Lock

# Ensure sibling src/ modules are in the Python search path regardless of startup cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RAW_DATA_PATH, SITES_MAPPING_PATH, ENRICHED_DATA_PATH

# Set stdout to UTF-8 to handle non-ASCII character logging on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Global requests session for TCP connection reuse (connection pooling is thread-safe)
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=15, pool_maxsize=15)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Shared thread-safe metrics
weather_cache = {}
cache_lock = Lock()
success_count = 0
fail_count = 0
processed_count = 0
total_queries = 0
start_time = 0

def fetch_weather_for_day(lat, lon, date_str):
    """
    Fetches hourly weather data for a coordinate and date.
    Uses requests.Session for connection pooling and a 5-second timeout.
    """
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={date_str}&end_date={date_str}"
        f"&hourly=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,"
        f"wind_direction_10m,wind_gusts_10m,visibility,cloud_cover,precipitation,dew_point_2m"
    )
    try:
        response = session.get(
            url, 
            headers={"User-Agent": "SpaceLaunchRiskAnalyzer/1.0 (antigravity-agent)"},
            timeout=5.0
        )
        if response.status_code == 200:
            data = response.json()
            if "hourly" in data:
                return data["hourly"]
    except Exception:
        pass
    return None

def weather_worker(row):
    global success_count, fail_count, processed_count, start_time, total_queries
    lat, lon, date_str = row["Latitude"], row["Longitude"], row["Launch_Date"]
    
    if lat == 0.0 and lon == 0.0:
        return

    # Add a tiny staggered sleep to smooth out parallel requests
    time.sleep(0.05 * (idx_stagger := processed_count % 10))

    hourly_weather = fetch_weather_for_day(lat, lon, date_str)

    with cache_lock:
        processed_count += 1
        if hourly_weather:
            weather_cache[(lat, lon, date_str)] = hourly_weather
            success_count += 1
        else:
            fail_count += 1

        if processed_count % 100 == 0:
            elapsed = time.time() - start_time
            est_total = (elapsed / processed_count) * total_queries
            est_remaining = est_total - elapsed
            print(
                f"Progress: {processed_count}/{total_queries} queries | "
                f"Succeeded: {success_count} | Failed/Skipped: {fail_count} | "
                f"Elapsed: {elapsed:.1f}s | Est. Remaining: {est_remaining:.1f}s"
            )

def enrich_dataset():
    global start_time, total_queries, processed_count, success_count, fail_count, weather_cache
    
    if not os.path.exists(RAW_DATA_PATH) or not os.path.exists(SITES_MAPPING_PATH):
        raise FileNotFoundError("Raw launch data or site mappings CSV not found. Run downloader.py and geocoder.py first.")

    print("Loading datasets...")
    launches_df = pd.read_csv(RAW_DATA_PATH)
    sites_df = pd.read_csv(SITES_MAPPING_PATH)

    # Merge launches with coordinates
    df = pd.merge(launches_df, sites_df, on="Location", how="left")

    # Clean dates and extract date and hour
    print("Parsing launch datetimes...")
    df["Cleaned_Datetime"] = pd.to_datetime(df["Datum"], errors="coerce", utc=True)
    
    # Drop rows with invalid dates
    initial_rows = len(df)
    df = df.dropna(subset=["Cleaned_Datetime"])
    print(f"Dropped {initial_rows - len(df)} rows due to invalid date parsing.")

    df["Launch_Date"] = df["Cleaned_Datetime"].dt.strftime("%Y-%m-%d")
    df["Launch_Hour"] = df["Cleaned_Datetime"].dt.hour

    # Deduplicate by (Latitude, Longitude, Launch_Date) for weather API efficiency
    unique_queries = df.groupby(["Latitude", "Longitude", "Launch_Date"]).size().reset_index()
    total_queries = len(unique_queries)
    print(f"Need to query weather for {total_queries} unique (location, date) combinations.")

    print("Starting concurrent weather enrichment (Open-Meteo Archive with 10 threads)...")
    processed_count = 0
    success_count = 0
    fail_count = 0
    weather_cache = {}
    start_time = time.time()

    # Convert dataframe rows to list of dictionaries for executor
    rows = [row.to_dict() for _, row in unique_queries.iterrows()]

    # Use ThreadPoolExecutor to run queries in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(weather_worker, rows)

    print(f"Completed API requests. Succeeded: {success_count}, Failed/Skipped: {fail_count}.")

    # Map the weather back to the main dataframe
    print("Mapping weather features back to launches...")
    weather_vars = [
        "temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m",
        "wind_direction_10m", "wind_gusts_10m", "visibility", "cloud_cover", "precipitation", "dew_point_2m"
    ]

    # Initialize empty columns
    for var in weather_vars:
        df[var] = None

    for index, row in df.iterrows():
        lat, lon, date_str, hour = row["Latitude"], row["Longitude"], row["Launch_Date"], row["Launch_Hour"]
        cache_key = (lat, lon, date_str)
        
        if cache_key in weather_cache:
            hourly_data = weather_cache[cache_key]
            h_idx = int(hour) if 0 <= hour < 24 else 12
            
            for var in weather_vars:
                if var in hourly_data and h_idx < len(hourly_data[var]):
                    df.at[index, var] = hourly_data[var][h_idx]

    # Save enriched dataset
    df.to_csv(ENRICHED_DATA_PATH, index=False)
    print(f"Enriched dataset successfully created and saved to: {ENRICHED_DATA_PATH}")

if __name__ == "__main__":
    enrich_dataset()
