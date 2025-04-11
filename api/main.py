from fastapi import FastAPI
from api.v1.endpoints import accounts

app = FastAPI(title="Banking System API")

# Include the API routes
app.include_router(accounts.router, prefix="/v1", tags=["accounts"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)