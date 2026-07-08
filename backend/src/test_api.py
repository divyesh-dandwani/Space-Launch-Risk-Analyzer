import urllib.request
import urllib.error
import json
import sys
import os

# Load .env file manually
env_path = ".env"
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key.strip()] = val.strip()

def test_prediction():
    port = os.environ.get("PORT", "8001")
    url = f"http://localhost:{port}/api/predict"
    payload = {
        "site": "LC-39A, Kennedy Space Center, Florida, USA",
        "date": "2026-07-10",
        "time": "15:00",
        "rocket": "Falcon 9 Block 5",
        "company": "SpaceX",
        "payload_type": "Crew",
        "rocket_cost": 62.0,
        "override_weather": True,
        "temperature_2m": 35.0,
        "relative_humidity_2m": 85.0,
        "surface_pressure": 1011.0,
        "wind_speed_10m": 45.0,
        "wind_gusts_10m": 55.0,
        "visibility": 1.0,
        "cloud_cover": 95.0,
        "precipitation": 3.5,
        "dew_point_2m": 32.0
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending test prediction request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers=headers
        )
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("\n" + "="*50)
            print("API RESPONSE RECEIVED SUCCESSFULLY")
            print("="*50)
            print(f"Success Probability : {res_data.get('success_probability')}%")
            print(f"Failure Risk        : {res_data.get('failure_risk')}%")
            print(f"Risk Level          : {res_data.get('risk_level')}")
            print(f"Risk Color Code     : {res_data.get('risk_color')}")
            
            print("\nWeather Summary:")
            print(json.dumps(res_data.get("weather_summary"), indent=2))
            
            print("\nContributing Factors:")
            for idx, factor in enumerate(res_data.get("contributing_factors", [])):
                print(f"{idx+1}. [{factor['impact']}] {factor['factor']}: {factor['description']}")
            print("="*50 + "\n")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error testing prediction API: {e}")
        try:
            print(f"Error Response Body: {e.read().decode()}")
        except Exception:
            pass
    except Exception as e:
        print(f"Error testing prediction API: {e}")
        print(f"Ensure the FastAPI server is running locally (e.g. uvicorn src.app:app --reload --port {port})")

if __name__ == "__main__":
    test_prediction()
