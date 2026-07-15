# app/routers/auth.py
from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.users import UserCreate, UserResponse
from app.utils.limiter import limiter
from app.database import get_db
from app.models.users import User
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse
from app.utils.exceptions import DuplicateException, AppException
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # Check for existing username or email
    if db.query(User).filter(User.username == payload.username).first():
        raise DuplicateException(resource="User", field="username", value=payload.username)
    if db.query(User).filter(User.email == payload.email).first():
        raise DuplicateException(resource="User", field="email", value=payload.email)

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request,form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AppException(detail="Incorrect username or password", status_code=401)
        
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user