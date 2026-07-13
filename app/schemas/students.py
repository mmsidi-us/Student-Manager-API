# app/schemas/students.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    name: str
    email: EmailStr
    grade_level: int = Field(..., ge=1, le=12, description="Grade level must be between 1 and 12")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    is_enrolled: bool = True

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass  # Full resource replacement 

class StudentPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    grade_level: Optional[int] = Field(None, ge=1, le=12)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    is_enrolled: Optional[bool] = None

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True