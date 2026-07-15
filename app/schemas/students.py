# app/schemas/students.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class StudentBase(BaseModel):
    name: str = Field(..., description="The full legal name of the student")
    email: EmailStr = Field(..., description="The official institutional email address")
    grade_level: int = Field(..., ge=1, le=12, description="The current grade level (1 through 12)")
    gpa: float = Field(..., ge=0.0, le=4.0, description="The Cumulative Grade Point Average (0.0 to 4.0)")

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    is_enrolled: bool

    # Pydantic V2 modern configuration with illustrative example schema
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Sidi Mohamed",
                "email": "sidi@example.com",
                "grade_level": 11,
                "gpa": 3.95,
                "is_enrolled": True
            }
        }
    )