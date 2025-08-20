"""
Authentication validators for CircusCircus Forum
Handles validation for user registration and login
"""
import re
from forum.models import User


class AuthValidator:
    """Validation class for authentication operations"""
    
    # Regex patterns for validation
    PASSWORD_REGEX = re.compile(r"^[a-zA-Z0-9@#&%!]{6,40}$")
    USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9@#&%!]{3,40}$")
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @classmethod
    def validate_email(cls, email):
        """
        Validate email format and uniqueness
        Returns: (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        if not cls.EMAIL_REGEX.match(email):
            return False, "Invalid email format"
        
        if cls.is_email_taken(email):
            return False, "An account already exists with this email"
        
        return True, None

    @classmethod
    def validate_username(cls, username):
        """
        Validate username format and uniqueness
        Returns: (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        if len(username) < 3 or len(username) > 40:
            return False, "Username must be between 3-40 characters"
        
        if not cls.USERNAME_REGEX.match(username):
            return False, "Username can only contain letters, numbers, and @#&%! characters"
        
        if cls.is_username_taken(username):
            return False, "Username is already taken"
        
        return True, None

    @classmethod
    def validate_password(cls, password):
        """
        Validate password format and strength
        Returns: (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 6 or len(password) > 40:
            return False, "Password must be between 6-40 characters"
        
        if not cls.PASSWORD_REGEX.match(password):
            return False, "Password can only contain letters, numbers, and @#&%! characters"
        
        return True, None

    @classmethod
    def validate_registration(cls, email, username, password, confirm_password=None):
        """
        Validate complete registration form
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate email
        email_valid, email_error = cls.validate_email(email)
        if not email_valid:
            errors.append(email_error)
        
        # Validate username
        username_valid, username_error = cls.validate_username(username)
        if not username_valid:
            errors.append(username_error)
        
        # Validate password
        password_valid, password_error = cls.validate_password(password)
        if not password_valid:
            errors.append(password_error)
        
        # Validate password confirmation if provided
        if confirm_password is not None:
            if password != confirm_password:
                errors.append("Passwords do not match")
        
        return len(errors) == 0, errors

    @classmethod
    def validate_login(cls, username, password):
        """
        Validate login credentials
        Returns: (is_valid, error_message, user_object)
        """
        if not username or not password:
            return False, "Username and password are required", None
        
        # Check if user exists and password is correct
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.is_active:
                return False, "Account is deactivated", None
            return True, None, user
        
        return False, "Invalid username or password", None

    @classmethod
    def is_email_taken(cls, email):
        """Check if email is already registered"""
        return User.query.filter_by(email=email).first() is not None

    @classmethod
    def is_username_taken(cls, username):
        """Check if username is already taken"""
        return User.query.filter_by(username=username).first() is not None
