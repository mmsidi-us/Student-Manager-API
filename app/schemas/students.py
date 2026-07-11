# app/schemas/book.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    name: str 
    email: EmailStr  # Automatically validates proper email formats
    grade_level: Optional[int] = Field(default=None, ge=1, le=12)  # Fixed: numeric limits
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0)
    is_enrolled: bool = Field(default=True)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    """Full update — all fields required."""
    pass

class StudentPatch(BaseModel):
    """Partial update — all fields optional."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    grade_level: Optional[int] = Field(default=None, ge=1, le=12)
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0)
    is_enrolled: Optional[bool] = None

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True