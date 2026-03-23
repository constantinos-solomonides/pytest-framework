"""
Notification Service stub.

Accepts structured messages from pipeline stages. Currently a stub;
actual platform integrations (Slack, email, MR comments) are future work.
"""

from fastapi import FastAPI

APP_VERSION = "0.1.0"

app = FastAPI(title="Notification Service")


@app.get("/health")
async def health_check():
    """Returns service health status."""
    return {"status": "healthy", "version": APP_VERSION}


@app.post("/notify", status_code=202)
async def notify(payload: dict):
    """
    Accepts a notification payload and acknowledges receipt.

    Arguments:
        payload: Arbitrary JSON object describing the notification.

    Returns:
        JSON acknowledgement. Actual delivery is not implemented in v1.
    """
    # TODO: implement forwarding to configured targets
    return {"accepted": True, "message": "stub - no delivery in v1"}
