"""
Database setup script for authentication module
Run this script to create the authentication-related database tables
"""
from forum import create_app
from forum.models import db
from forum.auth.auth_models import AuthToken, LoginAttempt

def setup_auth_tables():
    """Create authentication tables if they don't exist"""
    app = create_app()
    
    with app.app_context():
        # Create all tables (including auth tables)
        db.create_all()
        print("Authentication tables created successfully!")
        
        # Print table information
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("\nExisting tables:")
        for table in tables:
            print(f"  - {table}")
        
        print("\nAuth module setup complete!")

if __name__ == "__main__":
    setup_auth_tables()
