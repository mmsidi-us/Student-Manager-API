from pydantic import BaseModel, Field, EmailStr
from pydantic import BaseModel, ConfigDict
class UserCreate(BaseModel):
    
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr = Field(..., max_length=100)
   
    password: str = Field(..., min_length=6, max_length=72, description="Password max limits match bcrypt limits")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)