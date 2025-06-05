import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta
import click # For CLI commands

# Initialize extensions
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

api = Api(
    version='1.0',
    title='XueTong API',
    description='A RESTful API for the XueTong Online Learning Platform (MVP)',
    authorizations=authorizations
)

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_placeholder')

    instance_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "xuetong.sqlite3")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key-placeholder')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    from . import models # Import models to register them with SQLAlchemy

    # Register API namespaces
    from .auth_api import auth_ns
    api.add_namespace(auth_ns, path='/auth')

    from .course_api import course_ns
    api.add_namespace(course_ns, path='/courses')

    from .assignment_api import course_assignments_ns, assignment_ops_ns, submission_ops_ns
    api.add_namespace(course_assignments_ns) # Path: /courses/<int:course_id>/assignments
    api.add_namespace(assignment_ops_ns)     # Path: /assignments
    api.add_namespace(submission_ops_ns)     # Path: /submissions

    from .exam_api import course_exams_ns, exam_ops_ns, exam_result_ops_ns
    api.add_namespace(course_exams_ns)       # Path: /courses/<int:course_id>/exams
    api.add_namespace(exam_ops_ns)           # Path: /exams/<int:exam_id>
    api.add_namespace(exam_result_ops_ns)    # Path: /exam-results

    from .discussion_api import course_discussions_ns, discussion_ops_ns
    api.add_namespace(course_discussions_ns) # Path: /courses/<int:course_id>/discussions
    api.add_namespace(discussion_ops_ns)     # Path: /discussions

    # Placeholder for other future namespaces (e.g., enrollment etc.)

    # --- CLI Commands ---
    @app.cli.command("init-db")
    def init_db_command():
        """Creates or updates the database tables based on models."""
        with app.app_context(): # Ensure app context for db operations
            db.create_all()
        click.echo(click.style("Initialized/Updated the database!", fg='green'))

    @app.cli.command("create-admin")
    @click.option('--username', required=True, help='Admin username')
    @click.option('--email', required=True, help='Admin email address')
    @click.option('--password', required=True, help='Admin password (will be hashed)')
    @click.option('--real_name', required=True, help='Admin real name')
    def create_admin_command(username, email, password, real_name):
        """Creates a new admin user (user_type=3)."""
        # App context is usually available in CLI commands registered this way,
        # but explicit context can be added if issues arise.
        # from .models import User # Already imported via `from . import models`

        # It's better to ensure User is loaded within the app context for DB operations
        with app.app_context():
            if models.User.query.filter_by(email=email).first():
                click.echo(click.style(f'Error: User with email {email} already exists.', fg='red'))
                return
            if models.User.query.filter_by(username=username).first():
                click.echo(click.style(f'Error: User with username {username} already exists.', fg='red'))
                return

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


    # The old create_db_tables function exposed via app.extensions is no longer needed
    # if init-db CLI command is preferred. Keeping it doesn't harm for now.
    def create_db_tables_old_method(): # Renamed to avoid confusion
        with app.app_context():
            db.create_all()
            print("Database tables checked/created (if they didn't exist) via old method.")
    app.extensions['create_db_tables'] = create_db_tables_old_method


    return app
