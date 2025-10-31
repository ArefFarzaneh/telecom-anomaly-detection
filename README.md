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

## Project Structure
