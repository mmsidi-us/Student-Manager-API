# app/models/students.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    grade_level = Column(Integer, nullable=False)
    gpa = Column(Float, nullable=True)
    is_enrolled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    # Added to match the StudentResponse schema requirements
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
