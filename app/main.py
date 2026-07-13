# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database import engine, Base
from app.routers import students
from app.config import settings
from app.utils.exceptions import AppException

# 1. Initialize DB tables on startup
Base.metadata.create_all(bind=engine)

# 2. Single unified FastAPI instance
app = FastAPI(title="Student Manager API")

# 3. Include Routers
app.include_router(students.router)

@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs"}

# --- Global Exception Handlers ---

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