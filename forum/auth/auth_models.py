"""
Authentication models and utilities for CircusCircus Forum
Contains user authentication related database models and helper functions

Test the system:
Visit /auth/register for new account creation
Visit /auth/login for user login
Use admin/admin123! for admin access
http://127.0.0.1:5000/
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from forum.models import db, User
import datetime
import secrets
import hashlib


class AuthUser(UserMixin):
    """
    Extended User class with authentication-specific methods
    This extends the base User model with auth-specific functionality
    """
    
    @staticmethod
    def create_user(email, username, password):
        """
        Create a new user with proper validation and hashing
        Args:
            email: User's email address (must be unique)
            username: User's username (must be unique)
            password: Plain text password (will be hashed)
        Returns:
            User object or None if creation fails
        """
        try:
            # Create new user instance
            user = User(email=email, username=username, password=password)
            
            # Set admin status if username is 'admin'
            if username.lower() == "admin":
                user.admin = True
            
            # Set default values
            user.is_active = True
            user.email_verified = False
            user.created_at = datetime.datetime.utcnow()
            user.last_seen = datetime.datetime.utcnow()
            
            return user
            
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate user with username and password
        Args:
            username: Username to authenticate
            password: Plain text password
        Returns:
            User object if authentication successful, None otherwise
        """
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            # Update last seen timestamp
            user.last_seen = datetime.datetime.utcnow()
            db.session.commit()
            return user
        
        return None
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email address"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def activate_user(user):
        """Activate a user account"""
        user.is_active = True
        user.email_verified = True
        db.session.commit()
        return True
    
    @staticmethod
    def deactivate_user(user):
        """Deactivate a user account"""
        user.is_active = False
        db.session.commit()
        return True
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password after verifying old password
        Args:
            user: User object
            old_password: Current password (plain text)
            new_password: New password (plain text)
        Returns:
            True if successful, False otherwise
        """
        if user.check_password(old_password):
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def reset_password(user, new_password):
        """
        Reset user password (for admin or password reset functionality)
        Args:
            user: User object
            new_password: New password (plain text)
        Returns:
            True if successful
        """
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True


class AuthToken(db.Model):
    """
    Model for storing authentication tokens (password reset, email verification, etc.)
    """
    __tablename__ = 'auth_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    token_type = db.Column(db.String(50), nullable=False)  # 'password_reset', 'email_verification'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref='auth_tokens')
    
    def __init__(self, user_id, token_type, expires_in_hours=24):
        self.user_id = user_id
        self.token_type = token_type
        self.token = self.generate_token()
        self.created_at = datetime.datetime.utcnow()
        self.expires_at = self.created_at + datetime.timedelta(hours=expires_in_hours)
        self.is_used = False
    
    def generate_token(self):
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        """Check if token is expired"""
        return datetime.datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def use_token(self):
        """Mark token as used"""
        self.is_used = True
        db.session.commit()
    
    @staticmethod
    def create_token(user_id, token_type, expires_in_hours=24):
        """Create a new authentication token"""
        # Invalidate any existing tokens of the same type for this user
        AuthToken.query.filter_by(
            user_id=user_id, 
            token_type=token_type, 
            is_used=False
        ).update({'is_used': True})
        
        # Create new token
        token = AuthToken(user_id, token_type, expires_in_hours)
        db.session.add(token)
        db.session.commit()
        return token
    
    @staticmethod
    def verify_token(token_string, token_type):
        """
        Verify a token and return associated user if valid
        Args:
            token_string: Token string to verify
            token_type: Expected token type
        Returns:
            User object if token is valid, None otherwise
        """
        token = AuthToken.query.filter_by(
            token=token_string, 
            token_type=token_type
        ).first()
        
        if token and token.is_valid():
            return token.user
        
        return None


class LoginAttempt(db.Model):
    """
    Model for tracking login attempts (for security/rate limiting)
    """
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 compatible
    successful = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_agent = db.Column(db.Text)
    
    def __init__(self, username, ip_address, successful=False, user_agent=None):
        self.username = username
        self.ip_address = ip_address
        self.successful = successful
        self.attempted_at = datetime.datetime.utcnow()
        self.user_agent = user_agent
    
    @staticmethod
    def log_attempt(username, ip_address, successful=False, user_agent=None):
        """Log a login attempt"""
        attempt = LoginAttempt(username, ip_address, successful, user_agent)
        db.session.add(attempt)
        db.session.commit()
        return attempt
    
    @staticmethod
    def get_failed_attempts(username, ip_address, hours=1):
        """Get count of failed login attempts within specified hours"""
        cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        
        return LoginAttempt.query.filter(
            LoginAttempt.username == username,
            LoginAttempt.ip_address == ip_address,
            LoginAttempt.successful == False,
            LoginAttempt.attempted_at > cutoff_time
        ).count()
    
    @staticmethod
    def is_rate_limited(username, ip_address, max_attempts=5, hours=1):
        """Check if user/IP is rate limited due to failed attempts"""
        failed_count = LoginAttempt.get_failed_attempts(username, ip_address, hours)
        return failed_count >= max_attempts
