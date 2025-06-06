import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta
import click

# Import the configuration dictionary
from ..config import config # `config.py` is in parent directory `backend/`

# Initialize extensions (globally, to be initialized with app in create_app)
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

authorizations = {
    'jsonWebToken': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

# Global Api object. Namespaces will be added in create_app, then api initialized with app.
api = Api(
    version='1.0',
    title='XueTong API',
    description='A RESTful API for the XueTong Online Learning Platform (MVP)',
    authorizations=authorizations,
    doc='/doc/' # Optional: Serve Swagger UI at /doc/ instead of root
)

def create_app(config_name='default'): # Add config_name parameter
    app = Flask(__name__) # Flask's default instance_path is fine if SQLALCHEMY_DATABASE_URI is absolute

    # Load configuration from config.py
    app.config.from_object(config[config_name])

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    # Note: api.init_app(app) will be called after namespaces are added to the api object

    from . import models # Import models to register them with SQLAlchemy

    # Register API namespaces to the global 'api' object
    from .auth_api import auth_ns
    api.add_namespace(auth_ns, path='/auth')

    from .course_api import course_ns
    api.add_namespace(course_ns, path='/courses')

    from .assignment_api import course_assignments_ns, assignment_ops_ns, submission_ops_ns
    api.add_namespace(course_assignments_ns)
    api.add_namespace(assignment_ops_ns)
    api.add_namespace(submission_ops_ns)

    from .exam_api import course_exams_ns, exam_ops_ns, exam_result_ops_ns
    api.add_namespace(course_exams_ns)
    api.add_namespace(exam_ops_ns)
    api.add_namespace(exam_result_ops_ns)

    from .discussion_api import course_discussions_ns, discussion_ops_ns
    api.add_namespace(course_discussions_ns)
    api.add_namespace(discussion_ops_ns)

    from .progress_api import material_progress_ns, course_progress_ns
    api.add_namespace(material_progress_ns)
    api.add_namespace(course_progress_ns)

    from .admin_api import admin_ns
    api.add_namespace(admin_ns)

    # Now that all namespaces are added to the global 'api' object, initialize it with the app
    api.init_app(app)


    # --- CLI Commands ---
    @app.cli.command("init-db")
    def init_db_command():
        """Creates or updates the database tables based on models."""
        with app.app_context():
            db.create_all()
        click.echo(click.style("Initialized/Updated the database!", fg='green'))

    @app.cli.command("create-admin")
    @click.option('--username', required=True, help='Admin username')
    @click.option('--email', required=True, help='Admin email address')
    @click.option('--password', required=True, help='Admin password (will be hashed)')
    @click.option('--real_name', required=True, help='Admin real name')
    def create_admin_command(username, email, password, real_name):
        """Creates a new admin user (user_type=3)."""
        with app.app_context():
            if models.User.query.filter_by(email=email).first():
                click.echo(click.style(f'Error: User with email {email} already exists.', fg='red'))
                return
            if models.User.query.filter_by(username=username).first():
                click.echo(click.style(f'Error: User with username {username} already exists.', fg='red'))
                return

            # Use bcrypt from the initialized extension
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            admin_user = models.User(
                username=username,
                email=email,
                password_hash=hashed_password,
                real_name=real_name,
                user_type=3  # 3 for admin
            )
            db.session.add(admin_user)
            try:
                db.session.commit()
                click.echo(click.style(f'Admin user {username} created successfully with email {email}.', fg='green'))
            except Exception as e:
                db.session.rollback()
                click.echo(click.style(f'Error creating admin: {str(e)}', fg='red'))
                app.logger.error(f"Error creating admin: {e}")

    # Removed the old create_db_tables function exposed via app.extensions,
    # as init-db CLI command is the standard way now.

    return app
