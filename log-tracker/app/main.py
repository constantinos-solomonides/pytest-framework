from fastapi import FastAPI, Query
from typing import List, Union, Dict, Optional

app = FastAPI(title="Log Tracker Service")

@app.get("/version")
async def get_version():
    return {"version": "0.1.0"}

@app.get("/logs")
async def get_logs(start: Optional[str] = None, end: Optional[str] = None):
    return []

@app.post("/logs")
async def post_logs(logs: List[Union[str, Dict]]):
    return {"count": len(logs)}

@app.get("/info")
async def get_info():
    return {
        "supported_input_formats": ["json"],
        "storage_backend": "sqlite",
        "max_line_size": 16384,
        "uptime": "0s",
        "retention_policy": "FIFO"
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the Log Tracker API"}
