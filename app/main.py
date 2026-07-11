# app/main.py
from fastapi import FastAPI
from app.database import engine, Base, get_db
from app.models.students import Student
from app.routers import students
from app.schemas.students import StudentCreate, StudentResponse
from app.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Manager API")
app.include_router(students.router)

@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs"}