# app/main.py
import asyncio
import json
from typing import List, Dict, Any, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.simulator import start_simulator, SimulatorMessage
from app.anomaly import AnomalyDetector

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_map():
    with open("app/map.html", "r") as f:
        html = f.read()
    return HTMLResponse(html)

# Simple broadcast manager
class ConnectionManager:
    def __init__(self):
        self.active: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)

    async def broadcast_json(self, message: Dict[str, Any]):
        data = json.dumps(message, default=str)
        to_remove = []
        for ws in list(self.active):
            try:
                await ws.send_text(data)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(ws)


manager = ConnectionManager()

# Shared queue: simulator -> detector -> broadcaster
kpi_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)


@app.on_event("startup")
async def startup_event():
    # Start simulator background task
    loop = asyncio.get_event_loop()
    # Start anomaly detector background task
    detector = AnomalyDetector(queue=kpi_queue, broadcaster=manager)
    loop.create_task(detector.run())      # runs forever
    loop.create_task(start_simulator(kpi_queue, sectors=500, interval=2.5))
    app.state.detector = detector


@app.websocket("/ws/kpi")
async def websocket_kpi(ws: WebSocket):
    await manager.connect(ws)
    try:
        # Keep connection alive while frontend interacts.
        while True:
            # We don't expect incoming messages, but handle ping/pong or future commands
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=60.0)
                # echo or handle subscribe messages later
                await ws.send_text(json.dumps({"info": "server-received", "payload": msg}))
            except asyncio.TimeoutError:
                # send a keepalive ping
                try:
                    await ws.send_text(json.dumps({"ping": "keepalive"}))
                except Exception:
                    break
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:
        manager.disconnect(ws)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
