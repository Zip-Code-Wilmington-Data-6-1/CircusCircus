"""
Authentication routes for CircusCircus Forum
Handles all authentication-related routes including login, registration, logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from forum.models import db, User
from .auth_validators import AuthValidator
from .auth_models import AuthUser, LoginAttempt
import datetime


# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.index', _external=False, _scheme=''))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate registration data
        is_valid, errors = AuthValidator.validate_registration(
            email, username, password, confirm_password
        )
        
        if is_valid:
            try:
                # Create new user
                user = AuthUser.create_user(email, username, password)
                if user:
                    db.session.add(user)
                    db.session.commit()
                    
                    # Log successful registration
                    flash('Account created successfully! Please log in.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    errors = ['Error creating account. Please try again.']
            
            except Exception as e:
                db.session.rollback()
                errors = ['An error occurred during registration. Please try again.']
                current_app.logger.error(f"Registration error: {str(e)}")
        
        return render_template('auth/register.html', errors=errors, 
                             email=email, username=username)
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.index', _external=False, _scheme=''))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        # Get client IP for rate limiting
        client_ip = request.remote_addr or 'unknown'
        user_agent = request.headers.get('User-Agent', '')
        
        # Check rate limiting
        if LoginAttempt.is_rate_limited(username, client_ip):
            LoginAttempt.log_attempt(username, client_ip, False, user_agent)
            flash('Too many failed login attempts. Please try again later.', 'error')
            return render_template('auth/login.html', username=username)
        
        # Validate and authenticate user
        is_valid, error_message, user = AuthValidator.validate_login(username, password)
        
        if is_valid and user:
            # Log successful attempt
            LoginAttempt.log_attempt(username, client_ip, True, user_agent)
            
            # Login user
            login_user(user, remember=remember_me)
            
            # Update last seen
            user.last_seen = datetime.datetime.utcnow()
            db.session.commit()
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('routes.index', _external=False, _scheme=''))
        else:
            # Log failed attempt
            LoginAttempt.log_attempt(username, client_ip, False, user_agent)
            
            flash(error_message or 'Invalid username or password', 'error')
            return render_template('auth/login.html', username=username)
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('routes.index', _external=False, _scheme=''))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        
        # Validate current password
        if not current_user.check_password(current_password):
            errors.append('Current password is incorrect')
        
        # Validate new password
        password_valid, password_error = AuthValidator.validate_password(new_password)
        if not password_valid:
            errors.append(password_error)
        
        # Check password confirmation
        if new_password != confirm_password:
            errors.append('New passwords do not match')
        
        if not errors:
            # Change password
            if AuthUser.change_password(current_user, current_password, new_password):
                flash('Password changed successfully!', 'success')
                return redirect(url_for('auth.profile'))
            else:
                errors.append('Error changing password. Please try again.')
        
        return render_template('auth/change_password.html', errors=errors)
    
    return render_template('auth/change_password.html')


@auth_bp.route('/users')
@login_required
def users_list():
    """List all users (admin only or basic user list)"""
    if current_user.admin:
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('auth/admin_users.html', users=users)
    else:
        # Regular users can see basic user list
        users = User.query.filter_by(is_active=True).order_by(User.username).all()
        return render_template('auth/users_list.html', users=users)


@auth_bp.route('/user/<int:user_id>')
@login_required
def view_user(user_id):
    """View user profile"""
    user = User.query.get_or_404(user_id)
    
    # Basic privacy check - users can view public profiles
    if not user.is_active and not current_user.admin:
        flash('User not found.', 'error')
        return redirect(url_for('auth.users_list'))
    
    return render_template('auth/view_user.html', user=user)


@auth_bp.route('/admin/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
def admin_toggle_user_active(user_id):
    """Admin route to activate/deactivate users"""
    if not current_user.admin:
        flash('Access denied.', 'error')
        return redirect(url_for('routes.index', _external=False, _scheme=''))
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('auth.users_list'))
    
    # Toggle active status
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('auth.users_list'))


@auth_bp.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def admin_toggle_user_admin(user_id):
    """Admin route to grant/revoke admin privileges"""
    if not current_user.admin:
        flash('Access denied.', 'error')
        return redirect(url_for('routes.index', _external=False, _scheme=''))
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'error')
        return redirect(url_for('auth.users_list'))
    
    # Toggle admin status
    user.admin = not user.admin
    db.session.commit()
    
    status = 'granted' if user.admin else 'revoked'
    flash(f'Admin privileges {status} for user {user.username}.', 'success')
    
    return redirect(url_for('auth.users_list'))


# Legacy routes for backward compatibility with existing code
@auth_bp.route('/action_login', methods=['POST'])
def action_login():
    """Legacy login route for backward compatibility"""
    return login()


@auth_bp.route('/action_logout')
def action_logout():
    """Legacy logout route for backward compatibility"""
    return logout()


@auth_bp.route('/action_createaccount', methods=['POST'])
def action_createaccount():
    """Legacy registration route for backward compatibility"""
    return register()


@auth_bp.route('/loginform')
def loginform():
    """Legacy login form route for backward compatibility"""
    return login()
