from fastapi import FastAPI

app = FastAPI(title="Notification Service")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Welcome to the Notification API"}
