# Space Launch Risk Analyzer

A machine learning-powered safety assessment dashboard for space launches. The system analyzes historical space mission performance (4,000+ launches from 1957) alongside historical/forecast hourly atmospheric weather metrics (temperature, wind speeds, pressure, clouds, precipitation, etc.) from the **Open-Meteo API** to estimate the success probability and failure risk of upcoming launches.

---

## 📋 Problem Statement

Space launches are highly complex events that are critically sensitive to atmospheric conditions. Poor weather at the launch pad has historically led to scrubbed launches, visual tracking issues, and catastrophic failures (such as the Challenger disaster caused by cold-temperature O-ring failure). 

Evaluating launch safety is typically manual and complex. This project solves this by:
1. Mapping historical space launches (1957–Present) to their exact weather parameters at the hour of launch.
2. Training predictive Machine Learning classifiers on top of this compiled datasets.
3. Automatically applying real-world **Launch Commit Criteria (LSE)** to adjust predictions for critical weather anomalies in real time.

---

## 🛠️ Technology Stack

- **Backend (Python API)**: 
  - **FastAPI** & **Uvicorn** (High-performance API server)
  - **Pydantic** (Data validation schemas)
  - **Pandas** & **NumPy** (Data cleaning and feature engineering)
  - **Scikit-Learn** & **CatBoost** (Machine Learning & standardization scaling)
  - **Open-Meteo API** (Hourly weather forecast and historical archives)
- **Frontend (React)**:
  - **React (Vite)** (Fast modern SPA development)
  - **Vanilla CSS** (Custom responsive design with modern Glassmorphism cards)
  - **Dual Theme Support** (Light/Dark mode switcher button, persisting selections via `localStorage`)
  - **Responsive SVG Visualizations** (Custom launch volume and success rate graphs)

---

## 📊 Dataset References & Sources

1. **Space Mission Launches (1957–Present)**:
   - Source: Kaggle Datasets
   - Link: [All Space Missions from 1957](https://www.kaggle.com/datasets/agirlcoding/all-space-missions-from-1957)
   - Contains launch date, rocket type, operator company, site location, launch cost, and mission success/failure label.
2. **Atmospheric Weather Archives & Forecasts**:
   - Source: Open-Meteo API
   - Link: [Open-Meteo Weather APIs](https://open-meteo.com/)
   - Retrieves historical hourly weather profiles for coordinates matching the launch pads at the exact date/hour of launch, and pulls live forecasts for future launches.

---

## 🧠 Solution & ML Approach

1. **Find Launch Coordinates**: Converts launch site names (like "Kennedy Space Center") into GPS coordinates (Latitude & Longitude).
2. **Collect Weather Data**: Gets historical weather conditions (temperature, wind speed, visibility, cloud cover, rain, etc.) for every launch at its exact date and time.
3. **Calculate Past Success Rates**: Computes the historical success rate of each space agency, rocket model, and launch pad up to that day, ensuring future data doesn't leak into past predictions.
4. **Train ML Models**: Compares multiple machine learning algorithms (Random Forest, XGBoost, LightGBM, CatBoost). The **XGBoost Classifier** was selected as the best performing model based on its accuracy.
5. **Apply Weather Safety Rules**: Blends the ML prediction with real-world launch safety criteria (e.g., cutting the safety score if wind speed exceeds 40 km/h or temperature drops near freezing).

---

## 🚀 Quick Start (Run the App)

The data pipeline has already been run and the **XGBoost** model is trained. Follow these steps to run the application immediately:

### 1. Start the FastAPI Backend
Navigate to the `backend/` directory, install dependencies, and start the Uvicorn server:
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

## ⚙️ Data Pipeline Commands (Optional)

If you wish to download raw data, geocode coordinates, enrich weather, and train models from scratch:

```bash
cd backend

# 1. Download Space_Corrected.csv via kagglehub
python src/downloader.py

# 2. Map coordinates (sites_mapping.csv)
python src/geocoder.py

# 3. Pull hourly weather archive from Open-Meteo (runs parallel threads)
python src/weather_fetcher.py

# 4. Preprocess, feature engineer, and train the ML models
python src/train.py
```
*Upon completion, the best model (XGBoost) is automatically saved to `backend/models/best_model.joblib`.*

---

## 📡 Core API Endpoints

- **`POST /api/predict`**: Accepts site, date, time, vehicle, company, cost, and manual weather overrides. Returns safety metrics, real-time/forecast weather parameters, and diagnostic risk drivers.
- **`GET /api/sites`**: Returns unique spaceports and resolved coordinates.
- **`GET /api/rockets`**: Returns list of rockets and companies for UI dropdowns.
- **`GET /api/stats`**: Compiles yearly analytics and operator performance profiles.
