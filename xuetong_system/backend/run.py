import os
from app import create_app # app is the package (directory) here

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Construct the absolute path for the SQLite database from app config
        # Ensure this matches the URI in __init__.py
        # SQLALCHEMY_DATABASE_URI is 'sqlite:///../instance/xuetong.sqlite3'
        # So, db_file_path should be 'instance/xuetong.sqlite3' relative to 'backend' directory

        # Correctly derive the db_path from the app's configuration
        # The URI is like 'sqlite:///path/to/database.db'
        # We need the 'path/to/database.db' part.
        uri_parts = app.config['SQLALCHEMY_DATABASE_URI'].split('sqlite:///', 1)
        if len(uri_parts) < 2:
            raise ValueError("SQLALCHEMY_DATABASE_URI is not in the expected format.")

        # The path in SQLALCHEMY_DATABASE_URI is already absolute or relative to the app root as defined in __init__.py
        # In __init__.py, we have:
        # instance_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'instance')
        # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "xuetong.sqlite3")}'
        # This means the path in SQLALCHEMY_DATABASE_URI is absolute.
        db_file_path = uri_parts[1]

        if not os.path.exists(db_file_path):
            print(f"Database file not found at {db_file_path}. Attempting to create tables...")
            create_db_func = app.extensions.get('create_db_tables')
            if create_db_func:
                create_db_func() # This function already calls db.create_all()
                print(f"Database tables created. Database file should now exist at {db_file_path}")
            else:
                print("Error: Could not find the create_db_tables function in app.extensions.")
        else:
            print(f"Database file already exists at {db_file_path}.")

    app.run(debug=True, host='0.0.0.0', port=5001) # Changed port to avoid potential conflicts
