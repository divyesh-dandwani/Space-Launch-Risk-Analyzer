# Space Launch Risk Analyzer

A machine learning-powered safety assessment dashboard for space launches. The system analyzes historical space mission performance (4,000+ launches from 1957) alongside historical/forecast hourly atmospheric weather metrics (temperature, wind speeds, pressure, clouds, precipitation, etc.) from the **Open-Meteo API** to estimate the success probability and failure risk of upcoming launches.

---

## System Architecture

```text
Historical Launches (Kaggle)
│
▼
Geocoding coordinates (sites_mapping.csv)
│
▼
Open-Meteo Archive API (Historical hourly weather)
│
▼
Data Cleaning & Bayesian Success Rates Feature Engineering (preprocess.py)
│
▼
Machine Learning Model Training & Selection (XGBoost, CatBoost, LightGBM, RF)
│
▼
FastAPI Backend (app.py)  ◄───[Fetches current forecast / archive weather]
│
▼
React Dashboard (Vite + Glassmorphism Custom CSS)
```

---

## Quick Start (Run the Pre-Trained App)

The data pipeline has already been run and the **XGBoost** model is trained. Follow these steps to run the application immediately:

### 1. Start the FastAPI Backend
Navigate to the `backend/` directory, install the dependencies, and start the Uvicorn server:
```bash
# Navigate to backend
cd backend

# Install Python requirements
pip install -r requirements.txt

# Start the dev server on port 8001
uvicorn src.app:app --reload --port 8001
```
*The API will be available at `http://localhost:8001`.*

### 2. Start the React Frontend
Open a new terminal, navigate to the `frontend/` directory, install packages, and start the Vite dev server:
```bash
# Navigate to frontend
cd frontend

# Install Node modules
npm install

# Start the dev server on port 5173
npm run dev
```
*Open your browser and navigate to `http://localhost:5173` to interact with the dashboard.*

---

## Data Pipeline Commands (Optional)

If you wish to download the raw dataset, geocode coordinates, fetch weather data, and train models from scratch:

```bash
cd backend

# 1. Download Space_Corrected.csv via kagglehub
python src/downloader.py

# 2. Extract unique launch sites and map coordinates (sites_mapping.csv)
python src/geocoder.py

# 3. Pull hourly historical weather archives from Open-Meteo
# (Multi-threaded & connection-pooled, takes ~4 minutes)
python src/weather_fetcher.py

# 4. Preprocess, feature engineer, and train the candidate ML models
python src/train.py
```
*Upon completion, the best model (XGBoost) is automatically saved to `backend/models/best_model.joblib` and will be loaded by the FastAPI backend on startup.*

---

## Core API Endpoints

- **`POST /api/predict`**: Accepts site, date, time, vehicle, operator, and payload type. Retrieves current weather forecast or historical archive and returns the safety scores, weather metrics, and contributing risk factors.
- **`GET /api/sites`**: Returns unique spaceports and their resolved coordinates.
- **`GET /api/rockets`**: Returns lists of rockets and companies to populate UI dropdowns.
- **`GET /api/stats`**: Compiles yearly success rates, operator performance comparisons, and weather profiles for the dashboard charts.
