# app/simulator.py
import asyncio
import random
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any

@dataclass
class SimulatorMessage:
    sector_id: str
    province: str
    lat: float
    lon: float
    payload: float
    thr: float
    prb: float
    avail: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# Simplified bounding boxes for provinces (roughly)
PROVINCE_COORDS = {
    "Tehran": (35.7, 51.4),
    "Isfahan": (32.65, 51.67),
    "Fars": (29.6, 52.5),
    "Khorasan": (36.3, 59.6),
    "East Azerbaijan": (38.1, 46.3),
    "West Azerbaijan": (37.6, 45.0),
    "Mazandaran": (36.5, 52.3),
    "Gilan": (37.3, 49.6),
    "Kerman": (30.3, 57.1),
    "Hormozgan": (27.2, 56.3),
    "Sistan-Baluchestan": (28.6, 61.0),
}

def base_value_for_sector(idx: int):
    return 100 + (idx % 50) * 2

async def start_simulator(queue: asyncio.Queue, sectors: int = 200, interval: float = 2.0):
    provinces = list(PROVINCE_COORDS.keys())
    sectors_meta = []

    # pre-generate lat/lon near province centers
    for i in range(sectors):
        sector_id = f"IR_SECT_{i:04d}"
        province = provinces[i % len(provinces)]
        base_lat, base_lon = PROVINCE_COORDS[province]
        lat = base_lat + random.uniform(-0.4, 0.4)
        lon = base_lon + random.uniform(-0.4, 0.4)
        baseline = base_value_for_sector(i)
        sectors_meta.append((sector_id, province, lat, lon, baseline))

    t = 0.0
    while True:
        batch = []
        for idx, (sector_id, province, lat, lon, baseline) in enumerate(sectors_meta):
            sin_component = 20.0 * math.sin(t / 60.0 + (idx % 7))
            noise = random.normalvariate(0, 5.0)
            payload = max(1.0, baseline + sin_component + noise)
            thr = max(0.1, (payload / (10 + random.random()*5)))
            prb = min(99.9, max(1.0, 40 + (payload % 60) * 0.5 + random.normalvariate(0,4)))
            avail = max(90.0, 99.9 - abs(random.normalvariate(0, 0.4)))

            msg = SimulatorMessage(
                sector_id=sector_id,
                province=province,
                lat=round(lat, 4),
                lon=round(lon, 4),
                payload=round(payload, 3),
                thr=round(thr, 3),
                prb=round(prb, 3),
                avail=round(avail, 3),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            batch.append(msg.to_dict())

        await queue.put(batch)
        t += interval
        await asyncio.sleep(interval)
