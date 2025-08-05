from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.accounts.routes import router as account_router

app = FastAPI(
    title="Bank Account Management System",
    description="A simplified digital banking system built with FastAPI and MongoDB",
    version="1.0.0"
)

# Allow frontend clients (adjust the origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication and account routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(account_router, prefix="/accounts", tags=["Accounts"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Bank Account Management System API!"}
