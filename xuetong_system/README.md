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
    *   Admin-specific endpoints for user and course management.
    *   Endpoints for course, assignment, exam, discussion, and progress management.
*   **Command-Line Interface (CLI) Utilities:**
    *   `flask init-db`: A command to initialize the database, creating all tables based on the defined models.
    *   `flask create-admin`: A command to create an initial administrator user with specified credentials.
*   **Configuration:** Environment-based configurations for development, production, and testing.

## Project Structure

The project is primarily contained within the `xuetong_system/` directory:

*   `backend/`: Contains the Flask application and all related files.
    *   `app/`: The core application package.
        *   `models.py`: Defines all 11 SQLAlchemy database models.
        *   `auth_api.py`, `course_api.py`, `assignment_api.py`, `exam_api.py`, `discussion_api.py`, `progress_api.py`, `admin_api.py`: Define API routes and logic using Flask-RESTx.
        *   `__init__.py`: Initializes the Flask application, extensions (SQLAlchemy, Bcrypt, JWTManager, Flask-RESTx API), and registers API namespaces and CLI commands.
    *   `instance/`: This directory is created by `config.py` if it doesn't exist. SQLite database files (e.g., `xuetong_dev.sqlite3`, `xuetong_prod.sqlite3`) will be stored here.
    *   `venv/`: The Python virtual environment directory (created by the user).
    *   `run.py`: Script to start the Flask development API server using development configuration.
    *   `wsgi.py`: WSGI entry point for production deployment (e.g., with Gunicorn).
    *   `config.py`: Contains configuration classes for different environments.
    *   `requirements.txt`: Lists the Python dependencies for the project.
*   `frontend/`: Contains the Vue.js frontend application.
    *   `src/`: Frontend source code (components, views, stores, router, services).
    *   `dist/`: (Generated after build) Contains optimized static assets for deployment.
    *   `.env.development`, `.env.production`: Environment-specific configurations for the frontend (e.g., API base URL).
    *   `package.json`: Frontend project metadata and dependencies.
    *   `vite.config.js`: Vite build tool configuration.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore (at the root of `xuetong_system/`).
*   `xuetong_system/frontend/.gitignore`: Specific ignores for the frontend project (e.g., `node_modules`, `dist`).
*   `README.md`: This file.

## Setup Instructions

1.  **Clone the Repository:**
    If you have Git, clone the repository. Otherwise, ensure you have the `xuetong_system` directory structure.

2.  **Backend Setup (in `xuetong_system/backend/`):**
    *   Navigate to the backend directory: `cd path/to/xuetong_system/backend/`
    *   Create and activate a Python virtual environment:
        ```bash
        python -m venv venv
        # On Windows: .\venv\Scripts\activate
        # On macOS/Linux: source venv/bin/activate
        ```
    *   Install backend dependencies: `pip install -r requirements.txt`

3.  **Frontend Setup (in `xuetong_system/frontend/`):**
    *   Navigate to the frontend directory: `cd path/to/xuetong_system/frontend/`
    *   Install frontend dependencies: `npm install` (or `yarn install` / `pnpm install`)

## Running the Application (Development)

1.  **Start Backend API Server:**
    *   Ensure you are in `xuetong_system/backend/` with the virtual environment activated.
    *   Set environment variables (e.g., in a `.flaskenv` file or directly):
        ```bash
        export FLASK_APP=run.py
        export FLASK_CONFIG=development
        # Optionally set DEV_DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY if not using defaults from config.py
        ```
    *   Initialize the database (if first time or after model changes): `flask init-db`
    *   Create an admin user (recommended): `flask create-admin --username youradmin --email admin@example.com --password yourpass --real_name "Admin User"`
    *   Run the development server: `python run.py` or `flask run`
    *   The API server will typically run on `http://localhost:5001/`. Swagger UI for API docs will be at `http://localhost:5001/doc/`.

2.  **Start Frontend Development Server:**
    *   Ensure you are in `xuetong_system/frontend/`.
    *   (The `frontend/.env.development` file should set `VITE_API_BASE_URL=http://localhost:5001`.)
    *   Run the Vite development server: `npm run dev`
    *   The frontend will typically be available at `http://localhost:5173` (or another port shown in the console).

## Deployment Preparation

This section outlines key considerations for preparing the application for a production environment.

### Backend (Flask API)

*   **Configuration (`config.py`):**
    *   The `config.py` file manages different configurations (e.g., `DevelopmentConfig`, `ProductionConfig`).
    *   The `FLASK_CONFIG` environment variable (e.g., `export FLASK_CONFIG=production`) is used by `wsgi.py` (for production) and `run.py` (can be set for dev) to select the appropriate configuration class.
*   **Required Environment Variables for Production:**
    *   `FLASK_CONFIG=production`: Ensures production settings are loaded.
    *   `SECRET_KEY`: A strong, unique secret key for Flask session security, CSRF, etc. **Must be changed from default.**
    *   `JWT_SECRET_KEY`: A strong, unique secret key for signing JWTs. **Must be changed from default.**
    *   `DATABASE_URL`: The full database connection string for your production database (e.g., `postgresql://user:password@host:port/dbname`). The default `ProductionConfig` uses `sqlite:///instance/xuetong_prod.sqlite3` if `DATABASE_URL` is not set.
*   **Database Initialization (Production):**
    *   After setting up your production environment and configuration (especially `DATABASE_URL` and `FLASK_CONFIG=production`), run the database initialization command from your `backend` directory (with virtualenv activated):
        ```bash
        flask init-db
        ```
    *   Similarly, create an initial admin user using `flask create-admin ...` if needed for the production database.
*   **Running with Gunicorn (Production WSGI Server):**
    *   The `wsgi.py` file provides the `application` callable for WSGI servers.
    *   Gunicorn is listed in `requirements.txt`.
    *   Example command to run the backend with Gunicorn:
        ```bash
        # Ensure backend virtual environment is active
        # Ensure all production environment variables (FLASK_CONFIG, SECRET_KEY, etc.) are set
        cd /path/to/xuetong_system/backend/
        gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:application
        ```
    *   `--workers 4`: Example number of worker processes (adjust based on your server's CPU cores).
    *   `--bind 0.0.0.0:5000`: Makes Gunicorn listen on port 5000 on all network interfaces. This port is typically proxied by a web server like Nginx.

### Frontend (Vue.js SPA)

*   **API Base URL Configuration:**
    *   The frontend connects to the backend API using a base URL defined by an environment variable.
    *   For development, `frontend/.env.development` sets `VITE_API_BASE_URL=http://localhost:5001` (or your backend dev port).
    *   For production, `frontend/.env.production` should be configured. Examples:
        *   `VITE_API_BASE_URL=/api`: If Nginx (or another reverse proxy) serves the frontend and proxies requests from `/api` on the same domain to the backend API (e.g., Gunicorn on port 5000).
        *   `VITE_API_BASE_URL=https://api.yourdomain.com`: If your API is hosted on a separate subdomain.
*   **Building for Production:**
    *   Navigate to the frontend directory: `cd path/to/xuetong_system/frontend/`
    *   Run the build command: `npm run build`
    *   This generates optimized static assets (HTML, CSS, JavaScript) in the `frontend/dist/` directory. These are the files you will deploy.

### Serving in Production (Conceptual Example with Nginx)

A common production setup involves using a web server like Nginx to serve the static frontend files and act as a reverse proxy for the backend API (Gunicorn).

*   **Nginx Configuration Snippet (Illustrative):**
    ```nginx
    # /etc/nginx/sites-available/your_xuetong_site.conf
    server {
        listen 80; # Or 443 for HTTPS with SSL configuration
        server_name yourdomain.com; # Replace with your actual domain

        # Vue.js frontend static files (from frontend/dist/)
        location / {
            root /var/www/xuetong_system/frontend/dist; # Adjust path to your deployment
            try_files $uri $uri/ /index.html;
            # Add caching headers, security headers, etc.
        }

        # Reverse proxy API requests to the backend Flask/Gunicorn server
        # This path must match the VITE_API_BASE_URL if it's a relative path (e.g., /api)
        location /api/ {
            # If VITE_API_BASE_URL in frontend is just '/',
            # then proxy all non-static locations:
            # location ~ ^/(auth|courses|assignments|exams|discussions|progress|admin)/ { ... }

            proxy_pass http://127.0.0.1:5000; # Gunicorn running on port 5000
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            # Optional: Increase client body size if handling large file uploads via API
            # client_max_body_size 20M;
        }

        # SSL Configuration (Highly Recommended for Production)
        # listen 443 ssl;
        # ssl_certificate /path/to/your/fullchain.pem;
        # ssl_certificate_key /path/to/your/privkey.pem;
        # include /etc/letsencrypt/options-ssl-nginx.conf; # Example for Let's Encrypt
        # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;   # Example for Let's Encrypt
    }
    ```
*   **Important:** This Nginx example is conceptual. A production setup requires careful configuration, including SSL/TLS for HTTPS, security headers, logging, and performance tuning.

## API Endpoints Overview

The API is organized using Flask-RESTx. Interactive API documentation via Swagger UI is typically available at `/doc/` relative to the API root (e.g., `http://localhost:5001/doc/`) when the development server is running.

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

**Course Endpoints (base path: `/courses`):**

*   **`GET /courses/`**: List all available courses.
    *   **Authentication:** Not explicitly required by current implementation for listing, but could be added.
    *   **Success Response (200 OK):** Array of course objects (summary view).
*   **`POST /courses/`**: Create a new course.
    *   **Authentication:** JWT required (Role: Teacher of the course).
    *   **Request Body (JSON):** `course_name`, `description`, `start_date`, `end_date`, `status`, `cover_image` (optional).
    *   **Success Response (201 Created):** Detailed new course object.
*   **`GET /courses/<course_id>`**: Get details of a specific course, including chapters and materials.
    *   **Authentication:** Not explicitly required by current implementation, but could be added (e.g., for enrolled students or public courses).
    *   **Success Response (200 OK):** Detailed course object.

**Assignments & Submissions Endpoints:**

*   **Assignments (JWT required for all):**
    *   **`GET /courses/<course_id>/assignments/`**: List assignments for a specific course.
        *   **Access:** Course Teacher, Enrolled Students.
        *   **Response:** Array of assignment objects.
    *   **`POST /courses/<course_id>/assignments/`**: Create a new assignment for a course.
        *   **Access:** Course Teacher only.
        *   **Request Body (JSON):** `title`, `description` (optional), `deadline` (ISO 8601), `total_score` (optional, default 100).
        *   **Response (201 Created):** Newly created assignment object.
    *   **`GET /assignments/<assignment_id>`**: Get details of a specific assignment.
        *   **Access:** Course Teacher, Enrolled Students (in the course of the assignment).
        *   **Response:** Assignment object.

*   **Submissions (JWT required for all):**
    *   **`POST /assignments/<assignment_id>/submissions`**: Submit to an assignment.
        *   **Access:** Enrolled Student in the course of the assignment.
        *   **Request Body (JSON):** `content`, `attachment_url` (optional).
        *   **Response (201 Created):** Newly created submission object.
        *   **Notes:** Checks for deadlines and prevents duplicate submissions.
    *   **`GET /assignments/<assignment_id>/submissions`**: List all submissions for a specific assignment.
        *   **Access:** Course Teacher only.
        *   **Response:** Array of submission objects.
    *   **`GET /submissions/<submission_id>`**: Get details of a specific submission.
        *   **Access:** Submitting Student or Course Teacher.
        *   **Response:** Submission object.
    *   **`PUT /submissions/<submission_id>/grade`**: Grade a submission.
        *   **Access:** Course Teacher only.
        *   **Request Body (JSON):** `score` (integer), `feedback` (optional string).
        *   **Response (200 OK):** Updated submission object with grade.

**Exams & Exam Results Endpoints (JWT required for all):**

*   **Exams:**
    *   **`GET /courses/<course_id>/exams/`**: List exams for a specific course.
        *   **Access:** Course Teacher, Enrolled Students.
        *   **Response:** Array of exam objects.
    *   **`POST /courses/<course_id>/exams/`**: Create a new exam for a course.
        *   **Access:** Course Teacher only.
        *   **Request Body (JSON):** `exam_name` (string), `description` (optional string), `start_time` (ISO 8601 DateTime), `end_time` (ISO 8601 DateTime), `total_score` (int, default 100), `duration` (int, minutes).
        *   **Response (201 Created):** Newly created exam object.
    *   **`GET /exams/<exam_id>`**: Get details of a specific exam.
        *   **Access:** Course Teacher, Enrolled Students. (Teachers may see all results; students see their own if submitted - details TBC by API implementation).
        *   **Response:** Exam object (potentially with results for teachers).

*   **Exam Submissions/Results:**
    *   **`POST /exams/<exam_id>/submit`**: Student "submits" their exam (e.g., by providing their score for MVP).
        *   **Access:** Enrolled Student in the course of the exam.
        *   **Request Body (JSON):** `score` (integer).
        *   **Response (201 Created):** Newly created exam result object.
        *   **Notes:** Checks if exam is active and if already submitted.
    *   **`GET /exams/<exam_id>/results`**: List all results for a specific exam.
        *   **Access:** Course Teacher only.
        *   **Response:** Array of exam result objects.
    *   **`GET /exam-results/<result_id>`**: Get details of a specific exam result.
        *   **Access:** Submitting Student or Course Teacher.
        *   **Response:** Exam result object.
    *   **`PUT /exam-results/<result_id>`**: Teacher updates/overrides an exam result (e.g., score).
        *   **Access:** Course Teacher only.
        *   **Request Body (JSON):** `score` (integer).
        *   **Response (200 OK):** Updated exam result object.

**Discussions Endpoints (JWT required for all):**

*   **Course Discussions:**
    *   **`GET /courses/<course_id>/discussions/`**: List top-level discussion topics for a course.
        *   **Access:** Course Teacher, Enrolled Students.
        *   **Response:** Array of discussion topic objects (includes `reply_count`).
    *   **`POST /courses/<course_id>/discussions/`**: Create a new discussion topic in a course.
        *   **Access:** Course Teacher, Enrolled Students.
        *   **Request Body (JSON):** `title` (string, required), `content` (string, required).
        *   **Response (201 Created):** Newly created discussion topic object.

*   **Discussion Operations:**
    *   **`GET /discussions/<post_id>/thread`**: Get a specific discussion topic with its direct replies.
        *   **Access:** Course Teacher, Enrolled Students (of the post's course).
        *   **Response:** Discussion topic object with a nested list of direct replies.
    *   **`POST /discussions/<parent_post_id>/replies`**: Post a reply to a specific discussion post.
        *   **Access:** Course Teacher, Enrolled Students (of the parent post's course).
        *   **Request Body (JSON):** `content` (string, required). (Title is ignored/auto-generated for replies).
        *   **Response (201 Created):** Newly created reply object.

**Learning Progress (Simplified) Endpoints (JWT required for all, Student access):**

*   **Material Progress Operations:**
    *   **`POST /materials/<material_id>/progress`**: Student marks/unmarks progress for a specific material.
        *   **Access:** Enrolled Student.
        *   **Request Body (JSON):** `{"is_completed": true/false}`.
        *   **Response (200 OK or 201 Created):** Updated/created progress details for that material.
    *   **`GET /materials/<material_id>/progress`**: Student gets their progress for a specific material.
        *   **Access:** Enrolled Student.
        *   **Response (200 OK):** Progress details for that material (or default if no progress yet).

*   **Course Progress Overview:**
    *   **`GET /courses/<course_id>/my-material-progress`**: Student lists their completion status for all materials in a course.
        *   **Access:** Enrolled Student.
        *   **Response (200 OK):** List of material progress details for the specified course.

**Administrator Endpoints (base path: `/admin`, JWT and Admin Role required for all):**

*   **User Management (Admin):**
    *   **`GET /admin/users`**: List all users in the system.
        *   **Response:** Array of user objects with detailed information.
    *   **`GET /admin/users/<user_id>`**: Get details of a specific user.
        *   **Response:** Detailed user object.

*   **Course Management (Admin):**
    *   **`GET /admin/courses`**: List all courses in the system.
        *   **Response:** Array of course objects (summary view, similar to public course list but potentially with more admin-relevant info if DTOs differ).
    *   **`GET /admin/courses/<course_id>`**: Get details of a specific course, including its chapters, materials, etc.
        *   **Response:** Detailed course object.

*(Note: The base path for all API endpoints (e.g., `/auth`, `/courses`) is relative to where the Flask application is served. If Nginx proxies `/api/` to the Flask app, then frontend's `VITE_API_BASE_URL` would be `/api`, and actual request paths would be `/api/auth/login`, etc. The Swagger UI is available at `/doc/`.)*

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
*   **Production WSGI Server:** Gunicorn

---
This README provides guidance for setting up, running, and interacting with the XueTong System API backend.
