import os
import sys
import json
import urllib.request
import urllib.parse

# Ensure sibling src/ modules are in the Python search path regardless of startup cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
from contextlib import asynccontextmanager

from config import (
    BEST_MODEL_PATH, PREPROCESSORS_PATH, SITES_MAPPING_PATH, RAW_DATA_PATH, ENRICHED_DATA_PATH
)
from setup_mock import check_and_setup_mock
from preprocess import preprocess_data

# Global state
model = None
preprocessors = None
sites_df = None
raw_df = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, preprocessors, sites_df, raw_df
    print("FastAPI Backend starting up...")
    
    # Ensure dataset and trained models exist (auto-fallback to mock if skipped)
    try:
        check_and_setup_mock()
    except Exception as e:
        print(f"Error during self-healing setup: {e}")
        
    # Load model and preprocessors
    if os.path.exists(BEST_MODEL_PATH):
        model = joblib.load(BEST_MODEL_PATH)
        print(f"Model loaded successfully from {BEST_MODEL_PATH}")
    else:
        print(f"ERROR: Model not found at {BEST_MODEL_PATH}")

    if os.path.exists(PREPROCESSORS_PATH):
        preprocessors = joblib.load(PREPROCESSORS_PATH)
        print(f"Preprocessors loaded successfully from {PREPROCESSORS_PATH}")
    else:
        print(f"ERROR: Preprocessors not found at {PREPROCESSORS_PATH}")

    if os.path.exists(SITES_MAPPING_PATH):
        sites_df = pd.read_csv(SITES_MAPPING_PATH)
        print("Sites mapping loaded.")
    else:
        print("WARNING: Sites mapping not found.")

    if os.path.exists(RAW_DATA_PATH):
        raw_df = pd.read_csv(RAW_DATA_PATH)
        print("Raw launches dataset loaded.")
    else:
        print("WARNING: Raw dataset not found.")

    yield
    print("FastAPI Backend shutting down...")

app = FastAPI(title="Space Launch Risk Analyzer API", lifespan=lifespan)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("="*60)
    print("VALIDATION ERROR DETECTED:")
    print(exc.errors())
    print("Body:", exc.body)
    print("="*60)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

class PredictionRequest(BaseModel):
    site: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    rocket: str
    company: str
    payload_type: str
    rocket_cost: float = None
    override_weather: bool = False
    temperature_2m: float = None
    relative_humidity_2m: float = None
    surface_pressure: float = None
    wind_speed_10m: float = None
    wind_direction_10m: float = None
    wind_gusts_10m: float = None
    visibility: float = None
    cloud_cover: float = None
    precipitation: float = None
    dew_point_2m: float = None

def fetch_weather_data(lat: float, lon: float, date_str: str, hour: int):
    """
    Fetches weather data for coordinates and date.
    Uses Archive API for past dates (> 7 days ago) or Forecast API for future/recent dates.
    """
    # Calculate difference from today
    today = pd.Timestamp.now().normalize()
    target_date = pd.to_datetime(date_str).normalize()
    days_diff = (target_date - today).days

    # Decide between Archive and Forecast
    if days_diff < -7:
        url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={lat}&longitude={lon}&start_date={date_str}&end_date={date_str}"
            f"&hourly=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,"
            f"wind_direction_10m,wind_gusts_10m,visibility,cloud_cover,precipitation,dew_point_2m"
        )
        api_type = "Archive"
    else:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&start_date={date_str}&end_date={date_str}"
            f"&hourly=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,"
            f"wind_direction_10m,wind_gusts_10m,visibility,cloud_cover,precipitation,dew_point_2m"
        )
        api_type = "Forecast"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SpaceLaunchRiskAnalyzer/1.0"})
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if "hourly" in res_data:
                hourly = res_data["hourly"]
                h_idx = hour if 0 <= hour < len(hourly["time"]) else 12
                
                weather = {}
                vars_to_extract = [
                    "temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m",
                    "wind_direction_10m", "wind_gusts_10m", "visibility", "cloud_cover", "precipitation", "dew_point_2m"
                ]
                for var in vars_to_extract:
                    if var in hourly:
                        weather[var] = hourly[var][h_idx]
                    else:
                        weather[var] = 0.0
                weather["api_used"] = api_type
                return weather
    except Exception as e:
        print(f"Weather API Fetch Error ({api_type}): {e}")
        # Return fallback weather values
        return {
            "temperature_2m": 22.0,
            "relative_humidity_2m": 50.0,
            "surface_pressure": 1013.0,
            "wind_speed_10m": 12.0,
            "wind_direction_10m": 180.0,
            "wind_gusts_10m": 15.0,
            "visibility": 10.0,
            "cloud_cover": 30.0,
            "precipitation": 0.0,
            "dew_point_2m": 12.0,
            "api_used": f"Fallback due to error ({e})"
        }

@app.get("/api/sites")
async def get_sites():
    if sites_df is not None:
        # Group and take the first record to make it clean
        sites_list = []
        for _, row in sites_df.iterrows():
            sites_list.append({
                "name": row["Location"],
                "lat": float(row["Latitude"]),
                "lon": float(row["Longitude"])
            })
        return sorted(sites_list, key=lambda x: x["name"])
    return []

@app.get("/api/rockets")
async def get_rockets():
    if raw_df is not None:
        # Extract unique rockets and companies
        # Raw dataset details format: "Falcon 9 | Starlink"
        unique_rockets = set()
        unique_companies = set(raw_df["Company Name"].dropna().unique())
        
        for detail in raw_df["Detail"].dropna():
            rocket_name = str(detail).split("|")[0].strip()
            unique_rockets.add(rocket_name)
            
        return {
            "rockets": sorted(list(unique_rockets)),
            "companies": sorted(list(unique_companies))
        }
    return {"rockets": [], "companies": []}

@app.post("/api/predict")
async def predict_risk(req: PredictionRequest):
    global model, preprocessors, sites_df
    
    if model is None or preprocessors is None:
        raise HTTPException(status_code=500, detail="Machine learning models are not loaded.")

    # 1. Coordinate lookup
    lat, lon = 0.0, 0.0
    if sites_df is not None:
        site_match = sites_df[sites_df["Location"] == req.site]
        if not site_match.empty:
            lat = float(site_match.iloc[0]["Latitude"])
            lon = float(site_match.iloc[0]["Longitude"])
    
    # 2. Parse date and hour
    try:
        dt = pd.to_datetime(f"{req.date} {req.time}")
        hour = dt.hour
        year = dt.year
        month = dt.month
        day = dt.day
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date or time format.")

    # 3. Fetch weather from Open-Meteo (or use overrides)
    if req.override_weather:
        weather = {
            "temperature_2m": req.temperature_2m if req.temperature_2m is not None else 20.0,
            "relative_humidity_2m": req.relative_humidity_2m if req.relative_humidity_2m is not None else 50.0,
            "surface_pressure": req.surface_pressure if req.surface_pressure is not None else 1013.0,
            "wind_speed_10m": req.wind_speed_10m if req.wind_speed_10m is not None else 12.0,
            "wind_direction_10m": req.wind_direction_10m if req.wind_direction_10m is not None else 180.0,
            "wind_gusts_10m": req.wind_gusts_10m if req.wind_gusts_10m is not None else 15.0,
            "visibility": req.visibility if req.visibility is not None else 10.0,
            "cloud_cover": req.cloud_cover if req.cloud_cover is not None else 30.0,
            "precipitation": req.precipitation if req.precipitation is not None else 0.0,
            "dew_point_2m": req.dew_point_2m if req.dew_point_2m is not None else 12.0,
            "api_used": "Manual Override"
        }
    else:
        weather = fetch_weather_data(lat, lon, req.date, hour)
    
    # 4. Prepare preprocessed variables
    # For historical feature rates, lookup latest averages or defaults
    # Let's see: we calculate running success rates. Since this is a new prediction,
    # we can lookup the overall historical success rates of the selected company, rocket, and site.
    
    # Load enriched data to extract average success rates
    comp_rate = 0.85
    rock_rate = 0.85
    site_rate = 0.85
    
    if os.path.exists(ENRICHED_DATA_PATH):
        try:
            temp_df = pd.read_csv(ENRICHED_DATA_PATH)
            
            # Simple average successes
            temp_df["Success"] = temp_df["Status Mission"].apply(lambda x: 1 if str(x).strip() == "Success" else 0)
            
            c_df = temp_df[temp_df["Company Name"] == req.company]
            if not c_df.empty:
                comp_rate = c_df["Success"].mean()
                
            rocket_name_clean = req.rocket.split("|")[0].strip()
            temp_df["Rocket_Name_Clean"] = temp_df["Detail"].apply(lambda x: str(x).split("|")[0].strip() if pd.notna(x) else "Unknown")
            r_df = temp_df[temp_df["Rocket_Name_Clean"] == rocket_name_clean]
            if not r_df.empty:
                rock_rate = r_df["Success"].mean()
                
            s_df = temp_df[temp_df["Location"] == req.site]
            if not s_df.empty:
                site_rate = s_df["Success"].mean()
        except Exception as ex:
            print(f"Error calculating stats: {ex}")

    # Build input DataFrame
    input_data = pd.DataFrame([{
        "Location": req.site,
        "Datum": dt.strftime("%a %b %d, %Y %H:%M UTC"),
        "Cleaned_Datetime": dt,
        "Company Name": req.company,
        "Detail": f"{req.rocket} | Payload",
        "Status Rocket": "StatusActive",
        " Rocket": str(req.rocket_cost) if req.rocket_cost is not None else np.nan,
        "Latitude": lat,
        "Longitude": lon,
        "temperature_2m": weather["temperature_2m"],
        "relative_humidity_2m": weather["relative_humidity_2m"],
        "surface_pressure": weather["surface_pressure"],
        "wind_speed_10m": weather["wind_speed_10m"],
        "wind_direction_10m": weather["wind_direction_10m"],
        "wind_gusts_10m": weather["wind_gusts_10m"],
        "visibility": weather["visibility"],
        "cloud_cover": weather["cloud_cover"],
        "precipitation": weather["precipitation"],
        "dew_point_2m": weather["dew_point_2m"],
        "Launch_Year": year,
        "Launch_Month": month,
        "Launch_Day": day,
        "Launch_Hour": hour,
        "Company_Success_Rate": comp_rate,
        "Rocket_Success_Rate": rock_rate,
        "Site_Success_Rate": site_rate
    }])

    # 5. Preprocess
    X_inference, _, _ = preprocess_data(input_data, is_training=False, preprocessors=preprocessors)
    
    # 6. Predict baseline success probability using ML
    prob_success = float(model.predict_proba(X_inference)[0, 1])
    
    # Enforce Launch Safety Envelope (LSE) weather constraints
    # (Proportionate risk management matching FAA/NASA Launch Commit Criteria)
    wind = weather["wind_speed_10m"]
    precip = weather["precipitation"]
    temp = weather["temperature_2m"]
    visibility = weather["visibility"]
    clouds = weather["cloud_cover"]
    humidity = weather["relative_humidity_2m"]

    # Calculate individual penalty rates based on physical risk thresholds
    wind_penalty = 0.0
    if wind > 40.0:
        wind_penalty = 0.70  # Critical aerodynamic shear (hard limit)
    elif wind > 28.0:
        wind_penalty = 0.35  # High shear warning
    elif wind > 18.0:
        wind_penalty = 0.12  # Mild wind stress

    precip_penalty = 0.0
    if precip > 2.0:
        precip_penalty = 0.65  # Heavy active rain/snow (hard limit)
    elif precip > 0.1:
        precip_penalty = 0.30  # Moisture accumulation warning

    temp_penalty = 0.0
    if temp < 2.0:
        temp_penalty = 0.65  # Critical cold temperature (Challenger O-ring limit)
    elif temp < 7.0:
        temp_penalty = 0.25  # Cold soak advisory
    elif temp > 38.0:
        temp_penalty = 0.15  # Thermal dissipation limit

    vis_penalty = 0.0
    if visibility < 3.0:
        vis_penalty = 0.60  # Visual tracking failure (hard limit)
    elif visibility < 7.0:
        vis_penalty = 0.25  # Reduced tracking capability

    cloud_lightning_penalty = 0.0
    if clouds > 90.0 and (precip > 0.0 or humidity > 85.0):
        cloud_lightning_penalty = 0.35  # Charged cumulus triggered lightning index
    elif clouds > 95.0:
        cloud_lightning_penalty = 0.15  # Heavy overcast ceiling

    # Apply penalties sequentially in a multiplicative fashion to prevent negative results
    prob_success *= (1.0 - wind_penalty)
    prob_success *= (1.0 - precip_penalty)
    prob_success *= (1.0 - temp_penalty)
    prob_success *= (1.0 - vis_penalty)
    prob_success *= (1.0 - cloud_lightning_penalty)

    # Force a minimum probability floor of 3.0% under catastrophic launch conditions
    prob_success = max(0.03, prob_success)

    risk_score = round((1.0 - prob_success) * 100, 1)
    success_score = round(prob_success * 100, 1)
    
    # Determine risk level
    if risk_score <= 20.0:
        risk_level = "Low"
        risk_color = "#10B981"  # Emerald green
    elif risk_score <= 50.0:
        risk_level = "Medium"
        risk_color = "#F59E0B"  # Amber orange
    else:
        risk_level = "High"
        risk_color = "#EF4444"  # Crimson red

    # 7. Contributing Factors Explanation
    # We analyze which features deviate from normal (training medians)
    contributing_factors = []
    medians = preprocessors["medians"]
    
    # Check Wind Speed
    wind = weather["wind_speed_10m"]
    median_wind = medians.get("wind_speed_10m", 12.0)
    if wind > 25.0:
        contributing_factors.append({
            "factor": "High Wind Speed",
            "impact": "Negative",
            "description": f"Wind speeds are {wind:.1f} km/h, significantly higher than the typical median of {median_wind:.1f} km/h, increasing aerodynamic stress."
        })
    elif wind < 5.0:
        contributing_factors.append({
            "factor": "Calm Winds",
            "impact": "Positive",
            "description": f"Wind speeds are calm ({wind:.1f} km/h), providing excellent launch stability."
        })
        
    # Check Temp
    temp = weather["temperature_2m"]
    median_temp = medians.get("temperature_2m", 20.0)
    if temp < 5.0:
        contributing_factors.append({
            "factor": "Freezing Temperatures",
            "impact": "Negative",
            "description": f"Temperature is very low ({temp:.1f}°C). Sub-freezing temperatures pose risks of component contraction and seal/O-ring stiffness."
        })
    elif 15.0 <= temp <= 28.0:
        contributing_factors.append({
            "factor": "Optimal Temperature Range",
            "impact": "Positive",
            "description": f"Air temperature is ideal ({temp:.1f}°C), minimizing thermal expansion stresses."
        })
        
    # Check Cloud Cover & Precipitation
    precip = weather["precipitation"]
    clouds = weather["cloud_cover"]
    if precip > 0.5:
        contributing_factors.append({
            "factor": "Active Precipitation",
            "impact": "Negative",
            "description": f"Rain or precipitation is detected ({precip:.1f} mm/h), increasing humidity and flight visibility risks."
        })
    if clouds > 85.0:
        contributing_factors.append({
            "factor": "Heavy Cloud Cover",
            "impact": "Negative",
            "description": f"Cloud cover is {clouds:.0f}%, which limits visual tracking and flight line visibility."
        })
    elif clouds < 15.0:
        contributing_factors.append({
            "factor": "Clear Skies",
            "impact": "Positive",
            "description": f"Excellent visibility with clear skies ({clouds:.0f}% cloud cover) for launch tracking."
        })

    # Check Visibility
    vis = weather["visibility"]
    if vis < 4.0:
        contributing_factors.append({
            "factor": "Critical Low Visibility",
            "impact": "Negative",
            "description": f"Visibility is extremely low ({vis:.1f} km), violating the Launch Commit Criteria minimum requirement of 6.4 km for optical tracking."
        })
    elif vis < 8.0:
        contributing_factors.append({
            "factor": "Marginal Visibility",
            "impact": "Negative",
            "description": f"Visibility is reduced ({vis:.1f} km), making optical and radar flight line tracking difficult."
        })
    elif vis > 15.0:
        contributing_factors.append({
            "factor": "Excellent Visibility",
            "impact": "Positive",
            "description": f"Visibility is clear ({vis:.1f} km), providing perfect tracking conditions."
        })

    # Historical Factors
    if rock_rate < 0.70:
        contributing_factors.append({
            "factor": "Rocket Historical Reliability",
            "impact": "Negative",
            "description": f"The {req.rocket} rocket has a lower historical success rate of {rock_rate:.1%} in past missions."
        })
    elif rock_rate > 0.90:
        contributing_factors.append({
            "factor": "Proven Rocket Heritage",
            "impact": "Positive",
            "description": f"The {req.rocket} vehicle has a highly reliable track record with {rock_rate:.1%} success rate."
        })
        
    if comp_rate < 0.75:
        contributing_factors.append({
            "factor": "Launcher Success Rate",
            "impact": "Negative",
            "description": f"The operating company ({req.company}) has a lower historical mission success rate of {comp_rate:.1%}."
        })
    elif comp_rate > 0.90:
        contributing_factors.append({
            "factor": "Strong Launcher Heritage",
            "impact": "Positive",
            "description": f"The operating company ({req.company}) possesses an outstanding overall heritage of {comp_rate:.1%} success."
        })

    # Default factor if none matches
    if not contributing_factors:
        contributing_factors.append({
            "factor": "Normal Operating Margin",
            "impact": "Positive",
            "description": "All monitored weather variables and launcher parameters are within normal historical operating margins."
        })

    return {
        "success_probability": success_score,
        "failure_risk": risk_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "weather_summary": weather,
        "contributing_factors": contributing_factors
    }

@app.get("/api/stats")
async def get_stats():
    """
    Returns aggregated historical launch statistics for the React Dashboard charts.
    """
    if not os.path.exists(ENRICHED_DATA_PATH):
        return {"success_by_year": [], "success_by_company": []}
        
    try:
        df = pd.read_csv(ENRICHED_DATA_PATH)
        df["Success"] = df["Status Mission"].apply(lambda x: 1 if str(x).strip() == "Success" else 0)
        df["Cleaned_Datetime"] = pd.to_datetime(df["Cleaned_Datetime"])
        df["Launch_Year"] = df["Cleaned_Datetime"].dt.year
        
        # 1. Success rate by year (grouped)
        by_year = df.groupby("Launch_Year")
        year_stats = []
        for name, group in by_year:
            year_stats.append({
                "year": int(name),
                "total": int(len(group)),
                "successes": int(group["Success"].sum()),
                "rate": float(group["Success"].mean())
            })
            
        # 2. Success rate by major company (Top 10 companies by launch volume)
        top_companies = df["Company Name"].value_counts().head(10).index
        company_stats = []
        for comp in top_companies:
            comp_df = df[df["Company Name"] == comp]
            company_stats.append({
                "company": comp,
                "total": int(len(comp_df)),
                "successes": int(comp_df["Success"].sum()),
                "rate": float(comp_df["Success"].mean())
            })

        # 3. Weather success vs failure distributions (simple means)
        weather_compare = {}
        weather_cols = ["temperature_2m", "wind_speed_10m", "cloud_cover", "surface_pressure"]
        for col in weather_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                weather_compare[col] = {
                    "success_mean": float(df[df["Success"] == 1][col].mean()) if not df[df["Success"] == 1][col].isna().all() else 0.0,
                    "failure_mean": float(df[df["Success"] == 0][col].mean()) if not df[df["Success"] == 0][col].isna().all() else 0.0
                }
            
        return {
            "success_by_year": sorted(year_stats, key=lambda x: x["year"]),
            "success_by_company": sorted(company_stats, key=lambda x: x["total"], reverse=True),
            "weather_compare": weather_compare
        }
    except Exception as ex:
        print(f"Stats generation error: {ex}")
        return {"success_by_year": [], "success_by_company": []}
