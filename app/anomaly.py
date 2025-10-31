# app/anomaly.py
import asyncio
from typing import List, Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import deque
import time

class AnomalyDetector:
    def __init__(self, queue: asyncio.Queue, broadcaster, window_size: int = 2000):
        """
        queue: incoming batches (list of kpi dicts)
        broadcaster: ConnectionManager instance with broadcast_json method
        window_size: how many recent samples to keep for retraining
        """
        self.queue = queue
        self.broadcaster = broadcaster
        self.window = deque(maxlen=window_size)  # store numeric vectors
        self.model = None
        self.retrain_interval = 60.0  # seconds
        self.last_retrain = 0.0

    def _feature_vector(self, k: Dict[str, Any]):
        # Build a feature vector for the model from kpi dict
        # Example: payload, thr, prb, avail
        return [k["payload"], k["thr"], k["prb"], k["avail"]]

    def _train_initial(self, samples: List[Dict[str, Any]]):
        X = np.array([self._feature_vector(x) for x in samples])
        model = IsolationForest(contamination=0.01, random_state=42, n_jobs=1)
        model.fit(X)
        self.model = model
        for row in X:
            self.window.append(row)

    async def run(self):
        # Warm start: collect a few batches to build a baseline
        collected = []
        print("[detector] warming up, collecting initial samples...")
        while len(collected) < 5:  # collect 5 batches
            batch = await self.queue.get()
            collected.extend(batch)
        self._train_initial(collected)
        print("[detector] initial model trained.")

        while True:
            batch = await self.queue.get()
            # prepare numeric matrix
            X_batch = np.array([self._feature_vector(x) for x in batch])
            is_anomaly = [False] * len(batch)
            if self.model is not None:
                preds = self.model.predict(X_batch)  # -1 anomaly, 1 normal
                is_anomaly = [True if p == -1 else False for p in preds]
            # push results to frontend
            timestamp = time.time()
            for item, anomaly_flag in zip(batch, is_anomaly):
                item["is_anomaly"] = bool(anomaly_flag)
                item["sent_at"] = timestamp
                # send to all connected clients
                await self.broadcaster.broadcast_json({"type": "kpi_update", "payload": item})

            # append to rolling window and maybe retrain
            for row in X_batch:
                self.window.append(row)

            if time.time() - self.last_retrain > self.retrain_interval:
                # Retrain model on the rolling window (simulate adaptive learning)
                try:
                    X_retrain = np.array(self.window)
                    if len(X_retrain) >= 50:
                        model = IsolationForest(contamination=0.01, random_state=42, n_jobs=1)
                        model.fit(X_retrain)
                        self.model = model
                        self.last_retrain = time.time()
                        print(f"[detector] retrained model at {self.last_retrain}, window={len(X_retrain)}")
                except Exception as e:
                    print("[detector] retrain failed:", e)
