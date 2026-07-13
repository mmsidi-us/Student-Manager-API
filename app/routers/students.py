# app/routers/students.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.students import Student
from app.schemas.students import StudentCreate, StudentUpdate, StudentPatch, StudentResponse
from app.utils.exceptions import NotFoundException, DuplicateException, BadRequestException

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

# 2. POST STUDENT (Protected)
@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Code execution only happens if token checks out    # 1. Duplicate email handling
    existing = db.query(Student).filter(Student.email == payload.email).first()
    if existing:
        raise DuplicateException(resource="Student", field="email", value=payload.email)
    
    new_student = Student(**payload.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

# 1. GET ALL STUDENTS (Keep Public)
@router.get("/", response_model=List[StudentResponse])
def get_students(grade_level: Optional[int] = None, is_enrolled: Optional[bool] = None, db: Session = Depends(get_db)):
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
# 4. DELETE STUDENT (Protected)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 6. Delete endpoint with business rule exception
    student = get_student_or_404(id, db)
    
    # Custom rule: active students cannot be deleted
    if student.is_enrolled:
        raise BadRequestException(detail="Cannot delete an actively enrolled student. Unenroll them first.")
        
    db.delete(student)
    db.commit()
    return None