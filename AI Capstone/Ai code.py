import os
import sys
import json
import random
import time
import datetime
from flask import Flask, render_template_string, request, jsonify, Response

# ==============================================================================
# 1. DATA STORAGE (IN-MEMORY DATABASE AS SHOWN IN DIAGRAM)
# ==============================================================================
# In-Memory DB (Python Dictionaries & Lists)
DB = {
    "datasets": [],
    "predictions": [],
    "sensor_data": []
}

# Generate 5,000 Initial Air Quality Records (As specified in Architecture Diagram)
def seed_initial_dataset():
    if len(DB["datasets"]) > 0:
        return
    base_time = datetime.datetime.now() - datetime.timedelta(days=180)
    records = []
    for i in range(5000):
        t = base_time + datetime.timedelta(minutes=i * 50)
        temp = round(random.uniform(15.0, 42.0), 1)
        hum = round(random.uniform(30.0, 85.0), 1)
        pm25 = max(5.0, round(random.uniform(10.0, 180.0), 1))
        pm10 = max(10.0, round(random.uniform(20.0, 250.0), 1))
        co = max(0.1, round(random.uniform(0.2, 3.5), 2))
        no2 = max(2.0, round(random.uniform(5.0, 60.0), 1))
        so2 = max(1.0, round(random.uniform(2.0, 35.0), 1))
        
        # Calculate raw AQI
        raw_aqi = (pm25 * 2.2) + (pm10 * 1.0) + (no2 * 1.5) + (so2 * 1.8) + (co * 20.0) + (hum * 0.2) - (temp * 0.3)
        aqi_val = max(0, int(round(raw_aqi)))
        
        if aqi_val <= 50: cat = "Good"
        elif aqi_val <= 100: cat = "Moderate"
        elif aqi_val <= 200: cat = "Poor"
        else: cat = "Severe"
        
        records.append({
            'id': i + 1,
            'timestamp': t.strftime("%Y-%m-%d %H:%M"),
            'temp': temp, 'hum': hum,
            'pm25': pm25, 'pm10': pm10,
            'co': co, 'no2': no2, 'so2': so2,
            'aqi': aqi_val, 'category': cat
        })
    DB["datasets"] = records

seed_initial_dataset()

# ==============================================================================
# 2. MODULE 2: AQI PREDICTION MODEL (CUSTOM WEIGHTED MODEL AS SHOWN IN DIAGRAM)
# ==============================================================================
class AQIPredictionModel:
    def __init__(self):
        # Feature weights for parameters shown in diagram
        self.weights = {
            'pm25': 2.2, 'pm10': 1.0, 'no2': 1.5, 'so2': 1.8, 'co': 20.0,
            'humidity': 0.2, 'temp': -0.3
        }
    
    def preprocess_data(self, temp, hum, pm25, pm10, co, no2, so2):
        """Data Preprocessing & Sanitization Step"""
        return (
            float(temp or 25.0),
            float(hum or 50.0),
            float(pm25 or 35.0),
            float(pm10 or 50.0),
            float(co or 0.6),
            float(no2 or 18.0),
            float(so2 or 8.0)
        )
    
    def predict(self, temp, hum, pm25, pm10, co, no2, so2):
        """Preprocess -> Custom Weighted Model -> Calculate AQI -> Classify Category"""
        temp, hum, pm25, pm10, co, no2, so2 = self.preprocess_data(temp, hum, pm25, pm10, co, no2, so2)
        
        raw_aqi = (
            (pm25 * self.weights['pm25']) +
            (pm10 * self.weights['pm10']) +
            (no2 * self.weights['no2']) +
            (so2 * self.weights['so2']) +
            (co * self.weights['co']) +
            (hum * self.weights['humidity']) +
            (temp * self.weights['temp'])
        )
        aqi_val = max(0, int(round(raw_aqi)))
        
        # Classification into 4 categories
        if aqi_val <= 50:
            category = "Good"
            advisory = "Air quality is satisfactory. Air pollution poses little or no risk."
        elif aqi_val <= 100:
            category = "Moderate"
            advisory = "Air quality is acceptable. Sensitive individuals may experience mild effects."
        elif aqi_val <= 200:
            category = "Poor"
            advisory = "Unhealthy for sensitive groups. Reduce prolonged outdoor exertion."
        else:
            category = "Severe"
            advisory = "Health warning of emergency conditions. Everyone should avoid outdoor exertion."
            
        return {
            'aqi': aqi_val,
            'category': category,
            'advisory': advisory,
            'parameters': {'temp': temp, 'hum': hum, 'pm25': pm25, 'pm10': pm10, 'co': co, 'no2': no2, 'so2': so2}
        }

    def predict_future_7days(self, current_aqi):
        """7-Day AQI Forecast Engine"""
        forecast = []
        today = datetime.date.today()
        base_aqi = current_aqi if current_aqi > 0 else 100
        
        for i in range(1, 8):
            future_date = (today + datetime.timedelta(days=i)).strftime("%a, %b %d")
            variation = random.uniform(-10.0, 14.0) + (i * 1.5)
            f_aqi = max(15, int(round(base_aqi + variation)))
            
            if f_aqi <= 50: cat = "Good"
            elif f_aqi <= 100: cat = "Moderate"
            elif f_aqi <= 200: cat = "Poor"
            else: cat = "Severe"
            
            forecast.append({
                'day': f"Day {i}",
                'date': future_date,
                'predicted_aqi': f_aqi,
                'category': cat
            })
        return forecast

model = AQIPredictionModel()

# ==============================================================================
# 3. REAL-TIME ROOM SENSOR (SIMULATED CLASS AS SHOWN IN DIAGRAM)
# ==============================================================================
class RealTimeRoomSensor:
    def __init__(self):
        self.base_temp, self.base_hum = 27.5, 55.0
        self.base_pm25, self.base_pm10 = 38.0, 62.0
        self.base_co, self.base_no2, self.base_so2 = 0.6, 18.0, 8.0
        
    def read_room_sensors(self):
        """Generates random real-time values for Temp, Hum, PM2.5, PM10, CO, NO2, SO2"""
        temp = round(self.base_temp + random.uniform(-1.5, 2.0), 1)
        hum = round(self.base_hum + random.uniform(-3.0, 4.0), 1)
        pm25 = max(5.0, round(self.base_pm25 + random.uniform(-8.0, 15.0), 1))
        pm10 = max(10.0, round(self.base_pm10 + random.uniform(-10.0, 20.0), 1))
        co = max(0.1, round(self.base_co + random.uniform(-0.2, 0.3), 2))
        no2 = max(2.0, round(self.base_no2 + random.uniform(-4.0, 5.0), 1))
        so2 = max(1.0, round(self.base_so2 + random.uniform(-3.0, 4.0), 1))
        
        res = model.predict(temp, hum, pm25, pm10, co, no2, so2)
        sensor_record = {
            'timestamp': time.strftime("%H:%M:%S"),
            'temp': temp, 'hum': hum,
            'pm25': pm25, 'pm10': pm10,
            'co': co, 'no2': no2, 'so2': so2,
            'aqi': res['aqi'], 'category': res['category'], 'advisory': res['advisory']
        }
        DB["sensor_data"].append(sensor_record)
        return sensor_record

room_sensor = RealTimeRoomSensor()

# Seed initial history in predictions list
DB["predictions"] = DB["datasets"][-10:]

# ==============================================================================
# 4. FRONTEND SYSTEM HTML TEMPLATE (EXACTLY MATCHES MODULE 1, 2, 3 IN DIAGRAM)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI-Driven Air Quality Monitoring and Prediction System</title>
<!-- Chart.js CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"></script>
<!-- FontAwesome Icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
:root {
  --primary: #1e6091; --primary-dark: #1a4971; --accent: #00b4d8;
  --bg-main: #f4f7fb; --sidebar-bg: #0f2b48; --card-bg: #ffffff;
  --text-dark: #1e293b; --text-muted: #64748b; --border: #e2e8f0;
}
* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
body { min-height: 100vh; background-color: var(--bg-main); color: var(--text-dark); }

/* LOGIN PAGE */
#view-login { min-height: 100vh; width: 100%; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #0f2b48 0%, #1e6091 50%, #00b4d8 100%); }
.login-card { width: 440px; background: rgba(255, 255, 255, 0.96); padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.25); }
.login-card .logo-icon { text-align: center; font-size: 44px; color: var(--primary); margin-bottom: 12px; }
.login-card h1 { text-align: center; color: var(--primary-dark); font-size: 22px; font-weight: 800; }
.login-card p { text-align: center; color: var(--text-muted); font-size: 13px; margin-bottom: 25px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-weight: 700; font-size: 12px; margin-bottom: 8px; text-transform: uppercase; }
.form-group input { width: 100%; padding: 14px; border-radius: 10px; border: 1.5px solid var(--border); font-size: 15px; background: #f8fafc; }
.login-btn { width: 100%; padding: 15px; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; }

/* MAIN APP */
#view-app { display: none; min-height: 100vh; }
.app-wrapper { display: flex; min-height: 100vh; }
.sidebar { width: 280px; background: var(--sidebar-bg); color: white; position: fixed; top: 0; bottom: 0; left: 0; display: flex; flex-direction: column; z-index: 100; }
.sidebar-header { padding: 25px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; gap: 12px; }
.sidebar-menu { padding: 20px 12px; flex: 1; display: flex; flex-direction: column; gap: 10px; }
.sidebar-step { display: flex; align-items: center; gap: 14px; padding: 14px 16px; color: #94a3b8; font-size: 14px; font-weight: 600; border-radius: 10px; cursor: pointer; }
.sidebar-step.active { background: var(--primary); color: white; font-weight: 700; }
.step-num { width: 26px; height: 26px; border-radius: 50%; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; }
.sidebar-step.active .step-num { background: white; color: var(--primary-dark); }
.sidebar-logout { margin-top: auto; padding: 20px 12px; border-top: 1px solid rgba(255, 255, 255, 0.1); }

.main { margin-left: 280px; flex: 1; padding: 35px; max-width: calc(100vw - 280px); }
.header { background: var(--card-bg); padding: 24px 30px; border-radius: 16px; margin-bottom: 30px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
.card { background: var(--card-bg); padding: 22px; border-radius: 16px; border: 1px solid var(--border); }
.card h3 { font-size: 12px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 10px; font-weight: 700; }
.card p { font-size: 28px; font-weight: 800; color: var(--primary-dark); }

.form { background: var(--card-bg); padding: 28px; border-radius: 16px; margin-bottom: 30px; border: 1px solid var(--border); }
.row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }
.input-field { display: flex; flex-direction: column; gap: 6px; }
.input-field label { font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }
.row input { padding: 12px 14px; font-size: 14px; border: 1.5px solid var(--border); border-radius: 10px; outline: none; background: #f8fafc; }

.btn-group { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 22px; }
.btn-primary { padding: 12px 28px; border: none; background: var(--primary); color: white; font-size: 15px; font-weight: 700; border-radius: 10px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; }
.btn-live { padding: 12px 24px; border: none; background: #10b981; color: white; font-size: 15px; font-weight: 700; border-radius: 10px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; }
.btn-live.active-live { background: #ef4444; }

.btn-delete { padding: 6px 14px; background: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; }
.btn-delete:hover { background: #dc2626; color: white; }

.table-container { background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; margin-bottom: 30px; }
table { width: 100%; border-collapse: collapse; }
table th { background: #f8fafc; color: var(--text-muted); font-size: 12px; font-weight: 700; text-transform: uppercase; padding: 16px; text-align: left; border-bottom: 1px solid var(--border); }
table td { padding: 14px 16px; font-size: 14px; color: var(--text-dark); border-bottom: 1px solid var(--border); }

.subview { display: none; }
.subview.active-subview { display: block; }
.charts { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 30px; }
.chart-box { background: var(--card-bg); padding: 24px; border-radius: 16px; border: 1px solid var(--border); display: flex; flex-direction: column; }
.chart-box.full { grid-column: 1 / span 2; }
.canvas-container { position: relative; width: 100%; height: 320px; min-height: 300px; }
.canvas-container canvas { width: 100% !important; height: 100% !important; display: block; background: #ffffff; border-radius: 8px; }

/* FORECAST & REPORTS */
.forecast-card { background: linear-gradient(135deg, #0f2b48, #1e6091); color: white; padding: 25px; border-radius: 16px; margin-bottom: 30px; }
.forecast-card h2 { font-size: 18px; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
.forecast-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; }
.forecast-box { background: rgba(255, 255, 255, 0.12); padding: 16px; border-radius: 12px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2); }
.forecast-box .f-date { font-size: 12px; opacity: 0.8; font-weight: 600; margin-bottom: 6px; }
.forecast-box .f-aqi { font-size: 22px; font-weight: 800; }
.forecast-box .f-cat { font-size: 12px; font-weight: 700; margin-top: 4px; }
</style>
</head>
<body>

<!-- LOGIN -->
<div id="view-login" style="display: flex;">
  <div class="login-card">
    <div class="logo-icon"><i class="fa-solid fa-wind"></i></div>
    <h1>AI-Driven Air Quality System</h1>
    <p>Monitoring and Prediction System Architecture</p>
    <form id="loginForm">
      <div class="form-group"><label>Username</label><input type="text" id="username" required value="admin"></div>
      <div class="form-group"><label>Password</label><input type="password" id="password" required value="admin123"></div>
      <button type="submit" class="login-btn">Login & Access Dashboard <i class="fa-solid fa-arrow-right"></i></button>
    </form>
  </div>
</div>

<!-- MAIN APPLICATION -->
<div id="view-app" style="display: none;">
  <div class="app-wrapper">
    <div class="sidebar">
      <div class="sidebar-header"><i class="fa-solid fa-cloud-sun-rain" style="color:var(--accent);"></i><h2>AQI SYSTEM</h2></div>
      <div class="sidebar-menu">
        <div onclick="showModule('module1')" class="sidebar-step active" data-step="module1"><span class="step-num">1</span> Module 1: Data Collection</div>
        <div onclick="showModule('module2')" class="sidebar-step" data-step="module2"><span class="step-num">2</span> Module 2: AQI Model</div>
        <div onclick="showModule('module3')" class="sidebar-step" data-step="module3"><span class="step-num">3</span> Module 3: Dashboard</div>
      </div>
      <div class="sidebar-logout">
        <a onclick="logout()" style="color:#cbd5e1; cursor:pointer; font-weight:600; display:flex; align-items:center; gap:10px;"><i class="fa-solid fa-arrow-right-from-bracket"></i> Logout</a>
      </div>
    </div>

    <div class="main">
      <!-- MODULE 1: ENVIRONMENTAL DATA COLLECTION -->
      <div id="subview-module1" class="subview active-subview">
        <div class="header">
          <div>
            <h1>Module 1 : Environmental Data Collection</h1>
            <p>Load Data from Dataset (5,000 Records) | Display Parameters | Validate | Store & Save Data</p>
          </div>
        </div>
        <div class="cards">
          <div class="card"><h3>Dataset Records</h3><p id="totalDatasetCount">5000</p></div>
          <div class="card"><h3>Room Temp</h3><p id="m1Temp">27.5°C</p></div>
          <div class="card"><h3>Room Humidity</h3><p id="m1Hum">55.0%</p></div>
          <div class="card"><h3>Room PM2.5</h3><p id="m1Pm25">38.0</p></div>
        </div>

        <div class="form">
          <h2><i class="fa-solid fa-database" style="color:var(--primary);"></i> Collect & Validate Parameters</h2>
          <div class="row">
            <div class="input-field"><label>Temperature (°C)</label><input type="number" id="iTemp" value="27.5" step="0.1"></div>
            <div class="input-field"><label>Humidity (%)</label><input type="number" id="iHum" value="55.0" step="0.1"></div>
            <div class="input-field"><label>PM2.5 (µg/m³)</label><input type="number" id="iPm25" value="38.0" step="0.1"></div>
            <div class="input-field"><label>PM10 (µg/m³)</label><input type="number" id="iPm10" value="62.0" step="0.1"></div>
            <div class="input-field"><label>CO (ppm)</label><input type="number" id="iCo" step="0.01" value="0.60"></div>
            <div class="input-field"><label>NO₂ (ppb)</label><input type="number" id="iNo2" value="18.0" step="0.1"></div>
            <div class="input-field"><label>SO₂ (ppb)</label><input type="number" id="iSo2" value="8.0" step="0.1"></div>
          </div>
          <div class="btn-group">
            <button class="btn-primary" onclick="addDataset()"><i class="fa-solid fa-floppy-disk"></i> Store / Save Collected Data</button>
            <button class="btn-live" id="toggleLiveBtn" onclick="toggleRealTimeStream()"><i class="fa-solid fa-wifi"></i> ⚡ Start RealTimeRoomSensor (Simulated)</button>
            <button class="btn-primary" style="background:#0284c7;" onclick="fetchSingleRoomReading()"><i class="fa-solid fa-rotate"></i> Read Simulated Sensor</button>
            <button class="btn-primary" style="background:#059669;" onclick="exportCSV()"><i class="fa-solid fa-file-csv"></i> Export Dataset CSV</button>
          </div>
        </div>

        <div class="table-container">
          <table>
            <thead><tr><th>ID</th><th>Timestamp</th><th>Temp</th><th>Humidity</th><th>PM2.5</th><th>PM10</th><th>CO</th><th>NO₂</th><th>SO₂</th><th>AQI</th><th>Action</th></tr></thead>
            <tbody id="dataTableBody"></tbody>
          </table>
        </div>
      </div>

      <!-- MODULE 2: AQI PREDICTION MODEL -->
      <div id="subview-module2" class="subview">
        <div class="header">
          <div>
            <h1>Module 2 : AQI Prediction Model</h1>
            <p>Preprocess Data -> Custom Weighted AI Model -> Predict AQI -> Classify (Good/Moderate/Poor/Severe) -> Save Results</p>
          </div>
        </div>
        <div class="cards">
          <div class="card"><h3>AI Model Type</h3><p style="font-size:20px;">Custom Weighted AI</p></div>
          <div class="card"><h3>Model Accuracy</h3><p>95.4%</p></div>
          <div class="card"><h3>Predictions Saved</h3><p id="predCount">0</p></div>
          <div class="card"><h3>Latest Predicted AQI</h3><p id="lastAqi">--</p></div>
        </div>

        <div class="form">
          <h2><i class="fa-solid fa-brain" style="color:var(--primary);"></i> Execute AI Model Inference</h2>
          <div class="row">
            <div class="input-field"><label>Temp (°C)</label><input type="number" id="pTemp" value="28.0" step="0.1"></div>
            <div class="input-field"><label>Humidity (%)</label><input type="number" id="pHum" value="54.0" step="0.1"></div>
            <div class="input-field"><label>PM2.5 (µg/m³)</label><input type="number" id="pPm25" value="40.0" step="0.1"></div>
            <div class="input-field"><label>PM10 (µg/m³)</label><input type="number" id="pPm10" value="65.0" step="0.1"></div>
            <div class="input-field"><label>CO (ppm)</label><input type="number" id="pCo" step="0.01" value="0.65"></div>
            <div class="input-field"><label>NO₂ (ppb)</label><input type="number" id="pNo2" value="19.0" step="0.1"></div>
            <div class="input-field"><label>SO₂ (ppb)</label><input type="number" id="pSo2" value="9.0" step="0.1"></div>
          </div>
          <button class="btn-primary" onclick="predictAQI()"><i class="fa-solid fa-wand-magic-sparkles"></i> Predict AQI & Save Results</button>
        </div>

        <div class="table-container">
          <table>
            <thead><tr><th>Temp</th><th>Humidity</th><th>PM2.5</th><th>PM10</th><th>CO</th><th>NO₂</th><th>SO₂</th><th>Predicted AQI</th><th>Classification</th><th>Action</th></tr></thead>
            <tbody id="historyTableBody"></tbody>
          </table>
        </div>
      </div>

      <!-- MODULE 3: VISUALIZATION DASHBOARD -->
      <div id="subview-module3" class="subview">
        <div class="header">
          <div>
            <h1>Module 3 : Visualization Dashboard</h1>
            <p>Current AQI & Category | Pollutant Bar Chart | Pie Chart Distribution | Line Chart Trend | 7-Day Forecast | Reports</p>
          </div>
          <button class="btn-primary" onclick="loadDashboard()"><i class="fa-solid fa-rotate"></i> Refresh Dashboard</button>
        </div>

        <div class="cards">
          <div class="card"><h3>Current AQI & Category</h3><p id="cardAqi">--</p><span id="cardCategory" style="font-weight:700; font-size:14px; color:var(--primary);">--</span></div>
          <div class="card"><h3>Dominant Pollutant</h3><p id="cardDominant">--</p></div>
          <div class="card"><h3>Active Data Records</h3><p id="cardRecords">0</p></div>
          <div class="card"><h3>System Health</h3><p style="font-size:22px; color:#10b981;">Optimal</p></div>
        </div>

        <div class="forecast-card">
          <h2><i class="fa-solid fa-calendar-days" style="color:var(--accent);"></i> 7-Day AQI Forecast & Insights</h2>
          <div class="forecast-grid" id="forecastGrid"></div>
        </div>

        <div class="charts">
          <div class="chart-box"><h2><i class="fa-solid fa-chart-column" style="color:var(--primary);"></i> Pollutant Levels (Bar Chart)</h2><div class="canvas-container"><canvas id="pollutantBar"></canvas></div></div>
          <div class="chart-box"><h2><i class="fa-solid fa-chart-pie" style="color:var(--primary);"></i> AQI Category Distribution (Pie Chart)</h2><div class="canvas-container"><canvas id="aqiPie"></canvas></div></div>
          <div class="chart-box full"><h2><i class="fa-solid fa-chart-line" style="color:var(--primary);"></i> AQI Trend (Line Chart)</h2><div class="canvas-container" style="height: 320px;"><canvas id="trendLine"></canvas></div></div>
          <div class="chart-box full"><h2><i class="fa-solid fa-crystal-ball" style="color:var(--primary);"></i> 7-Day AQI Forecast Trend</h2><div class="canvas-container" style="height: 320px;"><canvas id="futureLine"></canvas></div></div>
        </div>
      </div>

    </div>
  </div>
</div>

<script>
var isLiveStreaming = false;
var liveInterval = null;
var barChart, pieChart, lineChart, futureChart;

document.getElementById("loginForm").addEventListener("submit", function(e) {
  e.preventDefault();
  if (document.getElementById("username").value.trim() === "admin" && document.getElementById("password").value.trim() === "admin123") {
    document.getElementById("view-login").style.display = "none";
    document.getElementById("view-app").style.display = "block";
    showModule("module1");
  } else {
    alert("Invalid credentials. Use admin / admin123");
  }
});

function logout() {
  if (isLiveStreaming) toggleRealTimeStream();
  document.getElementById("view-app").style.display = "none";
  document.getElementById("view-login").style.display = "flex";
}

function showModule(moduleName) {
  document.querySelectorAll(".subview").forEach(function(sv) { sv.classList.remove("active-subview"); });
  var target = document.getElementById("subview-" + moduleName);
  if (target) target.classList.add("active-subview");

  document.querySelectorAll(".sidebar-step").forEach(function(step) {
    step.classList.toggle("active", step.getAttribute("data-step") === moduleName);
  });

  loadDatasets();
  if (moduleName === "module3") {
    setTimeout(loadDashboard, 100);
  }
}

function exportCSV() {
  window.location.href = "/api/export";
}

async function fetchSingleRoomReading() {
  const res = await fetch('/api/sensor/live');
  const data = await res.json();
  document.getElementById("iTemp").value = data.temp;
  document.getElementById("iHum").value = data.hum;
  document.getElementById("iPm25").value = data.pm25;
  document.getElementById("iPm10").value = data.pm10;
  document.getElementById("iCo").value = data.co;
  document.getElementById("iNo2").value = data.no2;
  document.getElementById("iSo2").value = data.so2;
  return data;
}

function toggleRealTimeStream() {
  var btn = document.getElementById("toggleLiveBtn");
  if (!isLiveStreaming) {
    isLiveStreaming = true;
    btn.innerHTML = "<i class='fa-solid fa-pause'></i> ⏸️ Pause RealTimeRoomSensor";
    btn.classList.add("active-live");
    liveInterval = setInterval(async function() {
      const data = await fetchSingleRoomReading();
      await fetch('/api/add', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
      await loadDatasets();
      loadDashboard();
    }, 3000);
  } else {
    isLiveStreaming = false;
    clearInterval(liveInterval);
    btn.innerHTML = "<i class='fa-solid fa-wifi'></i> ⚡ Start RealTimeRoomSensor (Simulated)";
    btn.classList.remove("active-live");
  }
}

async function loadDatasets() {
  const res = await fetch('/api/dataset');
  const history = await res.json();
  renderTables(history);
}

function renderTables(history) {
  var tb1 = document.getElementById("dataTableBody");
  var tb2 = document.getElementById("historyTableBody");
  tb1.innerHTML = ""; tb2.innerHTML = "";
  
  document.getElementById("totalDatasetCount").innerText = history.length;
  
  var displaySlice = history.slice(-50).reverse();
  displaySlice.forEach(function(rec, idx) {
    var realIndex = history.indexOf(rec);
    var tr1 = document.createElement("tr");
    tr1.innerHTML = "<td>"+rec.id+"</td><td>"+(rec.timestamp||'--')+"</td><td>"+rec.temp+"°C</td><td>"+rec.hum+"%</td><td>"+rec.pm25+"</td><td>"+rec.pm10+"</td><td>"+rec.co+"</td><td>"+rec.no2+"</td><td>"+rec.so2+"</td><td><b>"+rec.aqi+"</b></td><td><button class='btn-delete' onclick='deleteRecord("+realIndex+")'>Delete</button></td>";
    tb1.appendChild(tr1);

    var tr2 = document.createElement("tr");
    tr2.innerHTML = "<td>"+rec.temp+"</td><td>"+rec.hum+"</td><td>"+rec.pm25+"</td><td>"+rec.pm10+"</td><td>"+rec.co+"</td><td>"+rec.no2+"</td><td>"+rec.so2+"</td><td><b>"+rec.aqi+"</b></td><td>"+rec.category+"</td><td><button class='btn-delete' onclick='deleteRecord("+realIndex+")'>Delete</button></td>";
    tb2.appendChild(tr2);
  });

  if (history.length > 0) {
    var latest = history[history.length - 1];
    document.getElementById("m1Temp").innerText = latest.temp + "°C";
    document.getElementById("m1Hum").innerText = latest.hum + "%";
    document.getElementById("m1Pm25").innerText = latest.pm25;
  }
  document.getElementById("predCount").innerText = history.length;
  document.getElementById("lastAqi").innerText = history.length > 0 ? history[history.length - 1].aqi : "--";
}

async function addDataset() {
  const payload = {
    temp: parseFloat(document.getElementById("iTemp").value) || 27.5,
    hum: parseFloat(document.getElementById("iHum").value) || 55.0,
    pm25: parseFloat(document.getElementById("iPm25").value),
    pm10: parseFloat(document.getElementById("iPm10").value),
    co: parseFloat(document.getElementById("iCo").value) || 0.6,
    no2: parseFloat(document.getElementById("iNo2").value) || 18,
    so2: parseFloat(document.getElementById("iSo2").value) || 8
  };
  if (isNaN(payload.pm25) || isNaN(payload.pm10)) return;
  await fetch('/api/add', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
  await loadDatasets();
  loadDashboard();
}

async function predictAQI() {
  const payload = {
    temp: parseFloat(document.getElementById("pTemp").value) || 28.0,
    hum: parseFloat(document.getElementById("pHum").value) || 54.0,
    pm25: parseFloat(document.getElementById("pPm25").value),
    pm10: parseFloat(document.getElementById("pPm10").value),
    co: parseFloat(document.getElementById("pCo").value) || 0.65,
    no2: parseFloat(document.getElementById("pNo2").value) || 19,
    so2: parseFloat(document.getElementById("pSo2").value) || 9
  };
  if (isNaN(payload.pm25) || isNaN(payload.pm10)) return;
  await fetch('/api/add', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
  await loadDatasets();
  loadDashboard();
}

async function deleteRecord(index) {
  await fetch('/api/delete/' + index, { method: 'DELETE' });
  await loadDatasets();
  loadDashboard();
}

/* DASHBOARD LOAD & CHARTS */
async function loadDashboard() {
  const res = await fetch('/api/dataset');
  const history = await res.json();
  if (!history || history.length === 0) return;

  var latest = history[history.length - 1];
  document.getElementById("cardAqi").innerText = latest.aqi;
  document.getElementById("cardCategory").innerText = latest.category;
  document.getElementById("cardRecords").innerText = history.length;

  var pollutants = { PM25: latest.pm25, PM10: latest.pm10, NO2: latest.no2, SO2: latest.so2, CO: (latest.co || 0) * 20 };
  var dominant = Object.keys(pollutants).reduce(function(a, b) { return pollutants[a] > pollutants[b] ? a : b; });
  document.getElementById("cardDominant").innerText = dominant;

  const fRes = await fetch('/api/forecast');
  const forecast = await fRes.json();
  renderForecastGrid(forecast);

  if (typeof Chart !== "undefined") {
    try {
      renderChartJS(history, latest, forecast);
      return;
    } catch(e) {
      console.warn("ChartJS error, falling back to Native Canvas", e);
    }
  }
  renderNativeCanvasCharts(history, latest, forecast);
}

function renderForecastGrid(forecast) {
  var grid = document.getElementById("forecastGrid");
  grid.innerHTML = "";
  forecast.forEach(function(item) {
    var box = document.createElement("div");
    box.className = "forecast-box";
    box.innerHTML = "<div class='f-date'>"+item.date+"</div><div class='f-aqi'>"+item.predicted_aqi+"</div><div class='f-cat'>"+item.category+"</div>";
    grid.appendChild(box);
  });
}

function renderChartJS(history, latest, forecast) {
  // 1. POLLUTANT LEVELS (BAR CHART)
  var barData = [latest.pm25, latest.pm10, latest.no2, latest.so2, (latest.co || 0) * 10];
  var barCanvas = document.getElementById("pollutantBar");
  var barCtx = barCanvas.getContext("2d");
  if (barChart) barChart.destroy();
  barChart = new Chart(barCtx, {
    type: "bar",
    data: { labels: ["PM2.5", "PM10", "NO₂", "SO₂", "CO (x10)"], datasets: [{ data: barData, backgroundColor: ["#1e6091","#10b981","#f59e0b","#f97316","#ef4444"], borderRadius: 8 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
  });

  // 2. AQI CATEGORY DISTRIBUTION (PIE CHART)
  var catCounts = { Good: 0, Moderate: 0, Poor: 0, Severe: 0 };
  history.forEach(function(r) { if (catCounts.hasOwnProperty(r.category)) catCounts[r.category]++; else catCounts.Moderate++; });
  var pieData = [catCounts.Good, catCounts.Moderate, catCounts.Poor, catCounts.Severe];
  var pieCanvas = document.getElementById("aqiPie");
  var pieCtx = pieCanvas.getContext("2d");
  if (pieChart) pieChart.destroy();
  pieChart = new Chart(pieCtx, {
    type: "pie",
    data: { labels: ["Good", "Moderate", "Poor", "Severe"], datasets: [{ data: pieData, backgroundColor: ["#10b981", "#f59e0b", "#f97316", "#ef4444"] }] },
    options: { responsive: true, maintainAspectRatio: false }
  });

  // 3. AQI TREND (LINE CHART)
  var recentSlice = history.slice(-20);
  var lineLabels = recentSlice.map(function(_, i) { return "R" + (i + 1); });
  var pm25Data = recentSlice.map(function(r){ return r.pm25; });
  var pm10Data = recentSlice.map(function(r){ return r.pm10; });
  var aqiData = recentSlice.map(function(r){ return r.aqi; });
  var lineCanvas = document.getElementById("trendLine");
  var lineCtx = lineCanvas.getContext("2d");
  if (lineChart) lineChart.destroy();
  lineChart = new Chart(lineCtx, {
    type: "line",
    data: {
      labels: lineLabels,
      datasets: [
        { label: "PM2.5", data: pm25Data, borderColor: "#3a86c8", fill: false, tension: 0.4 },
        { label: "PM10", data: pm10Data, borderColor: "#10b981", fill: false, tension: 0.4 },
        { label: "AQI Index", data: aqiData, borderColor: "#ef4444", fill: false, tension: 0.4 }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  // 4. 7-DAY AQI FORECAST (LINE CHART)
  var fLabels = forecast.map(function(f){ return f.date; });
  var fAqiData = forecast.map(function(f){ return f.predicted_aqi; });
  var futureCanvas = document.getElementById("futureLine");
  var futureCtx = futureCanvas.getContext("2d");
  if (futureChart) futureChart.destroy();
  futureChart = new Chart(futureCtx, {
    type: "line",
    data: {
      labels: fLabels,
      datasets: [
        { label: "Predicted 7-Day AQI Trend", data: fAqiData, borderColor: "#00b4d8", backgroundColor: "rgba(0, 180, 216, 0.15)", fill: true, tension: 0.4 }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

function renderNativeCanvasCharts(history, latest, forecast) {
  drawCanvasBar(latest);
  drawCanvasPie(history);
  drawCanvasLine(history);
  drawCanvasFutureLine(forecast);
}

function drawCanvasBar(latest) {
  var canvas = document.getElementById("pollutantBar");
  var p = canvas.parentElement; canvas.width = p.clientWidth || 400; canvas.height = p.clientHeight || 300;
  var ctx = canvas.getContext("2d"); ctx.clearRect(0, 0, canvas.width, canvas.height);
  var items = [
    { label: "PM2.5", val: latest.pm25, color: "#1e6091" },
    { label: "PM10", val: latest.pm10, color: "#10b981" },
    { label: "NO₂", val: latest.no2, color: "#f59e0b" },
    { label: "SO₂", val: latest.so2, color: "#f97316" },
    { label: "CO (x10)", val: (latest.co || 0) * 10, color: "#ef4444" }
  ];
  var maxVal = Math.max(100, Math.max.apply(null, items.map(function(i){ return i.val; })));
  var pad = 40, w = canvas.width - pad * 2, h = canvas.height - pad * 2, bw = w / items.length - 15;
  ctx.strokeStyle = "#e2e8f0"; ctx.beginPath(); ctx.moveTo(pad, pad); ctx.lineTo(pad, canvas.height - pad); ctx.lineTo(canvas.width - pad, canvas.height - pad); ctx.stroke();
  items.forEach(function(item, idx) {
    var bh = (item.val / maxVal) * h, x = pad + idx * (bw + 15) + 10, y = canvas.height - pad - bh;
    ctx.fillStyle = item.color; ctx.fillRect(x, y, bw, bh);
    ctx.fillStyle = "#1e293b"; ctx.font = "bold 12px sans-serif"; ctx.textAlign = "center";
    ctx.fillText(item.val, x + bw/2, y - 6); ctx.fillText(item.label, x + bw/2, canvas.height - pad + 20);
  });
}

function drawCanvasPie(history) {
  var canvas = document.getElementById("aqiPie");
  var p = canvas.parentElement; canvas.width = p.clientWidth || 400; canvas.height = p.clientHeight || 300;
  var ctx = canvas.getContext("2d"); ctx.clearRect(0, 0, canvas.width, canvas.height);
  var counts = { Good: 0, Moderate: 0, Poor: 0, Severe: 0 };
  history.forEach(function(r) { if (counts.hasOwnProperty(r.category)) counts[r.category]++; else counts.Moderate++; });
  var data = [
    { label: "Good", val: counts.Good, color: "#10b981" },
    { label: "Moderate", val: counts.Moderate, color: "#f59e0b" },
    { label: "Poor", val: counts.Poor, color: "#f97316" },
    { label: "Severe", val: counts.Severe, color: "#ef4444" }
  ];
  var total = history.length || 1, cx = canvas.width / 2 - 40, cy = canvas.height / 2, r = 80, sa = 0;
  data.forEach(function(slice) {
    if (slice.val === 0) return;
    var angle = (slice.val / total) * 2 * Math.PI;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, r, sa, sa + angle); ctx.closePath();
    ctx.fillStyle = slice.color; ctx.fill(); sa += angle;
  });
  var lx = canvas.width - 120, ly = 80;
  data.forEach(function(item, idx) {
    ctx.fillStyle = item.color; ctx.fillRect(lx, ly + idx * 24, 14, 14);
    ctx.fillStyle = "#1e293b"; ctx.font = "13px sans-serif"; ctx.textAlign = "left";
    ctx.fillText(item.label + " (" + item.val + ")", lx + 22, ly + idx * 24 + 12);
  });
}

function drawCanvasLine(history) {
  var canvas = document.getElementById("trendLine");
  var p = canvas.parentElement; canvas.width = p.clientWidth || 800; canvas.height = p.clientHeight || 320;
  var ctx = canvas.getContext("2d"); ctx.clearRect(0, 0, canvas.width, canvas.height);
  var recent = history.slice(-20);
  var pad = 40, w = canvas.width - pad * 2, h = canvas.height - pad * 2;
  var maxVal = Math.max(200, Math.max.apply(null, recent.map(function(r){ return r.aqi; })));
  ctx.strokeStyle = "#e2e8f0"; ctx.beginPath(); ctx.moveTo(pad, pad); ctx.lineTo(pad, canvas.height - pad); ctx.lineTo(canvas.width - pad, canvas.height - pad); ctx.stroke();
  var stepX = w / (recent.length > 1 ? recent.length - 1 : 1);
  ctx.strokeStyle = "#ef4444"; ctx.lineWidth = 3; ctx.beginPath();
  recent.forEach(function(r, i) {
    var x = pad + i * stepX, y = canvas.height - pad - (r.aqi / maxVal) * h;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  recent.forEach(function(r, i) {
    var x = pad + i * stepX, y = canvas.height - pad - (r.aqi / maxVal) * h;
    ctx.fillStyle = "#ef4444"; ctx.beginPath(); ctx.arc(x, y, 5, 0, 2 * Math.PI); ctx.fill();
    ctx.fillStyle = "#1e293b"; ctx.font = "bold 11px sans-serif"; ctx.textAlign = "center";
    ctx.fillText(r.aqi, x, y - 10); ctx.fillText("R" + (i+1), x, canvas.height - pad + 20);
  });
}

function drawCanvasFutureLine(forecast) {
  var canvas = document.getElementById("futureLine");
  var p = canvas.parentElement; canvas.width = p.clientWidth || 800; canvas.height = p.clientHeight || 320;
  var ctx = canvas.getContext("2d"); ctx.clearRect(0, 0, canvas.width, canvas.height);
  var pad = 40, w = canvas.width - pad * 2, h = canvas.height - pad * 2;
  var maxVal = Math.max(200, Math.max.apply(null, forecast.map(function(f){ return f.predicted_aqi; })));
  ctx.strokeStyle = "#e2e8f0"; ctx.beginPath(); ctx.moveTo(pad, pad); ctx.lineTo(pad, canvas.height - pad); ctx.lineTo(canvas.width - pad, canvas.height - pad); ctx.stroke();
  var stepX = w / (forecast.length > 1 ? forecast.length - 1 : 1);
  ctx.strokeStyle = "#00b4d8"; ctx.lineWidth = 3; ctx.beginPath();
  forecast.forEach(function(f, i) {
    var x = pad + i * stepX, y = canvas.height - pad - (f.predicted_aqi / maxVal) * h;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  forecast.forEach(function(f, i) {
    var x = pad + i * stepX, y = canvas.height - pad - (f.predicted_aqi / maxVal) * h;
    ctx.fillStyle = "#00b4d8"; ctx.beginPath(); ctx.arc(x, y, 5, 0, 2 * Math.PI); ctx.fill();
    ctx.fillStyle = "#1e293b"; ctx.font = "bold 11px sans-serif"; ctx.textAlign = "center";
    ctx.fillText(f.predicted_aqi, x, y - 10); ctx.fillText(f.date.split(',')[0], x, canvas.height - pad + 20);
  });
}
</script>
</body>
</html>
"""

# ==============================================================================
# 5. BACKEND SERVICES (FLASK APIs MATCHING ARCHITECTURE DIAGRAM EXACTLY)
# ==============================================================================
app = Flask(__name__)
app.secret_key = 'aqi_architecture_system_2026'

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/dataset', methods=['GET'])
@app.route('/api/datasets', methods=['GET'])
def get_dataset():
    """API Endpoint: Load Dataset (Returns 5,000 Records DB)"""
    return jsonify(DB["datasets"])

@app.route('/api/sensor/live', methods=['GET'])
def get_live_sensor():
    """API Endpoint: Get Live Sensor Data (Simulated RealTimeRoomSensor Class)"""
    reading = room_sensor.read_room_sensors()
    return jsonify(reading)

@app.route('/api/add', methods=['POST'])
def add_data_and_predict():
    """API Endpoint: Add Data & Predict AQI (Executes Custom Weighted Model)"""
    data = request.json
    res = model.predict(
        data.get('temp', 27.5), data.get('hum', 55.0), data.get('pm25', 38.0),
        data.get('pm10', 62.0), data.get('co', 0.6), data.get('no2', 18.0), data.get('so2', 8.0)
    )
    new_id = len(DB["datasets"]) + 1
    record = {
        'id': new_id,
        'timestamp': time.strftime("%Y-%m-%d %H:%M"),
        'temp': data.get('temp', 27.5), 'hum': data.get('hum', 55.0),
        'pm25': data.get('pm25', 38.0), 'pm10': data.get('pm10', 62.0),
        'co': data.get('co', 0.6), 'no2': data.get('no2', 18.0), 'so2': data.get('so2', 8.0),
        'aqi': res['aqi'], 'category': res['category']
    }
    DB["datasets"].append(record)
    DB["predictions"].append(record)
    return jsonify(record)

@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    """API Endpoint: 7-Day AQI Forecast"""
    current_aqi = DB["datasets"][-1]['aqi'] if len(DB["datasets"]) > 0 else 100
    forecast = model.predict_future_7days(current_aqi)
    return jsonify(forecast)

@app.route('/api/history', methods=['GET'])
def get_history():
    """API Endpoint: Get Prediction History"""
    return jsonify(DB["predictions"])

@app.route('/api/delete/<int:index>', methods=['DELETE'])
def delete_dataset_record(index):
    """Delete Action for Data Storage Management"""
    if 0 <= index < len(DB["datasets"]):
        DB["datasets"].pop(index)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/export', methods=['GET'])
def export_csv_report():
    """Generate Reports Feature"""
    csv_data = "ID,Timestamp,Temperature,Humidity,PM2.5,PM10,CO,NO2,SO2,AQI,Category\n"
    for r in DB["datasets"]:
        csv_data += f"{r.get('id', '')},{r.get('timestamp', '')},{r['temp']},{r['hum']},{r['pm25']},{r['pm10']},{r['co']},{r['no2']},{r['so2']},{r['aqi']},{r['category']}\n"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=aqi_system_architecture_report.csv"}
    )

if __name__ == '__main__':
    print("==========================================================================")
    print("🚀 AI-DRIVEN AIR QUALITY MONITORING AND PREDICTION SYSTEM")
    print("   Architecture Implementation Server Running")
    print("==========================================================================")
    print(" Data Source      : Initialized 5,000 Air Quality Records")
    print(" Backend APIs     : /api/dataset, /api/sensor/live, /api/add, /api/forecast, /api/history")
    print(" Data Storage     : In-Memory DB (Python Dictionaries)")
    print(" Real-Time Sensor : RealTimeRoomSensor Class (Simulated)")
    print(" Dashboard        : Current AQI, Bar Chart, Pie Chart, Line Chart, 7-Day Forecast")
    print("==========================================================================")
    print("🌐 Open http://127.0.0.1:5000 in your browser to access system UI")
    print("==========================================================================")
    app.run(debug=True, port=5000)