# Infosys_FastAPI_Assignment

# User Management API

A RESTful API developed using **Python and FastAPI** to manage user registration, login, authentication, and profile operations.

## Project Overview

The User Management API provides a secure way to manage user accounts. Users can register, log in, and access protected resources using JWT (JSON Web Token) authentication.

The application uses SQLite for database management and SQLAlchemy ORM for database operations.

## Technologies Used

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- JWT (JSON Web Token)
- Password Hashing
- Uvicorn

## Features

- User Registration
- User Login
- Secure Password Hashing
- JWT Token Generation
- Token-based Authentication
- Protected API Endpoints
- User Profile Management
- SQLite Database Integration
- Input Validation using Pydantic

## Project Structure

```text
Infosys_FastAPI_Assignment/
│
├── main.py
├── requirements.txt
├── app/
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── other application files
│
├── .gitignore
└── README.md
```

*Note: This is an illustrative structure. Your actual project may contain additional Python files and folders.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Deepthi0301/Infosys_FastAPI_Assignment
```

### 2. Navigate to the Project Folder

```bash
cd Infosys_FastAPI_Assignment
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
uvicorn main:app --reload
```

The application runs at:

http://127.0.0.1:8000

## API Documentation

FastAPI provides interactive API documentation using Swagger UI.

Open the following URL after starting the application:

http://127.0.0.1:8000/docs

You can explore and test the API endpoints directly through Swagger UI.

## Authentication and Security

- Passwords are hashed before being stored in the database.
- JWT tokens are generated during successful login.
- Protected endpoints require valid authentication tokens.
- Pydantic schemas validate incoming request data.

## Database

The application uses **SQLite** to store user information and **SQLAlchemy ORM** to perform database operations.

## Testing

The application can be tested using Swagger UI.

Main functionalities to test:

- User registration
- User login
- JWT token generation
- Accessing protected endpoints
- User profile management
- Invalid input and authentication handling

## Future Enhancements

- Password reset functionality
- Email verification
- User role management
- Frontend integration
- Additional security features

## Conclusion

This project demonstrates the development of a RESTful API using FastAPI, secure user authentication using JWT, password hashing, and database management using SQLite and SQLAlchemy.

---

**Developed as part of Infosys Springboard Internship – Assignment 1.**
