# app/routers/students.py
from fastapi import APIRouter, Depends, status, BackgroundTasks, Request # Import Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils.limiter import limiter  #

from app.database import get_db
from app.models.students import Student
from app.schemas.students import StudentCreate, StudentUpdate, StudentPatch, StudentResponse
from app.utils.exceptions import NotFoundException, DuplicateException, BadRequestException
from app.utils.security import get_current_user
from app.models.users import User
# Import the new background utilities
from app.utils.notifications import log_activity, send_notification


# app/routers/students.py (Partial Update - showcasing dependency placements)
from app.utils.security import get_current_user
from app.models.users import User # Import user model

router = APIRouter(prefix="/students", tags=["Students"])

def get_student_or_404(student_id: int, db: Session) -> Student:
    """Helper function to fetch resource or trigger custom 404."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFoundException(resource="Student", resource_id=student_id)
    return student

# --- Protected POST Endpoint ---
@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def create_student(
    request: Request,
    payload: StudentCreate, 
    background_tasks: BackgroundTasks,  # Inject BackgroundTasks dependency
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Student).filter(Student.email == payload.email).first()
    if existing:
        raise DuplicateException(resource="Student", field="email", value=payload.email)
    
    new_student = Student(**payload.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    # Enqueue tasks to run immediately AFTER the HTTP response is dispatched
    background_tasks.add_task(
        log_activity, 
        user_id=current_user.id, 
        action=f"Created student record for '{new_student.name}' (ID: {new_student.id})"
    )
    background_tasks.add_task(
        send_notification, 
        email=new_student.email, 
        message=f"Welcome {new_student.name}! Your student record has been successfully created."
    )
    
    return new_student

# 1. GET ALL STUDENTS (Keep Public)
@router.get("/", response_model=List[StudentResponse])
@limiter.limit("60/minute")
def get_students(request: Request,grade_level: Optional[int] = None, is_enrolled: Optional[bool] = None, db: Session = Depends(get_db)):
    # Same code remains completely accessible to anyone...
    # 2. Get with filters
    query = db.query(Student)
    if grade_level is not None:
        query = query.filter(Student.grade_level == grade_level)
    if is_enrolled is not None:
        query = query.filter(Student.is_enrolled == is_enrolled)
    return query.all()

@router.get("/{id}", response_model=StudentResponse)
def get_student(id: int, db: Session = Depends(get_db)):
    # 3. Get specific student with 404 handling helper
    return get_student_or_404(id, db)

@router.put("/{id}", response_model=StudentResponse)
def update_student(id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    # 4. Full replacement
    student = get_student_or_404(id, db)
    
    if student.email != payload.email:
        existing = db.query(Student).filter(Student.email == payload.email).first()
        if existing:
            raise DuplicateException(resource="Student", field="email", value=payload.email)
            
    for key, value in payload.model_dump().items():
        setattr(student, key, value)
        
    db.commit()
    db.refresh(student)
    return student

# 3. PATCH STUDENT (Protected)
@router.patch("/{id}", response_model=StudentResponse)
def patch_student(id: int, payload: StudentPatch, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):    # 5. Partial update
    student = get_student_or_404(id, db)
    
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] != student.email:
        existing = db.query(Student).filter(Student.email == data["email"]).first()
        if existing:
            raise DuplicateException(resource="Student", field="email", value=data["email"])
            
    for key, value in data.items():
        setattr(student, key, value)
        
    db.commit()
    db.refresh(student)
    return student

# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_student(id: int, db: Session = Depends(get_db)):
# --- Protected DELETE Endpoint ---
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    id: int, 
    background_tasks: BackgroundTasks,  # Inject BackgroundTasks dependency
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise NotFoundException(resource="Student", resource_id=id)
        
    if student.is_enrolled:
        raise AppException(detail="Cannot delete an actively enrolled student. Unenroll them first.", status_code=400)
        
    student_name = student.name  # Cache the name string before removing from DB
    db.delete(student)
    db.commit()
    
    # Enqueue logging task in the background
    background_tasks.add_task(
        log_activity, 
        user_id=current_user.id, 
        action=f"Deleted student record for '{student_name}' (ID: {id})"
    )
    
    return None