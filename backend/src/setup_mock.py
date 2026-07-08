import os
import sys
import numpy as np
import pandas as pd
import joblib

# Ensure sibling src/ modules are in the Python search path regardless of startup cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DATA_DIR, RAW_DATA_PATH, SITES_MAPPING_PATH, ENRICHED_DATA_PATH,
    BEST_MODEL_PATH, PREPROCESSORS_PATH, SPACEPORT_COORDINATES
)

def check_and_setup_mock():
    # If preprocessor and model already exist, do nothing
    if os.path.exists(BEST_MODEL_PATH) and os.path.exists(PREPROCESSORS_PATH):
        print("Model and preprocessor binaries exist. Skipping mock setup.")
        return

    print("Preprocessors/model not found. Generating mock training data...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # List of locations from config
    locations = list(SPACEPORT_COORDINATES.keys())
    num_launches = 500
    np.random.seed(42)
    
    data = []
    companies = ["SpaceX", "CASC", "Roscosmos", "ULA", "Arianespace", "ISRO", "NASA"]
    rockets = ["Falcon 9", "Long March 2D", "Proton-M", "Atlas V", "Ariane 5", "PSLV", "Saturn V"]
    statuses = ["StatusActive", "StatusRetired"]
    countries = ["USA", "China", "Kazakhstan", "French Guiana", "India", "Russia", "Japan"]
    
    # Generate dates
    start_date = pd.Timestamp("1960-01-01")
    end_date = pd.Timestamp("2020-08-01")
    date_range = (end_date - start_date).days
    
    for i in range(num_launches):
        days_to_add = np.random.randint(0, date_range)
        dt = start_date + pd.Timedelta(days=days_to_add)
        dt = dt.replace(hour=np.random.randint(0, 24))
        
        loc_key = np.random.choice(locations)
        coords = SPACEPORT_COORDINATES[loc_key]
        
        # Turn location key into pretty string format
        location_name = loc_key.replace("lc-", "LC-").replace("slc-", "SLC-").title()
        if "Space Center" not in location_name and len(location_name) < 15:
            location_name += " Cosmodrome"
            
        company = np.random.choice(companies)
        rocket = np.random.choice(rockets)
        status_rocket = np.random.choice(statuses)
        country = np.random.choice(countries)
        
        # Weather parameters (synthetic but physically realistic)
        temp = np.random.uniform(5, 35)  # Celsius
        humidity = np.random.uniform(20, 95)  # %
        pressure = np.random.uniform(980, 1030)  # hPa
        wind_speed = np.random.uniform(0, 45)  # km/h
        wind_dir = np.random.uniform(0, 360)
        wind_gust = wind_speed + np.random.uniform(0, 15)
        visibility = np.random.uniform(2, 16)  # km
        clouds = np.random.uniform(0, 100)  # %
        precip = np.random.exponential(0.5) if np.random.rand() > 0.8 else 0.0
        dew = temp - (100 - humidity) / 5.0
        
        cost = np.random.uniform(20, 250) if np.random.rand() > 0.4 else np.nan
        
        # Deterministic rules for target variables to let the model learn structure
        p_success = 0.90
        if wind_speed > 28:
            p_success -= 0.35  # High winds are dangerous
        if temp < 5:
            p_success -= 0.20  # Challenger cold O-ring risk
        if clouds > 90 and precip > 2.0:
            p_success -= 0.25  # Thunderstorms/heavy rain
        if company == "SpaceX":
            p_success += 0.05
        if status_rocket == "StatusRetired":
            p_success -= 0.05
            
        p_success = max(0.1, min(0.99, p_success))
        success = 1 if np.random.rand() < p_success else 0
        status_mission = "Success" if success == 1 else "Failure"
        
        data.append({
            "Location": location_name,
            "Datum": dt.strftime("%a %b %d, %Y %H:%M UTC"),
            "Cleaned_Datetime": dt,
            "Company Name": company,
            "Detail": f"{rocket} | Payload {i}",
            "Status Rocket": status_rocket,
            " Rocket": str(cost),
            "Status Mission": status_mission,
            "Latitude": coords[0],
            "Longitude": coords[1],
            "temperature_2m": temp,
            "relative_humidity_2m": humidity,
            "surface_pressure": pressure,
            "wind_speed_10m": wind_speed,
            "wind_direction_10m": wind_dir,
            "wind_gusts_10m": wind_gust,
            "visibility": visibility,
            "cloud_cover": clouds,
            "precipitation": precip,
            "dew_point_2m": dew
        })
        
    df = pd.DataFrame(data)
    df.to_csv(ENRICHED_DATA_PATH, index=False)
    
    # Save Space_Corrected.csv
    df[["Company Name", "Location", "Datum", "Detail", "Status Rocket", " Rocket", "Status Mission"]].to_csv(RAW_DATA_PATH, index=False)
    
    # Save sites_mapping.csv
    sites_mapping = df[["Location", "Latitude", "Longitude"]].drop_duplicates()
    sites_mapping.to_csv(SITES_MAPPING_PATH, index=False)
    
    # Import and run preprocessing + training
    from preprocess import preprocess_data
    X, y, preprocessors = preprocess_data(df, is_training=True)
    
    # Train random forest model
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X, y)
    
    os.makedirs(os.path.dirname(BEST_MODEL_PATH), exist_ok=True)
    joblib.dump(model, BEST_MODEL_PATH)
    print("Mock setup and training completed successfully. Model saved to disk.")

if __name__ == "__main__":
    check_and_setup_mock()
