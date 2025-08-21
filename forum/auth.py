"""
Authentication Module for CircusCircus Forum
Handles user registration, login, logout, and profile management
Extracted and modernized from routes.py to match team's modular structure
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from forum.models import db, User
import re
import datetime

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates')

# Validation patterns - Meeting your exact requirements
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9@#&%!]{3,40}$")
PASSWORD_REGEX = re.compile(r"^[a-zA-Z0-9@#&%!]{6,40}$")


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_email(email, exclude_user_id=None):
    """
    Validate email format and uniqueness
    Args:
        email: Email to validate
        exclude_user_id: User ID to exclude from uniqueness check (for profile updates)
    Returns:
        tuple: (is_valid, error_message)
    """
    if not email or not EMAIL_REGEX.match(email):
        return False, "Invalid email format"
    
    query = User.query.filter_by(email=email)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    
    if query.first():
        return False, "Email already exists"
    return True, None


def validate_username(username, exclude_user_id=None):
    """
    Validate username format and uniqueness
    Args:
        username: Username to validate
        exclude_user_id: User ID to exclude from uniqueness check (for profile updates)
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username or not USERNAME_REGEX.match(username):
        return False, "Username must be 3-40 characters with letters, numbers, and @#&%!"
    
    query = User.query.filter_by(username=username)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    
    if query.first():
        return False, "Username already taken"
    return True, None


def validate_password(password):
    """
    Validate password format
    Args:
        password: Password to validate
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password or not PASSWORD_REGEX.match(password):
        return False, "Password must be 6-40 characters with letters, numbers, and @#&%!"
    return True, None


def validate_registration_form(email, username, password, confirm_password, exclude_user_id=None):
    """
    Validate complete registration form data
    Args:
        email: Email address
        username: Username
        password: Password
        confirm_password: Password confirmation
        exclude_user_id: User ID to exclude from uniqueness checks
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate email
    email_valid, email_error = validate_email(email, exclude_user_id)
    if not email_valid:
        errors.append(email_error)
    
    # Validate username
    username_valid, username_error = validate_username(username, exclude_user_id)
    if not username_valid:
        errors.append(username_error)
    
    # Validate password
    password_valid, password_error = validate_password(password)
    if not password_valid:
        errors.append(password_error)
    
    # Check password confirmation
    if password != confirm_password:
        errors.append("Passwords do not match")
    
    return len(errors) == 0, errors


# ============================================================================
# AUTHENTICATION ROUTES - NEW MODERN STRUCTURE
# ============================================================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route - Modern replacement for /action_createaccount
    Handles both GET (display form) and POST (process registration)
    """
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Extract form data
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate all inputs
        is_valid, errors = validate_registration_form(email, username, password, confirm_password)
        
        if is_valid:
            try:
                # Create new user - using your existing User constructor
                user = User(email=email, username=username, password=password)
                
                # Auto-assign admin if username is "admin" (matching your existing logic)
                if username.lower() == "admin":
                    user.admin = True
                
                # Save to database
                db.session.add(user)
                db.session.commit()
                
                # Success message and redirect to login
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            
            except Exception as e:
                db.session.rollback()
                errors = ["Database error. Please try again."]
                print(f"Registration error: {e}")  # Log for debugging
        
        # If validation failed or database error, redisplay form with errors
        return render_template('auth/register.html', errors=errors, 
                             email=email, username=username)
    
    # GET request - display registration form
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route - Modern replacement for /action_login
    Handles both GET (display form) and POST (process login)
    """
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Extract form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        # Basic input validation
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('auth/login.html', username=username)
        
        # Find user and authenticate - matching your existing logic
        user = User.query.filter(User.username == username).first()
        
        if user and user.check_password(password):
            # Successful authentication
            login_user(user, remember=remember_me)
            
            # Update last seen if field exists (future enhancement)
            if hasattr(user, 'last_seen'):
                user.last_seen = datetime.datetime.utcnow()
                db.session.commit()
            
            # Check for next parameter and redirect accordingly
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('index'))
        else:
            # Authentication failed - matching your existing error message
            flash('Username or password is incorrect!', 'error')
            return render_template('auth/login.html', username=username)
    
    # GET request - display login form
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route - Modern replacement for /action_logout
    """
    username = current_user.username
    logout_user()
    flash(f'Goodbye, {username}! You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """
    User profile display - New feature
    Shows user information, posts, comments, etc.
    """
    # Get user statistics
    post_count = len(current_user.posts) if current_user.posts else 0
    comment_count = len(current_user.comments) if current_user.comments else 0
    
    # Get recent posts (latest 5)
    recent_posts = []
    if current_user.posts:
        recent_posts = sorted(current_user.posts, 
                            key=lambda p: p.postdate if p.postdate else datetime.datetime.min, 
                            reverse=True)[:5]
    
    return render_template('auth/profile.html', 
                         user=current_user,
                         post_count=post_count,
                         comment_count=comment_count,
                         recent_posts=recent_posts)


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit user profile - New feature
    Allows users to update their email and username
    """
    if request.method == 'POST':
        # Extract form data
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        
        # Validate inputs (excluding current user from uniqueness check)
        email_valid, email_error = validate_email(email, current_user.id)
        username_valid, username_error = validate_username(username, current_user.id)
        
        errors = []
        if not email_valid:
            errors.append(email_error)
        if not username_valid:
            errors.append(username_error)
        
        if not errors:
            try:
                # Update user information
                current_user.email = email
                current_user.username = username
                db.session.commit()
                
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('auth.profile'))
            
            except Exception as e:
                db.session.rollback()
                errors = ["Database error. Please try again."]
                print(f"Profile update error: {e}")  # Log for debugging
        
        # Redisplay form with errors
        return render_template('auth/edit_profile.html', errors=errors, user=current_user)
    
    # GET request - display edit form
    return render_template('auth/edit_profile.html', user=current_user)


@auth_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change user password - New feature
    Allows users to update their password with proper validation
    """
    if request.method == 'POST':
        # Extract form data
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        
        # Verify current password
        if not current_user.check_password(current_password):
            errors.append("Current password is incorrect")
        
        # Validate new password format
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            errors.append(password_error)
        
        # Check password confirmation
        if new_password != confirm_password:
            errors.append("New passwords do not match")
        
        # Check that new password is different from current
        if current_password == new_password:
            errors.append("New password must be different from current password")
        
        if not errors:
            try:
                # Update password by creating a new user instance temporarily to hash password
                from werkzeug.security import generate_password_hash
                current_user.password_hash = generate_password_hash(new_password)
                
                db.session.commit()
                
                flash('Password changed successfully!', 'success')
                return redirect(url_for('auth.profile'))
            
            except Exception as e:
                db.session.rollback()
                errors = ["Database error. Please try again."]
                print(f"Password change error: {e}")  # Log for debugging
        
        # Redisplay form with errors
        return render_template('auth/change_password.html', errors=errors)
    
    # GET request - display password change form
    return render_template('auth/change_password.html')


# ============================================================================
# LEGACY COMPATIBILITY ROUTES
# Maintains backward compatibility with existing routes.py structure
# ============================================================================

@auth_bp.route('/action_login', methods=['POST'])
def action_login():
    """
    Legacy login route - Maintains compatibility with existing forms
    Redirects to modern login handler
    """
    return login()


@auth_bp.route('/action_logout')
def action_logout():
    """
    Legacy logout route - Maintains compatibility with existing links
    Redirects to modern logout handler
    """
    return logout()


@auth_bp.route('/action_createaccount', methods=['POST'])
def action_createaccount():
    """
    Legacy account creation route - Maintains compatibility with existing forms
    Redirects to modern registration handler
    """
    return register()


@auth_bp.route('/loginform')
def loginform():
    """
    Legacy login form route - Maintains compatibility with existing navigation
    Redirects to modern login form
    """
    return redirect(url_for('auth.login'))


# ============================================================================
# UTILITY FUNCTIONS FOR OTHER MODULES
# ============================================================================

def get_user_stats(user):
    """
    Get user statistics for use in other modules
    Args:
        user: User object
    Returns:
        dict: User statistics
    """
    return {
        'posts_count': len(user.posts) if user.posts else 0,
        'comments_count': len(user.comments) if user.comments else 0,
        'is_admin': user.admin,
        'username': user.username,
        'email': user.email,
        'member_since': getattr(user, 'created_at', None)
    }


def is_admin_user(user):
    """
    Check if user has admin privileges
    Args:
        user: User object
    Returns:
        bool: True if user is admin
    """
    return getattr(user, 'admin', False)


def username_available(username, exclude_user_id=None):
    """
    Check if username is available (for use by other modules)
    Args:
        username: Username to check
        exclude_user_id: User ID to exclude from check
    Returns:
        bool: True if available
    """
    is_valid, error = validate_username(username, exclude_user_id)
    return is_valid


def email_available(email, exclude_user_id=None):
    """
    Check if email is available (for use by other modules)
    Args:
        email: Email to check
        exclude_user_id: User ID to exclude from check
    Returns:
        bool: True if available
    """
    is_valid, error = validate_email(email, exclude_user_id)
    return is_valid


# ============================================================================
# ADMIN UTILITIES (Future Enhancement)
# ============================================================================

def admin_required(f):
    """
    Decorator to require admin privileges for a route
    Usage: @admin_required
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.admin:
            flash('Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


# Export the blueprint for registration in main app
__all__ = ['auth_bp']