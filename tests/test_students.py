# tests/test_students.py
import pytest

# ==============================================================================
# 🔒 1. Authentication & Security Tests
# ==============================================================================

def test_protected_endpoints_return_401_without_token(client):
    """Ensures protected resource routers deny access with a 401 status without token."""
    # Attempting to fetch students anonymously
    response = client.get("/students/")
    assert response.status_code == 401
    
    # Attempting to create a student anonymously
    payload = {"name": "Anonymous", "email": "anon@example.com", "grade_level": 5, "gpa": 3.0}
    response = client.post("/students/", json=payload)
    assert response.status_code == 401


# ==============================================================================
# ➕ 2. Create Student (POST) Tests
# ==============================================================================

def test_create_student_success(client, auth_headers):
    """Tests that a student is successfully created with correct attributes."""
    payload = {
        "name": "Sidi Mohamed",
        "email": "sidi@example.com",
        "grade_level": 11,
        "gpa": 3.95,
        "is_enrolled": True
    }
    response = client.post("/students/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert "id" in data

def test_create_student_invalid_gpa_bounds(client, auth_headers):
    """Validates that a 422 error is returned when GPA exceeds max boundary (4.0)."""
    payload = {
        "name": "Invalid GPA Student",
        "email": "badgpa@example.com",
        "grade_level": 10,
        "gpa": 4.5,  # GPA upper bound constraint is 4.0
        "is_enrolled": True
    }
    response = client.post("/students/", json=payload, headers=auth_headers)
    assert response.status_code == 422

def test_create_student_invalid_grade_level(client, auth_headers):
    """Validates that a 422 error is returned when grade_level exceeds max bounds."""
    payload = {
        "name": "Bad Grade Student",
        "email": "badgrade@example.com",
        "grade_level": 15,  # Grade level must be between 1 and 12
        "gpa": 3.0,
        "is_enrolled": True
    }
    response = client.post("/students/", json=payload, headers=auth_headers)
    assert response.status_code == 422


# ==============================================================================
# 📂 3. Read Student (GET) Tests
# ==============================================================================

def test_list_students_empty(client, auth_headers):
    """Tests that an empty list is returned when no database entries exist."""
    response = client.get("/students/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_list_students_with_data(client, auth_headers, sample_student):
    """Tests listing all students when database records exist."""
    response = client.get("/students/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == sample_student.email

def test_get_student_by_id_found(client, auth_headers, sample_student):
    """Retrieves a single student record using their valid ID."""
    response = client.get(f"/students/{sample_student.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == sample_student.name

def test_get_student_by_id_not_found(client, auth_headers):
    """Asserts that a 404 is thrown when requesting a non-existent student ID."""
    response = client.get("/students/9999", headers=auth_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ==============================================================================
# ✏️ 4. Update Student (PUT) Tests
# ==============================================================================

def test_update_student_success(client, auth_headers, sample_student):
    """Verifies that an existing student's attributes can be successfully updated."""
    payload = {
        "name": "Ahmed Updated",
        "email": "ahmed_new@example.com",
        "grade_level": 12,
        "gpa": 3.9,
        "is_enrolled": False
    }
    response = client.put(f"/students/{sample_student.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ahmed Updated"
    assert data["email"] == "ahmed_new@example.com"
    assert data["grade_level"] == 12

def test_update_student_not_found(client, auth_headers):
    """Ensures updating a non-existent ID results in a 404 error."""
    payload = {
        "name": "Ghost",
        "email": "ghost@example.com",
        "grade_level": 11,
        "gpa": 3.5,
        "is_enrolled": True
    }
    response = client.put("/students/9999", json=payload, headers=auth_headers)
    assert response.status_code == 404


# ==============================================================================
# 🗑️ 5. Delete Student (DELETE) Tests
# ==============================================================================

# tests/test_students.py

def test_delete_student_success(client, auth_headers, sample_student):
    """Confirms successful student record deletion and subsequent retrieval failure."""
    # 1. Ensure the student is NOT enrolled so they can be deleted
    sample_student.is_enrolled = False
    
    # (If your database session isn't automatically committed/flushed, 
    # you can unenroll them via an API PUT request first, or update the DB directly)

    response = client.delete(f"/students/{sample_student.id}", headers=auth_headers)
    
    # 2. Assert status code is 204 No Content (matching your router configuration)
    assert response.status_code == 204
    
    # 3. Verify they are gone
    get_response = client.get(f"/students/{sample_student.id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_student_not_found(client, auth_headers):
    """Asserts trying to delete an invalid ID returns a 404 error."""
    response = client.delete("/students/9999", headers=auth_headers)
    assert response.status_code == 404