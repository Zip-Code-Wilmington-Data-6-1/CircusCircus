"""
Test script for authentication module validation
Tests the core functionality of the auth system
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forum.auth.auth_validators import AuthValidator

def test_email_validation():
    """Test email validation functionality"""
    print("Testing Email Validation:")
    
    test_cases = [
        ("valid@example.com", True),
        ("user.name@domain.co.uk", True),
        ("test+tag@example.org", True),
        ("invalid.email", False),
        ("@domain.com", False),
        ("user@", False),
        ("", False),
    ]
    
    for email, expected in test_cases:
        is_valid, error = AuthValidator.validate_email(email)
        # Note: This will show "email taken" error for valid emails if they exist in DB
        # In a real test, we'd mock the database
        if email and "@" in email and "." in email.split("@")[1]:
            # For valid format emails, we expect either True or "email taken" error
            result = is_valid or (error and "already exists" in error)
        else:
            result = is_valid == expected
        
        status = "✅" if result else "❌"
        print(f"  {status} {email:<25} -> {'Valid' if is_valid else error}")

def test_username_validation():
    """Test username validation functionality"""
    print("\nTesting Username Validation:")
    
    test_cases = [
        ("validuser", True),
        ("user123", True),
        ("user@name", True),
        ("test#user", True),
        ("user%name!", True),
        ("ab", False),  # too short
        ("a" * 41, False),  # too long
        ("user space", False),  # invalid character
        ("", False),
    ]
    
    for username, expected in test_cases:
        is_valid, error = AuthValidator.validate_username(username)
        # Similar to email, existing usernames will show "taken" error
        if username and len(username) >= 3 and len(username) <= 40:
            import re
            pattern = re.compile(r"^[a-zA-Z0-9@#&%!]{3,40}$")
            if pattern.match(username):
                result = is_valid or (error and "already taken" in error)
            else:
                result = is_valid == expected
        else:
            result = is_valid == expected
        
        status = "✅" if result else "❌"
        print(f"  {status} {username:<20} -> {'Valid' if is_valid else error}")

def test_password_validation():
    """Test password validation functionality"""
    print("\nTesting Password Validation:")
    
    test_cases = [
        ("password123", True),
        ("pass@word!", True),
        ("myPASS#123", True),
        ("test&pass%", True),
        ("12345", False),  # too short
        ("a" * 41, False),  # too long
        ("pass word", False),  # invalid character (space)
        ("password$", False),  # invalid character ($)
        ("", False),
    ]
    
    for password, expected in test_cases:
        is_valid, error = AuthValidator.validate_password(password)
        result = is_valid == expected
        status = "✅" if result else "❌"
        print(f"  {status} {password:<15} -> {'Valid' if is_valid else error}")

def test_registration_validation():
    """Test complete registration validation"""
    print("\nTesting Registration Validation:")
    
    test_cases = [
        {
            'email': 'newuser@test.com',
            'username': 'newuser123',
            'password': 'password123!',
            'confirm': 'password123!',
            'expected': True
        },
        {
            'email': 'invalid.email',
            'username': 'validuser',
            'password': 'validpass123',
            'confirm': 'validpass123',
            'expected': False  # Invalid email
        },
        {
            'email': 'valid@email.com',
            'username': 'ab',
            'password': 'validpass123',
            'confirm': 'validpass123',
            'expected': False  # Username too short
        },
        {
            'email': 'valid@email.com',
            'username': 'validuser',
            'password': '123',
            'confirm': '123',
            'expected': False  # Password too short
        },
        {
            'email': 'valid@email.com',
            'username': 'validuser',
            'password': 'password123',
            'confirm': 'different123',
            'expected': False  # Passwords don't match
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        is_valid, errors = AuthValidator.validate_registration(
            test_case['email'],
            test_case['username'],
            test_case['password'],
            test_case['confirm']
        )
        
        # For valid cases, we might get "email/username taken" errors, which is OK
        if test_case['expected'] and not is_valid:
            # Check if errors are only about email/username being taken
            acceptable_errors = all(
                'already exists' in error or 'already taken' in error
                for error in errors
            )
            result = acceptable_errors
        else:
            result = is_valid == test_case['expected']
        
        status = "✅" if result else "❌"
        print(f"  {status} Test case {i+1}: {'Valid' if is_valid else f'Errors: {errors}'}")

if __name__ == "__main__":
    print("CircusCircus Authentication Module Validation Tests")
    print("=" * 55)
    
    try:
        test_email_validation()
        test_username_validation()
        test_password_validation()
        test_registration_validation()
        
        print("\n" + "=" * 55)
        print("Validation tests completed!")
        print("\nNote: 'Email/username already exists' errors are expected")
        print("if you've already created users in the database.")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the project root directory.")
    except Exception as e:
        print(f"Test error: {e}")
        print("Make sure the auth module is properly set up.")
