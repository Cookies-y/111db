import os
from app import create_app

# Attempt to load .env file for local development if python-dotenv is used,
# though typically this is handled by Flask's built-in .flaskenv support or explicit calls.
# from dotenv import load_dotenv
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # Assuming .env is in backend/
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)

# Determine the configuration name from environment variable or use default
config_name = os.getenv('FLASK_CONFIG') or 'development'

# Create the Flask app instance using the factory
app = create_app(config_name)

if __name__ == '__main__':
    # For development, it's useful to know which config is loaded.
    # The app context is needed to access app.config if it's not already available.
    # However, app.config is available directly on the app object after creation.
    print(f"Starting XueTong API with '{config_name}' configuration...")
    print(f"  DEBUG mode: {app.config.get('DEBUG')}")
    print(f"  Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # Note: Database initialization is now handled by 'flask init-db' CLI command.
    # It's recommended to run 'flask init-db' once before starting the server for the first time
    # or after model changes.

    # Get host and port from app configuration, with defaults
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5001) # Default to 5001 if not in config

    app.run(debug=app.config.get('DEBUG'), host=host, port=port)
