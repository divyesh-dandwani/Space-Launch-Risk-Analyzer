import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Ensure sibling src/ modules are in the Python search path regardless of startup cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ENRICHED_DATA_PATH, PREPROCESSORS_PATH

def clean_cost(val):
    if pd.isna(val):
        return np.nan
    val = str(val).strip().replace(",", "")
    try:
        return float(val)
    except ValueError:
        return np.nan

def calculate_running_success_rate(df, group_col, target_col="Success"):
    """
    Calculates the running success rate for a group (e.g., Company, Rocket, Site)
    up to the launch day, avoiding future lookahead bias.
    Formula: (Prior Successes + alpha * prior_success_rate) / (Prior Launches + alpha)
    using Laplace/Bayesian smoothing.
    """
    df = df.sort_values("Cleaned_Datetime").copy()
    
    # Calculate cumulative successes and launches before the current row
    grouped = df.groupby(group_col)
    
    cum_success = grouped[target_col].cumsum() - df[target_col]
    cum_launches = grouped.cumcount()
    
    # Global average success rate as prior
    global_prior = 0.85
    alpha = 5.0  # Smoothing parameter
    
    running_rate = (cum_success + alpha * global_prior) / (cum_launches + alpha)
    return running_rate

def preprocess_data(df=None, is_training=True, preprocessors=None):
    if df is None:
        df = pd.read_csv(ENRICHED_DATA_PATH)
        
    df = df.copy()
    
    # Ensure datetimes are parsed and sorted
    df["Cleaned_Datetime"] = pd.to_datetime(df["Cleaned_Datetime"])
    df = df.sort_values("Cleaned_Datetime").reset_index(drop=True)

    # 1. Target Label
    if "Status Mission" in df.columns:
        df["Success"] = df["Status Mission"].apply(lambda x: 1 if str(x).strip() == "Success" else 0)
    else:
        df["Success"] = np.nan

    # 2. Extract Country from Location
    df["Country"] = df["Location"].apply(lambda x: str(x).split(",")[-1].strip() if pd.notna(x) else "Unknown")

    # 3. Extract Rocket Name from Detail
    # Detail is e.g. "Falcon 9 Block 5 | Starlink V1 L9 & BlackSky"
    df["Rocket_Name"] = df["Detail"].apply(lambda x: str(x).split("|")[0].strip() if pd.notna(x) else "Unknown")

    # 4. Clean Rocket Cost
    df["Rocket_Cost"] = df[" Rocket"].apply(clean_cost)

    # 5. Extract Date components
    df["Launch_Year"] = df["Cleaned_Datetime"].dt.year
    df["Launch_Month"] = df["Cleaned_Datetime"].dt.month
    df["Launch_Day"] = df["Cleaned_Datetime"].dt.day
    df["Launch_Hour"] = df["Cleaned_Datetime"].dt.hour

    # 6. Engineer Running Success Rates (Historical Features)
    df["Company_Success_Rate"] = calculate_running_success_rate(df, "Company Name")
    df["Rocket_Success_Rate"] = calculate_running_success_rate(df, "Rocket_Name")
    df["Site_Success_Rate"] = calculate_running_success_rate(df, "Location")

    # Define features
    num_features = [
        "temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m",
        "wind_direction_10m", "wind_gusts_10m", "visibility", "cloud_cover", "precipitation", "dew_point_2m",
        "Rocket_Cost", "Launch_Year", "Launch_Month", "Launch_Hour",
        "Company_Success_Rate", "Rocket_Success_Rate", "Site_Success_Rate"
    ]
    
    cat_features = ["Company Name", "Location", "Rocket_Name", "Status Rocket", "Country"]

    # Impute missing values for numerical features
    # (Especially cost and weather values)
    if is_training:
        # Save training medians for inference
        medians = {}
        for col in num_features:
            medians[col] = float(df[col].median()) if df[col].notna().any() else 0.0
            df[col] = df[col].fillna(medians[col])
            
        # Category mappings
        cat_mappings = {}
        for col in cat_features:
            # Map unique strings to integers (plus unknown category)
            unique_cats = df[col].dropna().unique()
            mapping = {cat: idx for idx, cat in enumerate(unique_cats)}
            mapping["Unknown"] = len(unique_cats)
            cat_mappings[col] = mapping
            df[col] = df[col].map(mapping).fillna(mapping["Unknown"]).astype(int)
            
        # Fit scaler on numerical features
        scaler = StandardScaler()
        df[num_features] = scaler.fit_transform(df[num_features])
        
        preprocessors = {
            "medians": medians,
            "cat_mappings": cat_mappings,
            "scaler": scaler,
            "num_features": num_features,
            "cat_features": cat_features
        }
        
        # Save preprocessors
        joblib.dump(preprocessors, PREPROCESSORS_PATH)
        print(f"Saved preprocessors to: {PREPROCESSORS_PATH}")
        
    else:
        # Load / use preprocessors for inference
        if preprocessors is None:
            preprocessors = joblib.load(PREPROCESSORS_PATH)
            
        medians = preprocessors["medians"]
        cat_mappings = preprocessors["cat_mappings"]
        scaler = preprocessors["scaler"]
        
        # Apply numerical imputation
        for col in num_features:
            df[col] = df[col].fillna(medians.get(col, 0.0))
            
        # Apply categorical mappings
        for col in cat_features:
            mapping = cat_mappings[col]
            df[col] = df[col].map(lambda x: mapping.get(x, mapping["Unknown"])).astype(int)
            
        # Apply scaling
        df[num_features] = scaler.transform(df[num_features])

    # Keep only the features + target
    all_features = num_features + cat_features
    X = df[all_features]
    y = df["Success"]

    return X, y, preprocessors

def split_and_prepare():
    df = pd.read_csv(ENRICHED_DATA_PATH)
    
    # Sort chronologically to do temporal split
    df["Cleaned_Datetime"] = pd.to_datetime(df["Cleaned_Datetime"])
    df = df.sort_values("Cleaned_Datetime").reset_index(drop=True)
    
    X, y, preprocessors = preprocess_data(df, is_training=True)
    
    # Chronological Split (Train 70%, Val 15%, Test 15%)
    n = len(df)
    train_idx = int(n * 0.70)
    val_idx = int(n * 0.85)
    
    X_train, y_train = X.iloc[:train_idx], y.iloc[:train_idx]
    X_val, y_val = X.iloc[train_idx:val_idx], y.iloc[train_idx:val_idx]
    X_test, y_test = X.iloc[val_idx:], y.iloc[val_idx:]
    
    print(f"Splits prepared:")
    print(f" - Train: {X_train.shape[0]} rows")
    print(f" - Val: {X_val.shape[0]} rows")
    print(f" - Test: {X_test.shape[0]} rows")
    
    return X_train, y_train, X_val, y_val, X_test, y_test

if __name__ == "__main__":
    split_and_prepare()
