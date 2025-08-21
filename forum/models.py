
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime

# create db here so it can be imported (with the models) into the App object.
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#OBJECT MODELS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    
    # User Profile Fields
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    bio = db.Column(db.Text)
    profile_picture_url = db.Column(db.Text)
    
    # User Settings
    show_email_publicly = db.Column(db.Boolean, default=False)
    receive_notifications = db.Column(db.Boolean, default=True)
    theme_preference = db.Column(db.Text, default='light')  # 'light' or 'dark'
    
    # Account Management
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    posts = db.relationship("Post", backref="user", lazy='dynamic')
    comments = db.relationship("Comment", backref="user", lazy='dynamic')
    
    # Direct Messages relationships
    sent_messages = db.relationship('DirectMessage', 
                                  foreign_keys='DirectMessage.sender_id',
                                  backref='sender', 
                                  lazy='dynamic')
    received_messages = db.relationship('DirectMessage', 
                                      foreign_keys='DirectMessage.recipient_id',
                                      backref='recipient', 
                                      lazy='dynamic')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.created_at = datetime.datetime.utcnow()
        self.last_seen = datetime.datetime.utcnow()
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
<<<<<<< Updated upstream
    def get_full_name(self):
        """Return the user's full name if available, otherwise username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.username
    
    def update_last_seen(self):
        """Update the last seen timestamp"""
        self.last_seen = datetime.datetime.utcnow()
        db.session.commit()
    
    def get_post_count(self):
        """Get the number of posts by this user"""
        return self.posts.count()
    
    def get_comment_count(self):
        """Get the number of comments by this user"""
        return self.comments.count()
    
    def can_send_message_to(self, user):
        """Check if this user can send messages to another user"""
        # Users can send messages to each other if both are active
        return self.is_active and user.is_active
    
    def get_unread_message_count(self):
        """Get count of unread messages for this user"""
        return self.received_messages.filter_by(is_read=False).count()
    
    def __repr__(self):
        return f'<User {self.username}>'
    
=======
    # New Methods 
    # Flask-Login requires these methods for user management
    def get_id(self):
         return str(self.id)
    
    @property
    def is_authenticated(self):
        """Check if user is authenticated"""
        return True
    
    @property
    def is_active(self):
        """Check if user is active"""
        return True
    
    
    @property
    def is_anonymous(self):
        """Check if user is anonymous"""
        return False




# Emoji Reaction model
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emoji = db.Column(db.String(16), nullable=False)  # e.g. 'like', 'heart', 'smile', or even the emoji itself
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user = db.relationship('User', backref='reactions')
    post = db.relationship('Post', backref='reactions')

>>>>>>> Stashed changes
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)  # Support for public/private posts
    comments = db.relationship("Comment", backref="post")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subforum_id = db.Column(db.Integer, db.ForeignKey('subforum.id'))
    postdate = db.Column(db.DateTime)

    #cache stuff
    lastcheck = None
    savedresponce = None
    def __init__(self, title, content, postdate, is_public=True):
        self.title = title
        self.content = content
        self.postdate = postdate
        self.is_public = is_public
    def get_time_string(self):
        #this only needs to be calculated every so often, not for every request
        #this can be a rudamentary chache
        now = datetime.datetime.now()
        if self.lastcheck is None or (now - self.lastcheck).total_seconds() > 30:
            self.lastcheck = now
        else:
            return self.savedresponce

        diff = now - self.postdate

        seconds = diff.total_seconds()
        print(seconds)
        if seconds / (60 * 60 * 24 * 30) > 1:
            self.savedresponce =  " " + str(int(seconds / (60 * 60 * 24 * 30))) + " months ago"
        elif seconds / (60 * 60 * 24) > 1:
            self.savedresponce =  " " + str(int(seconds / (60*  60 * 24))) + " days ago"
        elif seconds / (60 * 60) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60))) + " hours ago"
        elif seconds / (60) > 1:
            self.savedresponce = " " + str(int(seconds / 60)) + " minutes ago"
        else:
            self.savedresponce =  "Just a moment ago!"

        return self.savedresponce

class Subforum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True)
    description = db.Column(db.Text)
    subforums = db.relationship("Subforum")
    parent_id = db.Column(db.Integer, db.ForeignKey('subforum.id'))
    posts = db.relationship("Post", backref="subforum")
    path = None
    hidden = db.Column(db.Boolean, default=False)
    def __init__(self, title, description):
        self.title = title
        self.description = description

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    postdate = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    lastcheck = None
    savedresponce = None
    def __init__(self, content, postdate):
        self.content = content
        self.postdate = postdate
    def get_time_string(self):
        #this only needs to be calculated every so often, not for every request
        #this can be a rudamentary chache
        now = datetime.datetime.now()
        if self.lastcheck is None or (now - self.lastcheck).total_seconds() > 30:
            self.lastcheck = now
        else:
            return self.savedresponce

        diff = now - self.postdate
        seconds = diff.total_seconds()
        if seconds / (60 * 60 * 24 * 30) > 1:
            self.savedresponce =  " " + str(int(seconds / (60 * 60 * 24 * 30))) + " months ago"
        elif seconds / (60 * 60 * 24) > 1:
            self.savedresponce =  " " + str(int(seconds / (60*  60 * 24))) + " days ago"
        elif seconds / (60 * 60) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60))) + " hours ago"
        elif seconds / (60) > 1:
            self.savedresponce = " " + str(int(seconds / 60)) + " minutes ago"
        else:
            self.savedresponce =  "Just a moment ago!"
        return self.savedresponce

class DirectMessage(db.Model):
    """Model for direct messages between users"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __init__(self, sender_id, recipient_id, subject, content):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.subject = subject
        self.content = content
        self.timestamp = datetime.datetime.utcnow()
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        db.session.commit()
    
    def get_time_string(self):
        """Get a human-readable time string for when the message was sent"""
        now = datetime.datetime.utcnow()
        diff = now - self.timestamp
        seconds = diff.total_seconds()
        
        if seconds / (60 * 60 * 24 * 30) > 1:
            return f"{int(seconds / (60 * 60 * 24 * 30))} months ago"
        elif seconds / (60 * 60 * 24) > 1:
            return f"{int(seconds / (60 * 60 * 24))} days ago"
        elif seconds / (60 * 60) > 1:
            return f"{int(seconds / (60 * 60))} hours ago"
        elif seconds / 60 > 1:
            return f"{int(seconds / 60)} minutes ago"
        else:
            return "Just now"
    
    def __repr__(self):
        return f'<DirectMessage from {self.sender_id} to {self.recipient_id}: {self.subject}>'

def error(errormessage):
	return "<b style=\"color: red;\">" + errormessage + "</b>"

def generateLinkPath(subforumid):
	links = []
	subforum = Subforum.query.filter(Subforum.id == subforumid).first()
	parent = Subforum.query.filter(Subforum.id == subforum.parent_id).first()
	links.append("<a href=\"/subforum?sub=" + str(subforum.id) + "\">" + subforum.title + "</a>")
	while parent is not None:
		links.append("<a href=\"/subforum?sub=" + str(parent.id) + "\">" + parent.title + "</a>")
		parent = Subforum.query.filter(Subforum.id == parent.parent_id).first()
	links.append("<a href=\"/\">Forum Index</a>")
	link = ""
	for l in reversed(links):
		link = link + " / " + l
	return link


#Post checks
def valid_title(title):
	return len(title) > 4 and len(title) < 140
def valid_content(content):
	return len(content) > 10 and len(content) < 5000

