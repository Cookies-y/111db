import os
from datetime import timedelta

# basedir is the 'backend' directory
basedir = os.path.abspath(os.path.dirname(__file__))

# instance_path will be 'backend/instance'
# This is fine for development if instance folder within backend is acceptable.
# For production, an instance folder outside the app package is often preferred,
# but for SQLite, as long as the path is absolute and writable, it works.
# The default Flask instance_path is os.path.join(app.root_path, 'instance')
# If app.root_path is backend/app, then default instance_path is backend/app/instance.
# The current backend/app/__init__.py already creates backend/instance, so this is consistent.
# We will use the path relative to 'basedir' (backend directory) to ensure it's backend/instance.
instance_folder_path = os.path.join(basedir, 'instance')

# Ensure the instance folder exists when config is loaded
if not os.path.exists(instance_folder_path):
    try:
        os.makedirs(instance_folder_path)
    except OSError as e:
        # Handle potential race condition if another process creates it
        if not os.path.isdir(instance_folder_path):
            raise

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-string-for-dev'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'another-super-secret-jwt-key-for-dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    # Example: How to use the instance_folder_path for other configs if needed
    # MY_CUSTOM_CONFIG_FILE = os.path.join(instance_folder_path, 'custom.cfg')

class DevelopmentConfig(Config):
    DEBUG = True
    PORT = 5001 # Port for development server
    # SQLALCHEMY_DATABASE_URI will use the instance_folder_path defined above
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_folder_path, 'xuetong_dev.sqlite3')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Example: For PostgreSQL (ensure psycopg2-binary is in requirements.txt)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'postgresql://user:password@host:port/dbname'
    # For production SQLite (ensure path is appropriate for your deployment):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_folder_path, 'xuetong_prod.sqlite3')
    # Important: Change SECRET_KEY and JWT_SECRET_KEY in production via environment variables!
    # For example, ensure they are not the default hardcoded strings.
    # if SECRET_KEY == 'a-very-hard-to-guess-string-for-dev':
    #     print("WARNING: Production SECRET_KEY is using default. Set via environment variable.")
    # if JWT_SECRET_KEY == 'another-super-secret-jwt-key-for-dev':
    #     print("WARNING: Production JWT_SECRET_KEY is using default. Set via environment variable.")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_folder_path, 'xuetong_test.sqlite3') # Separate test DB
    # Or use in-memory SQLite for tests: 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5) # Faster expiration for tests
    # Disable CSRF protection in tests if forms were still used and CSRF enabled
    # WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig # Default to development
}
