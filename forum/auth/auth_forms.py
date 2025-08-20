"""
Authentication forms for CircusCircus Forum
Handles form validation and rendering for user authentication
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from forum.models import User


class RegistrationForm(FlaskForm):
    """User registration form with validation"""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=40, message='Username must be between 3-40 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, max=40, message='Password must be between 6-40 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Create Account')
    
    def validate_email(self, email):
        """Custom validator for email uniqueness"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account already exists with this email address.')
    
    def validate_username(self, username):
        """Custom validator for username uniqueness and format"""
        import re
        
        # Check format
        username_pattern = re.compile(r"^[a-zA-Z0-9@#&%!]{3,40}$")
        if not username_pattern.match(username.data):
            raise ValidationError('Username can only contain letters, numbers, and @#&%! characters.')
        
        # Check uniqueness
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')
    
    def validate_password(self, password):
        """Custom validator for password format"""
        import re
        
        password_pattern = re.compile(r"^[a-zA-Z0-9@#&%!]{6,40}$")
        if not password_pattern.match(password.data):
            raise ValidationError('Password can only contain letters, numbers, and @#&%! characters.')


class LoginForm(FlaskForm):
    """User login form"""
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember Me')
    
    submit = SubmitField('Sign In')


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form"""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format')
    ])
    
    submit = SubmitField('Request Password Reset')


class PasswordResetForm(FlaskForm):
    """Password reset form"""
    
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, max=40, message='Password must be between 6-40 characters')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Reset Password')
    
    def validate_password(self, password):
        """Custom validator for password format"""
        import re
        
        password_pattern = re.compile(r"^[a-zA-Z0-9@#&%!]{6,40}$")
        if not password_pattern.match(password.data):
            raise ValidationError('Password can only contain letters, numbers, and @#&%! characters.')


class ChangePasswordForm(FlaskForm):
    """Change password form for logged-in users"""
    
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=6, max=40, message='Password must be between 6-40 characters')
    ])
    
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, new_password):
        """Custom validator for new password format"""
        import re
        
        password_pattern = re.compile(r"^[a-zA-Z0-9@#&%!]{6,40}$")
        if not password_pattern.match(new_password.data):
            raise ValidationError('Password can only contain letters, numbers, and @#&%! characters.')
