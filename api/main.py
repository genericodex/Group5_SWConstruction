from fastapi import FastAPI
from api.v1.endpoints import accounts

from domain.accounts import AccountType
from infrastructure.Authentication.login import InMemoryAuthenticationService

app = FastAPI(title="Banking System API")

# Include the API routes
app.include_router(accounts.router, prefix="/v1", tags=["accounts"])

# Initialize the authentication service
auth_service = InMemoryAuthenticationService()


@app.on_event("startup")
async def startup_event():
    """
    Register demo accounts on startup.
    """
    print("Starting up the Banking System API...")

    # Register sample accounts
    print("Registering accounts...")
    auth_service.register(
        account_id="123",
        username="user1",
        password="password123",
        account_type=AccountType.SAVINGS
    )
    auth_service.register(
        account_id="456",
        username="user2",
        password="securePass456",
        account_type=AccountType.CHECKING
    )
    print("Accounts registered!")

    # Logging in as a demonstration
    print("Demonstration: Logging in...")
    try:
        logged_in_account = auth_service.login(username="user1", password="password123")
        print(f"Login successful! Welcome, {logged_in_account.username}. Account ID: {logged_in_account.account_id}")
    except ValueError as e:
        print(f"Login failed: {e}")

    print("Attempting invalid login...")
    try:
        auth_service.login(username="user1", password="wrongPassword")
    except ValueError as e:
        print(f"Login failed: {e}")

    print("Logging in as user2...")
    try:
        logged_in_account = auth_service.login(username="user2", password="securePass456")
        print(f"Login successful! Welcome, {logged_in_account.username}.")
    except ValueError as e:
        print(f"Login failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down the Banking System API...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="debug",
    )
