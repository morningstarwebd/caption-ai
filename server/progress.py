from fastapi import WebSocket
from typing import Dict, List
import threading
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # dictionary mapping job_id to a list of active websocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # thread-safe lock (works across event loops and threads)
        self.lock = threading.Lock()

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        with self.lock:
            if job_id not in self.active_connections:
                self.active_connections[job_id] = []
            self.active_connections[job_id].append(websocket)
        logger.info(f"WebSocket connected for job {job_id}")

    async def disconnect(self, websocket: WebSocket, job_id: str):
        with self.lock:
            if job_id in self.active_connections:
                try:
                    self.active_connections[job_id].remove(websocket)
                except ValueError:
                    pass
                if not self.active_connections[job_id]:
                    del self.active_connections[job_id]
        logger.info(f"WebSocket disconnected for job {job_id}")

    async def broadcast_progress(self, job_id: str, status: str, percent: int, details: str = ""):
        message = {
            "type": "progress",
            "job_id": job_id,
            "status": status,
            "percent": percent,
            "details": details
        }
        
        with self.lock:
            connections = list(self.active_connections.get(job_id, []))

        dead = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to websocket, removing: {e}")
                dead.append(connection)

        if dead:
            with self.lock:
                for conn in dead:
                    if job_id in self.active_connections:
                        try:
                            self.active_connections[job_id].remove(conn)
                        except ValueError:
                            pass

    async def broadcast(self, job_id: str, data: dict):
        # Allow sending generic dictionaries 
        message = {
            "type": "progress",
            "job_id": job_id,
            **data
        }
        with self.lock:
            connections = list(self.active_connections.get(job_id, []))

        dead = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to websocket, removing: {e}")
                dead.append(connection)

        if dead:
            with self.lock:
                for conn in dead:
                    if job_id in self.active_connections:
                        try:
                            self.active_connections[job_id].remove(conn)
                        except ValueError:
                            pass

manager = ConnectionManager()
