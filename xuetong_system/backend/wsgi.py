import os
from app import create_app

# The FLASK_CONFIG environment variable determines which configuration to load.
# For production, this should typically be set to 'production'.
# Gunicorn, uWSGI, etc., will be configured to point to this 'application' callable.
config_name = os.getenv('FLASK_CONFIG') or 'production'
application = create_app(config_name)

# Optional: Add any production-specific startup logic here if absolutely necessary,
# though most configurations should be handled within Config classes or the app factory.

# Example: If you want to log the configuration being used in production (be cautious with log verbosity)
# with application.app_context():
#     print(f"WSGI application created with '{config_name}' configuration.")
#     print(f"  DEBUG mode: {application.config.get('DEBUG')}")
#     print(f"  Database URI: {application.config.get('SQLALCHEMY_DATABASE_URI')}")

# The following is usually not needed for WSGI servers like Gunicorn,
# as they just need the 'application' callable.
# if __name__ == "__main__":
#    # This would only run if you execute `python wsgi.py` directly,
#    # which is not the typical way to run a WSGI app in production.
#    # For production, use a WSGI server like Gunicorn: gunicorn wsgi:application
#    print(f"Starting application directly via wsgi.py (not recommended for production)...")
#    host = application.config.get('HOST', '0.0.0.0')
#    port = application.config.get('PORT', 5000) # Gunicorn usually handles port
#    application.run(host=host, port=port)
