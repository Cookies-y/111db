# XueTong System (MVP)

## Overview

XueTong System is a Minimum Viable Product (MVP) for a simple online learning platform. It allows users to register with distinct roles (Student or Teacher), log in, and interact with course content. Teachers can create courses, and all authenticated users can view a list of available courses. This project serves as a basic demonstration of web application development using Flask.

## Features Implemented (MVP)

*   **User Authentication:**
    *   User registration with 'Student' and 'Teacher' roles.
    *   Secure user login and logout functionality.
    *   Password hashing for security (using Werkzeug).
*   **Course Management:**
    *   Teachers can create new courses, providing a course name and description.
    *   All authenticated users can view a list of available courses, including details like course name, description, teacher, and creation date.
*   **Role-Based Access Control (RBAC):**
    *   Basic RBAC is implemented, e.g., only users with the 'Teacher' role can access the course creation page and functionality.
*   **Frontend:**
    *   User interface implemented using Flask's Jinja2 templating engine.
    *   Basic styling provided by CSS.
    *   Flashed messages for user feedback (e.g., success on registration, login errors).

## Project Structure

The project is primarily contained within the `xuetong_system/` directory:

*   `backend/`: Contains the Flask application and all related files.
    *   `app/`: The core application package.
        *   `models.py`: Defines database models (User, Course) using Flask-SQLAlchemy.
        *   `forms.py`: Defines forms for registration, login, and course creation using Flask-WTF.
        *   `auth_routes.py`: Handles authentication routes (login, register, logout).
        *   `main_routes.py`: Handles main application routes (course listing, course creation, index).
        *   `__init__.py`: Initializes the Flask application, extensions, and blueprints.
        *   `templates/`: Contains Jinja2 HTML templates.
            *   `auth/`: Templates for authentication pages.
            *   `main/`: Templates for main application pages.
            *   `base.html`: Base layout template.
        *   `static/`: Contains static files (currently only CSS).
            *   `css/style.css`: Main stylesheet.
    *   `instance/`: This directory is created automatically. The SQLite database file (`xuetong.sqlite3`) will be stored here.
    *   `venv/`: The Python virtual environment directory (should be created by the user).
    *   `run.py`: A Python script used to start the Flask development server.
    *   `requirements.txt`: Lists the Python dependencies for the project.
*   `frontend/`: This directory was initially planned for separate frontend development (e.g., with a JavaScript framework). However, for this MVP, the frontend is server-side rendered and integrated within the `backend/app/templates/` and `backend/app/static/` directories.
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

## Running the Application

1.  **Ensure Location and Environment:**
    Make sure you are still in the `xuetong_system/backend/` directory and that your virtual environment (`venv`) is activated.

2.  **Run the Development Server:**
    Execute the `run.py` script:
    ```bash
    python run.py
    ```

3.  **Access the Application:**
    The application will typically be available in your web browser at:
    `http://127.0.0.1:5001/`
    (The port `5001` is specified in `run.py`; if you change it there, use the new port).

4.  **Database Creation:**
    On the first run, if the database file does not exist, it will be automatically created at `xuetong_system/backend/instance/xuetong.sqlite3`.

## Technology Stack (MVP)

*   **Backend:** Python, Flask framework
*   **Database:** SQLite (via Flask-SQLAlchemy)
*   **Templating:** Jinja2 (comes with Flask)
*   **Forms:** Flask-WTF (integrates WTForms with Flask)
*   **Authentication:** Flask-Login for session management
*   **Password Hashing:** Werkzeug (a Flask dependency)
*   **Frontend Styling:** Basic CSS

---
This README provides a good starting point for understanding and running the XueTong System MVP.
