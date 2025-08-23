from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from forum.models import db, User, Post, Comment
from werkzeug.security import check_password_hash

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
def index():
    """Display user settings dashboard"""
    return render_template('settings/index.html', user=current_user)

@settings_bp.route('/profile')
@login_required
def profile():
    """Display user profile information"""
    post_count = current_user.get_post_count()
    comment_count = current_user.get_comment_count()
    
    return render_template('settings/profile.html', 
                         user=current_user,
                         post_count=post_count,
                         comment_count=comment_count)

@settings_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('settings/change_password.html')
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
            return render_template('settings/change_password.html')
        
        # Check if passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('settings/change_password.html')
        
        # Update password
        current_user.update_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('settings.index'))
    
    return render_template('settings/change_password.html')

@settings_bp.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email():
    """Change user email address"""
    if request.method == 'POST':
        new_email = request.form.get('new_email')
        password = request.form.get('password')
        
        # Validate password
        if not current_user.check_password(password):
            flash('Password is incorrect.', 'error')
            return render_template('settings/change_email.html')
        
        # Validate email format (basic validation)
        if '@' not in new_email or '.' not in new_email:
            flash('Please enter a valid email address.', 'error')
            return render_template('settings/change_email.html')
        
        # Check if email is already taken
        existing_user = User.query.filter(User.email == new_email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email address is already in use.', 'error')
            return render_template('settings/change_email.html')
        
        # Update email
        current_user.update_email(new_email)
        db.session.commit()
        
        flash('Email address changed successfully!', 'success')
        return redirect(url_for('settings.index'))
    
    return render_template('settings/change_email.html')

@settings_bp.route('/account_info')
@login_required
def account_info():
    from forum.models import Post, Comment
    
    # Try different possible field names
    try:
        post_count = Post.query.filter_by(author_id=current_user.id).count()
    except:
        try:
            post_count = Post.query.filter_by(poster_id=current_user.id).count()
        except:
            try:
                post_count = Post.query.filter_by(user_id=current_user.id).count()
            except:
                post_count = 0  # Fallback if no matching field
    
    try:
        comment_count = Comment.query.filter_by(author_id=current_user.id).count()
    except:
        try:
            comment_count = Comment.query.filter_by(poster_id=current_user.id).count()
        except:
            try:
                comment_count = Comment.query.filter_by(user_id=current_user.id).count()
            except:
                comment_count = 0  # Fallback if no matching field
    
    return render_template('settings/account_info.html', 
                         user=current_user, 
                         post_count=post_count, 
                         comment_count=comment_count)