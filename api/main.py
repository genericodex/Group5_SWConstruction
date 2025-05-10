from fastapi import FastAPI
from api.v1.endpoints import accounts, notifications, logs

app = FastAPI(
    title="Banking System API",
    description="API for banking operations including accounts, transactions, transfers, and adapters",
    version="1.0.0"
)

# Include the API routes
app.include_router(accounts.router, prefix="/v1", tags=["accounts"])
app.include_router(notifications.router, prefix="/v1", tags=["adapters"])
app.include_router(logs.router, prefix="/v1", tags=["logs"])

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="debug",
    )