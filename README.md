# Telecom Sector Anomaly Detection Dashboard

**Real-time KPI monitoring and anomaly detection for telecom sectors across Iran**, powered by **FastAPI**, **WebSockets**, **Leaflet.js**, and **scikit-learn Isolation Forest**.

This end-to-end Python project simulates live telecom network KPIs (payload, throughput, PRB utilization, availability) from 500+ sectors across Iran, detects anomalies in real time using an adaptive machine learning model, and visualizes results on an interactive map and live dashboard.

---

## Features

- **Live KPI Simulation** – Generates realistic, time-varying KPIs per sector with seasonal patterns and noise.
- **Real-time Anomaly Detection** – Uses **Isolation Forest** with rolling window retraining every 60 seconds.
- **WebSocket Streaming** – Pushes updates instantly to all connected clients.
- **Interactive Map** – Leaflet-based map centered on Iran with color-coded sector markers (Green = Normal, Red = Anomaly).
- **Live Dashboard** – Alternative `/static/index.html` view showing raw stream and anomaly feed.
- **Adaptive Learning** – Model retrains on recent data to adapt to changing network behavior.
- **Scalable Architecture** – Async queue-based pipeline: Simulator → Detector → Broadcaster.

---

---

## How It Works

1. **`simulator.py`**  
   Generates batches of KPI data every ~2.5 seconds for 500 sectors. Each sector has:
   - Fixed location near a province center
   - Baseline payload + sinusoidal variation + Gaussian noise
   - Derived metrics: throughput, PRB, availability

2. **`anomaly.py`**  
   - Consumes batches via `asyncio.Queue`
   - Trains initial **Isolation Forest** on first 5 batches
   - Scores incoming data in real time
   - Retrains every 60s on rolling window (2000 samples)
   - Flags anomalies (`is_anomaly: true`)

3. **`main.py`**  
   - FastAPI server with WebSocket endpoint `/ws/kpi`
   - Broadcasts enriched KPI + anomaly flag to all clients
   - Serves map at `/` and dashboard at `/static/index.html`

4. **Frontend**  
   - `map.html`: Interactive Iran map with dynamic markers
   - `index.html`: Text-based live feed + anomaly list

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/telecom-anomaly-dashboard.git
cd telecom-anomaly-dashboard
```
## Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
# or
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Open in browser
Interactive Map: http://localhost:8000
Live Dashboard: http://localhost:8000/static/index.html
