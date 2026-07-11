# app/routers/books.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from app.database import get_db
from app.models.students import Student
from app.schemas.students import StudentCreate, StudentUpdate, StudentPatch, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])

def get_student_or_404(db: Session, student_id: int) -> Student:
    """Helper: fetch a student or raise 404."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student

# ── CREATE ──
@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student."""
    db_student = Student(**student.model_dump())
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A student with this email already exists")
    return db_student

# ── READ (many) ──
@router.get("", response_model=List[StudentResponse])
def list_students(
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    grade_level: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """List students with optional filters."""
    query = db.query(Student)
    if name:
        query = query.filter(Student.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Student.email.ilike(f"%{email}%"))
    if grade_level is not None:
        query = query.filter(Student.grade_level == grade_level)
    return query.all()

# ── READ (one) ──
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get a specific student by ID."""
    return get_student_or_404(db, student_id)

# ── UPDATE (PUT) ──
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)):
    """Fully replace a student's data."""
    db_student = get_student_or_404(db, student_id)
    for field, value in student_data.model_dump().items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    return db_student

# ── UPDATE (PATCH) ──
@router.patch("/{student_id}", response_model=StudentResponse)
def patch_student(student_id: int, student_data: StudentPatch, db: Session = Depends(get_db)):
    """Partially update a student."""
    db_student = get_student_or_404(db, student_id)
    update_data = student_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    return db_student

# ── DELETE ──
@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student."""
    db_student = get_student_or_404(db, student_id)
    db.delete(db_student)
    db.commit()
    return None