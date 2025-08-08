from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.accounts.routes import router as accounts_router

app = FastAPI(title="Bank Account Management System", version="1.0.0", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Bank Account Management System API!"}
