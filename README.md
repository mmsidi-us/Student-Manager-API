# 🎓 Student Manager API

A persistent, structured RESTful API for managing student records, built using **FastAPI**, **SQLAlchemy (ORM)**, and **Pydantic v2**. This project features full CRUD capabilities, dynamic search filtering, strict data validation, and robust **JWT Authentication** to secure sensitive endpoints.

---

## 🚀 Features

* **Full CRUD Operations**: Create, read, update (PUT/PATCH), and delete student profiles.
* **Persistent Storage**: Utilizes SQLite to ensure student data is securely saved.
* **JWT Authentication**: Secure user management with signup (`/auth/register`), login (`/auth/login`), and token-based access control.
* **Granular Route Protection**:
  * **Public**: Anyone can browse the student directory (`GET /students`).
  * **Protected**: Only authenticated users with a valid JWT token can create, patch, or delete student profiles.
* **Data Validation**: Strict type checking and value boundaries (e.g., GPA between `0.0` and `4.0`, Grade Level between `1` and `12`).
* **Robust Error Handling**: Unified global exception overrides returning standardized JSON responses for 404, 409, 422, and 500 errors.

---

## 🛠 Project Structure

```text
Student-Manager-API/
│
├── app/
│   ├── models/          # SQLAlchemy Database Models (Student, User)
│   ├── schemas/         # Pydantic Schemas (Data validation & Serialization)
│   ├── routers/         # Endpoint Route Handlers (students, auth)
│   ├── utils/           # Utilities (Security/JWT handlers, Custom Exceptions)
│   ├── database.py      # Database Connection & Session Control
│   ├── config.py        # Settings Management via Pydantic Settings
│   └── main.py          # Application Entrypoint & Global Exception Handlers
│
├── .gitignore           # Ignored files (venv, local DB, cache)
└── requirements.txt     # Python Project Dependencies
