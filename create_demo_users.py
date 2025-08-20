"""
Demo script showing how to use the authentication module
Run this after setup_auth.py to create demo users
"""
from forum import create_app
from forum.models import db, User
from forum.auth.auth_models import AuthUser

def create_demo_users():
    """Create demo users for testing"""
    app = create_app()
    
    with app.app_context():
        # Check if users already exist
        if User.query.count() > 0:
            print("Users already exist in database. Skipping demo user creation.")
            print(f"Current user count: {User.query.count()}")
            return
        
        demo_users = [
            {
                'email': 'admin@circuscircus.com',
                'username': 'admin',
                'password': 'admin123!'
            },
            {
                'email': 'user1@example.com',
                'username': 'testuser1',
                'password': 'password123!'
            },
            {
                'email': 'user2@example.com',
                'username': 'testuser2',
                'password': 'mypassword456!'
            }
        ]
        
        created_users = []
        
        for user_data in demo_users:
            try:
                user = AuthUser.create_user(
                    user_data['email'],
                    user_data['username'],
                    user_data['password']
                )
                
                if user:
                    db.session.add(user)
                    created_users.append(user)
                    print(f"Created user: {user.username} ({'Admin' if user.admin else 'Regular user'})")
                else:
                    print(f"Failed to create user: {user_data['username']}")
            
            except Exception as e:
                print(f"Error creating user {user_data['username']}: {str(e)}")
                db.session.rollback()
        
        if created_users:
            try:
                db.session.commit()
                print(f"\nSuccessfully created {len(created_users)} demo users!")
                print("\nDemo Login Credentials:")
                print("Admin user: admin / admin123!")
                print("Regular user 1: testuser1 / password123!")
                print("Regular user 2: testuser2 / mypassword456!")
                print("\nNote: All passwords follow the 6-40 character requirement with alphanumeric + @#&%! characters")
            except Exception as e:
                print(f"Error committing users to database: {str(e)}")
                db.session.rollback()
        else:
            print("No users were created.")

if __name__ == "__main__":
    create_demo_users()
