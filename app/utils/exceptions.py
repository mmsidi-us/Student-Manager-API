# app/utils/exceptions.py

class AppException(Exception):
    """Base exception for our application."""
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code

class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            detail=f"{resource} with id {resource_id} not found",
            status_code=404
        )

class DuplicateException(AppException):
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            detail=f"{resource} with {field} '{value}' already exists",
            status_code=409
        )

class ForbiddenException(AppException):
    def __init__(self, detail: str = "You don't have permission to perform this action"):
        super().__init__(detail=detail, status_code=403)

# Add this inside app/utils/exceptions.py
class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail=detail, status_code=400)