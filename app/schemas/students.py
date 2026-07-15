# app/schemas/students.py
# app/schemas/students.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from pydantic import ConfigDict

class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Student's full name")
    email: EmailStr = Field(..., max_length=100)
    grade_level: int = Field(..., ge=1, le=12, description="Grade level from school year 1 to 12")
    gpa: float = Field(..., ge=0.0, le=4.0, description="Grade Point Average bounds")
    is_enrolled: bool = Field(default=True)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

class StudentPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    grade_level: Optional[int] = Field(None, ge=1, le=12)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    is_enrolled: Optional[bool] = None




class StudentResponse(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)