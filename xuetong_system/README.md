# XueTong System - API Backend (Phase 1)

## Overview

This is the backend API for the XueTong System, an online learning platform. This phase of the project focuses on establishing a robust, pure API backend designed to be consumed by a separate frontend application (e.g., built with Vue.js, React, or Angular). The current system provides core functionalities including a detailed database schema, user authentication (registration and JWT-based login), and initial API endpoints.

## Features Implemented (Backend - Phase 1)

*   **Comprehensive Database Schema:**
    *   Includes 11 models representing Users, Courses, Chapters, Materials, Assignments, Submissions, Exams, Exam Results, Discussions, Enrollments, and Progress.
*   **User Management & Authentication:**
    *   User registration API (`/auth/register`) allowing creation of 'student' and 'teacher' accounts.
    *   User login API (`/auth/login`) which, upon successful authentication, returns a JSON Web Token (JWT).
    *   Secure password hashing using Bcrypt.
    *   JWT-based authentication for securing API endpoints.
*   **API Endpoints:**
    *   A protected test endpoint (`/auth/protected`) to verify JWT authentication.
*   **Command-Line Interface (CLI) Utilities:**
    *   `flask init-db`: A command to initialize the database, creating all tables based on the defined models.
    *   `flask create-admin`: A command to create an initial administrator user with specified credentials.

## Project Structure

The project is primarily contained within the `xuetong_system/` directory:

*   `backend/`: Contains the Flask application and all related files.
    *   `app/`: The core application package.
        *   `models.py`: Defines all 11 SQLAlchemy database models.
        *   `auth_api.py`: Defines API routes and logic for authentication (registration, login) and user-related operations using Flask-RESTx.
        *   `__init__.py`: Initializes the Flask application, extensions (SQLAlchemy, Bcrypt, JWTManager, Flask-RESTx API), and registers API namespaces and CLI commands.
        *   *(Note: `templates/`, `static/`, and `forms.py` have been removed as part of the shift to a pure API backend.)*
    *   `instance/`: This directory is created automatically. The SQLite database file (`xuetong.sqlite3`) will be stored here.
    *   `venv/`: The Python virtual environment directory (should be created by the user).
    *   `run.py`: A Python script used to start the Flask development API server.
    *   `requirements.txt`: Lists the Python dependencies for the project.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
*   `README.md`: This file.

## Setup Instructions

1.  **Clone the Repository:**
    If you have Git, clone the repository. Otherwise, ensure you have the `xuetong_system` directory structure.

2.  **Navigate to Backend Directory:**
    Open your terminal and navigate into the backend directory:
    ```bash
    cd path/to/xuetong_system/backend/
    ```

3.  **Create and Activate Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    # Create the virtual environment
    python -m venv venv
    ```
    Activate the virtual environment:
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    Your terminal prompt should change to indicate that the virtual environment is active.

4.  **Install Dependencies:**
    With the virtual environment activated, install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    This will install Flask, Flask-RESTx, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt, and other necessary packages.

## Running the API Application

1.  **Ensure Location and Environment:**
    Make sure you are still in the `xuetong_system/backend/` directory and that your virtual environment (`venv`) is activated.

2.  **Set Flask App Environment Variable (Optional but Recommended):**
    For Flask CLI commands to work smoothly, you might need to set the `FLASK_APP` environment variable.
    *   On macOS/Linux:
        ```bash
        export FLASK_APP=run.py
        ```
    *   On Windows (cmd.exe):
        ```bash
        set FLASK_APP=run.py
        ```
    *   On Windows (PowerShell):
        ```bash
        $env:FLASK_APP = "run.py"
        ```
    Alternatively, you can invoke Flask directly: `python -m flask <command>`.

3.  **Initialize the Database:**
    Before running the application for the first time, or if you've made changes to the models, initialize the database:
    ```bash
    flask init-db
    ```
    This command creates all necessary tables in the `instance/xuetong.sqlite3` database file.

4.  **Create an Admin User (Recommended):**
    Use the CLI command to create an initial admin user:
    ```bash
    flask create-admin --username youradmin --email admin@example.com --password yoursecurepassword --real_name "Admin User"
    ```
    Replace placeholders with your desired admin credentials.

5.  **Run the Development API Server:**
    Execute the `run.py` script:
    ```bash
    python run.py
    ```
    The API server will start, typically available at `http://127.0.0.1:5001/`. This backend serves API endpoints; there is no browser UI directly served by this application.

## API Endpoints Overview

The API is organized using Flask-RESTx. Interactive API documentation via Swagger UI is typically available at the root URL of the API (e.g., `http://127.0.0.1:5001/`) when the development server is running.

You can also test endpoints using tools like Postman or `curl`.

**Key Authentication Endpoints (base path: `/auth`):**

*   **`POST /auth/register`**: Register a new user.
    *   **Request Body (JSON):**
        ```json
        {
            "username": "newstudent",
            "password": "password123",
            "real_name": "New Student",
            "email": "newstudent@example.com",
            "user_type": "student"
        }
        ```
    *   **Success Response (201 Created):** User details (excluding password).
    *   **Error Responses:** 400 (validation error), 409 (user already exists).

*   **`POST /auth/login`**: Log in an existing user.
    *   **Request Body (JSON):**
        ```json
        {
            "email": "newstudent@example.com",
            "password": "password123"
        }
        ```
    *   **Success Response (200 OK):**
        ```json
        {
            "access_token": "<JWT_TOKEN>"
        }
        ```
    *   **Error Responses:** 401 (invalid credentials).

*   **`GET /auth/protected`**: A sample endpoint to test JWT authentication.
    *   **Headers:**
        *   `Authorization: Bearer <JWT_TOKEN>`
    *   **Success Response (200 OK):**
        ```json
        {
            "message": "Hello User ID <id>! This is a protected endpoint.",
            "current_user_id": <id>
        }
        ```
    *   **Error Responses:** 401 (missing or invalid token).

*(Note: If a global API prefix like `/api` is configured in Flask-RESTx, these paths would be `/api/auth/register`, etc.)*

## Technology Stack

*   **Backend Framework:** Python, Flask
*   **API Development:** Flask-RESTx
*   **Database ORM:** Flask-SQLAlchemy
*   **Database:** SQLite (for development/MVP)
*   **Authentication:** JWT (JSON Web Tokens) via Flask-JWT-Extended and PyJWT
*   **Password Hashing:** Flask-Bcrypt
*   **Data Validation:** `email-validator` (for email format validation in models/logic, if used beyond WTForms)
*   **CLI:** Click (Flask's default CLI library)
*   **WSGI Server (Flask dev server):** Werkzeug

---
This README provides guidance for setting up, running, and interacting with the XueTong System API backend.
