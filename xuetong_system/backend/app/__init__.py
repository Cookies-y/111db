import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'dev_secret_key_for_xuetong_system' # Replace with a real secret key in production
    # Construct the absolute path for the SQLite database
    instance_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "xuetong.sqlite3")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Define where to redirect for login

    # User loader for Flask-Login
    from .models import User # Import here to avoid circular dependency
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import blueprints
    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .main_routes import main_bp
    app.register_blueprint(main_bp) # No URL prefix for main routes


    # Function to create database tables
    def create_db_tables():
        with app.app_context():
            from .models import User, Course # Ensure models are imported within context
            db.create_all()
            print("Database tables created (if they didn't exist).")

    # You might want to call create_db_tables() conditionally,
    # e.g., via a CLI command or only if the db file doesn't exist.
    # For now, it's a callable function.
    app.extensions['create_db_tables'] = create_db_tables


    return app
