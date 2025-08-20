"""
User settings and profile management functionality
"""

from .models import db, User
from .user import valid_name, valid_bio, valid_profile_picture_url, valid_email
import datetime

class UserSettingsManager:
    """Class to handle user settings and profile updates"""
    
    def __init__(self, user):
        self.user = user
    
    def update_profile(self, first_name=None, last_name=None, bio=None, profile_picture_url=None):
        """Update user profile information"""
        errors = []
        
        if first_name is not None:
            if not valid_name(first_name):
                errors.append("First name can only contain letters, spaces, hyphens, and apostrophes (max 50 characters)")
            else:
                self.user.first_name = first_name.strip() if first_name else None
        
        if last_name is not None:
            if not valid_name(last_name):
                errors.append("Last name can only contain letters, spaces, hyphens, and apostrophes (max 50 characters)")
            else:
                self.user.last_name = last_name.strip() if last_name else None
        
        if bio is not None:
            if not valid_bio(bio):
                errors.append("Bio cannot exceed 500 characters")
            else:
                self.user.bio = bio.strip() if bio else None
        
        if profile_picture_url is not None:
            if not valid_profile_picture_url(profile_picture_url):
                errors.append("Profile picture must be a valid image URL (jpg, jpeg, png, gif, webp)")
            else:
                self.user.profile_picture_url = profile_picture_url.strip() if profile_picture_url else None
        
        if not errors:
            db.session.commit()
            return True, "Profile updated successfully"
        
        return False, errors
    
    def update_settings(self, show_email_publicly=None, receive_notifications=None, theme_preference=None):
        """Update user privacy and preference settings"""
        errors = []
        
        if show_email_publicly is not None:
            self.user.show_email_publicly = bool(show_email_publicly)
        
        if receive_notifications is not None:
            self.user.receive_notifications = bool(receive_notifications)
        
        if theme_preference is not None:
            if theme_preference not in ['light', 'dark']:
                errors.append("Theme preference must be 'light' or 'dark'")
            else:
                self.user.theme_preference = theme_preference
        
        if not errors:
            db.session.commit()
            return True, "Settings updated successfully"
        
        return False, errors
    
    def update_email(self, new_email):
        """Update user email with validation"""
        from .user import email_taken
        
        if not valid_email(new_email):
            return False, "Invalid email format"
        
        if email_taken(new_email) and new_email != self.user.email:
            return False, "An account with this email already exists"
        
        self.user.email = new_email
        self.user.email_verified = False  # Email needs to be verified again
        db.session.commit()
        
        return True, "Email updated successfully. Please verify your new email address."
    
    def change_password(self, current_password, new_password):
        """Change user password with validation"""
        from werkzeug.security import generate_password_hash
        from .user import valid_password
        
        if not self.user.check_password(current_password):
            return False, "Current password is incorrect"
        
        if not valid_password(new_password):
            return False, "New password must be 6-40 characters and contain only letters, numbers, and !@#%&"
        
        self.user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return True, "Password changed successfully"
    
    def deactivate_account(self):
        """Deactivate user account"""
        self.user.is_active = False
        db.session.commit()
        return True, "Account deactivated successfully"
    
    def reactivate_account(self):
        """Reactivate user account (admin function)"""
        self.user.is_active = True
        db.session.commit()
        return True, "Account reactivated successfully"

class UserStatsManager:
    """Class to handle user statistics and activity tracking"""
    
    def __init__(self, user):
        self.user = user
    
    def get_user_stats(self):
        """Get comprehensive user statistics"""
        return {
            'post_count': self.user.get_post_count(),
            'comment_count': self.user.get_comment_count(),
            'unread_messages': self.user.get_unread_message_count(),
            'account_age_days': (datetime.datetime.utcnow() - self.user.created_at).days,
            'last_seen': self.user.last_seen,
            'is_active': self.user.is_active,
            'is_admin': self.user.admin
        }
    
    def get_recent_activity(self, limit=10):
        """Get user's recent posts and comments"""
        recent_posts = self.user.posts.order_by(self.user.posts.postdate.desc()).limit(limit).all()
        recent_comments = self.user.comments.order_by(self.user.comments.postdate.desc()).limit(limit).all()
        
        # Combine and sort by date
        activity = []
        for post in recent_posts:
            activity.append({
                'type': 'post',
                'id': post.id,
                'title': post.title,
                'date': post.postdate,
                'content_preview': post.content[:100] + '...' if len(post.content) > 100 else post.content
            })
        
        for comment in recent_comments:
            activity.append({
                'type': 'comment',
                'id': comment.id,
                'post_title': comment.post.title,
                'date': comment.postdate,
                'content_preview': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content
            })
        
        # Sort by date, most recent first
        activity.sort(key=lambda x: x['date'], reverse=True)
        return activity[:limit]

def get_user_settings_manager(user_id):
    """Factory function to create UserSettingsManager"""
    user = User.query.get(user_id)
    if not user:
        return None
    return UserSettingsManager(user)

def get_user_stats_manager(user_id):
    """Factory function to create UserStatsManager"""
    user = User.query.get(user_id)
    if not user:
        return None
    return UserStatsManager(user)
