"""
Log Tracker API entry point.

Exposes endpoints for submitting and retrieving log lines.
Storage is backed by a dedicated SQLite file.
"""

import time

from fastapi import FastAPI, Query

APP_VERSION = "0.1.0"
_start_time = time.time()

app = FastAPI(title="Log Tracker Service")


@app.get("/version")
async def get_version():
    """Returns the semver version of the service as JSON."""
    return {"version": APP_VERSION}


@app.get("/info")
async def get_info():
    """Returns service capabilities, limits, and runtime metadata."""
    uptime_seconds = int(time.time() - _start_time)
    return {
        "version": APP_VERSION,
        "supported_input_formats": ["list_of_strings", "list_of_objects"],
        "storage_backend": "sqlite",
        "max_line_size_bytes": 16384,
        "retention_policy": "fifo",
        "uptime_seconds": uptime_seconds,
    }


@app.post("/logs", status_code=201)
async def post_logs(logs: list[str | dict]):
    """
    Accepts log data as JSON.

    Arguments:
        logs: A list where each element is either a plain string
              or an object with 'metadata' and 'line' keys.

    Returns:
        JSON with the count of accepted log lines.
    """
    # TODO: implement SQLite storage, line size validation, FIFO eviction
    return {"accepted": len(logs)}


@app.get("/logs")
async def get_logs(
    start: str | None = Query(None, description="ISO8601 start time"),
    end: str | None = Query(None, description="ISO8601 end time"),
):
    """
    Retrieves log lines filtered by time range.

    Arguments:
        start: Optional ISO8601 timestamp for range start.
        end:   Optional ISO8601 timestamp for range end.

    Returns:
        JSON array of log line strings.
    """
    # TODO: implement SQLite retrieval with time range filtering
    return []
