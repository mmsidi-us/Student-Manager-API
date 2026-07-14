# app/main.py
"""
================================================================================
🔒 STUDENT-MANAGER-API SECURITY HARDENING SUMMARY
================================================================================
The following security layers are active within this application:

1. CORS Policy Enforcement:
   - Restricts cross-origin requests specifically to local developer instances:
     * Streamlit frontend (http://localhost:8501)
     * React frontend (http://localhost:3000)
   - Restricts HTTP methods strictly to: GET, POST, PUT, PATCH, DELETE.

2. Rate Limiting (slowapi):
   - Prevents brute-force and Denial-of-Service (DoS) attacks using client IP limits:
     * Authentication (/auth/login) capped at 5 requests/minute.
     * Record Creation (POST /students) capped at 20 requests/minute.
     * General Directory Exploration (GET) capped at 60 requests/minute.

3. Strict Payload Validation (Pydantic Constraints):
   - Mitigates buffer-overflow and SQL/NoSQL injections.
   - Restricts string fields with 'max_length' and numeric values with 'ge' and 'le'.

4. Secure Password Hashing:
   - Utilizes bcrypt (via PassLib) with a manual 72-byte truncation boundary.
================================================================================
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.models import students, users
from app.routers import students as students_router, auth as auth_router

from app.utils.limiter import limiter

# 1. Initialize Rate Limiter

app = FastAPI(title="Student Manager API")

# Link SlowAPI's exception handler to FastAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Configure CORS Middleware
allowed_origins = [
    "http://localhost:8501",  # Streamlit
    "http://localhost:3000",  # React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # Restrict to used methods
    allow_headers=["*"],
)

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

# Include Routers
app.include_router(auth_router.router)
app.include_router(students_router.router)

@app.get("/")
def root():
    return {"message": "Secured Student Manager API is online!"}

# --- Global Exception Handlers ---
from app.utils.exceptions import AppException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handles custom domain business exceptions (400, 404, 409)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Fallback catch-all for raw code failures."""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "detail": "An internal server error occurred",
            "status_code": 500
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Cleaner payload formatting for Pydantic failures."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "detail": "Validation failed",
            "errors": errors
        }
    )