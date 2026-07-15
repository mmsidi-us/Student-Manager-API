# app/routers/students.py
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.schemas.students import StudentResponse, StudentCreate
from app.models.students import Student
from app.utils.exceptions import NotFoundException, AppException
from app.models.users import User
from app.database import get_db
from app.utils.security import get_current_user

router = APIRouter()

# --- 1. Get Student by ID (Documenting 404) ---
@router.get(
    "/{id}", 
    response_model=StudentResponse,
    summary="Retrieve a student by ID",
    responses={
        404: {
            "description": "Student not found in the database",
            "content": {"application/json": {"example": {"detail": "Student with ID 1 not found"}}}
        }
    }
)
def get_student(id: int, db: Session = Depends(get_db)):
    """
    Search for a single student and return their complete academic profile.

    ### Required Path Parameters:
    * **id** (integer): The unique identifier of the student.

    ### Response Scenarios:
    * **200 OK**: Successfully matched and returned student details.
    * **404 Not Found**: No student found matches the provided ID.
    """
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise NotFoundException(resource="Student", resource_id=id)
    return student


# --- 2. Create Student (Documenting 401 & 422) ---
@router.post(
    "/", 
    response_model=StudentResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student record",
    responses={
        401: {
            "description": "Authentication credentials missing or invalid",
            "content": {"application/json": {"example": {"detail": "Not authenticated"}}}
        },
        422: {
            "description": "Validation error (invalid input payload bounds)",
            "content": {"application/json": {"example": {"detail": "Validation Error"}}}
        }
    }
)
def create_student(
    student: StudentCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Insert a new student record. Requires a valid authorization token.

    ### Data Constraints:
    * **name**: Required string.
    * **email**: Must be a unique, valid email.
    * **grade_level**: Must be an integer between **1** and **12**.
    * **gpa**: Must be a float value between **0.0** and **4.0**.

    ### Authentication:
    * Requires authorization header: `Authorization: Bearer <JWT_TOKEN>`
    """
    # Logic to create student...
    pass


# --- 3. Delete Student (Documenting 400 & 404) ---
@router.delete(
    "/{id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student record permanently",
    responses={
        400: {
            "description": "Business logic constraint violation",
            "content": {"application/json": {"example": {"detail": "Cannot delete an actively enrolled student. Unenroll them first."}}}
        },
        404: {
            "description": "Target student record not found",
            "content": {"application/json": {"example": {"detail": "Student with ID 1 not found"}}}
        }
    }
)
def delete_student(
    id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Permanently delete a student record from the database.

    ### Business Logic Guardrails:
    * You **cannot** delete a student who is actively enrolled (`is_enrolled = True`).
    * If active, the system returns a **400 Bad Request** error forcing you to unenroll them first.
    """
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise NotFoundException(resource="Student", resource_id=id)
    
    if student.is_enrolled:
        raise AppException(detail="Cannot delete an actively enrolled student. Unenroll them first.", status_code=400)
    
    db.delete(student)
    db.commit()
    return


# --- 4. List Students ---
@router.get(
    "/", 
    response_model=List[StudentResponse], 
    summary="List all registered students"
)
def list_students(db: Session = Depends(get_db)):
    """Fetch and return an array of all student records stored in the database."""
    return db.query(Student).all()