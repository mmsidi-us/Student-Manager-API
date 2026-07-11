# 🎓 Student Manager API

A persistent, structured RESTful API for managing student records, built using **FastAPI**, **SQLAlchemy (ORM)**, and **Pydantic v2**. This project features full CRUD capabilities, dynamic search filtering, strict data validation (including email formats), and automated database integration with **SQLite**.

---

## 🚀 Features

* **Full CRUD Operations**: Create, read, update (PUT/PATCH), and delete student profiles.
* **Persistent Storage**: Utilizes SQLite to ensure student data is securely saved.
* **Partial Updates (PATCH)**: Update only specific fields without modifying the whole record.
* **Dynamic Search & Filtering**: Filter students dynamically by `name`, `email`, or `grade_level` via query parameters.
* **Data Validation**: Strict type checking and value boundaries (e.g., GPA between `0.0` and `4.0`, Grade Level between `1` and `12`).
* **Robust Error Handling**: Prevents database duplication using `IntegrityError` handling for unique email addresses.

---

## 🛠️ Project Structure

```text
Student-Manager-API/
├── app/
│   ├── models/          # SQLAlchemy Database Models (Schema definition)
│   ├── schemas/         # Pydantic Schemas (Data validation & Serialization)
│   ├── routers/         # Endpoint Route Handlers (Logic layers)
│   ├── database.py      # Database Connection & Session Control
│   ├── config.py        # Settings Management via Pydantic Settings
│   └── main.py          # Application Entrypoint
├── .gitignore           # Ignored files (venv, local DB, cache)
└── requirements.txt     # Python Project Dependencies
