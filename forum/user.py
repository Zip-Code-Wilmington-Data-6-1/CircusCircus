
from .models import User, DirectMessage

import re

##
# Some utility routines and validation functions for user management
##

password_regex = re.compile("^[a-zA-Z0-9!@#%&]{6,40}$")
username_regex = re.compile("^[a-zA-Z0-9!@#%&]{4,40}$")
email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

#Account checks
def valid_username(username):
	if not username_regex.match(username):
		#username does not meet requirements
		return False
	#username is not taken and does meet the requirements
	return True

def valid_password(password):
	return password_regex.match(password)

def valid_email(email):
	"""Validate email format"""
	return email_regex.match(email)

def valid_name(name):
	"""Validate first/last name - allow letters, spaces, hyphens, apostrophes"""
	if not name:
		return True  # Names are optional
	name_regex = re.compile(r"^[a-zA-Z\s\-']{1,50}$")
	return name_regex.match(name)

def valid_bio(bio):
	"""Validate user bio - max 500 characters"""
	if not bio:
		return True  # Bio is optional
	return len(bio) <= 500

def valid_profile_picture_url(url):
	"""Basic validation for profile picture URL"""
	if not url:
		return True  # Profile picture is optional
	# Basic URL validation - could be enhanced
	url_regex = re.compile(r'^https?://.*\.(jpg|jpeg|png|gif|webp)$', re.IGNORECASE)
	return url_regex.match(url)

def username_taken(username):
	return User.query.filter(User.username == username).first()

def email_taken(email):
	return User.query.filter(User.email == email).first()

def get_user_by_username(username):
	"""Get user by username"""
	return User.query.filter(User.username == username).first()

def get_user_by_id(user_id):
	"""Get user by ID"""
	return User.query.get(user_id)

def create_user(email, username, password, first_name=None, last_name=None, bio=None):
	"""Create a new user with optional profile information"""
	user = User(email=email, username=username, password=password)
	if first_name:
		user.first_name = first_name
	if last_name:
		user.last_name = last_name
	if bio:
		user.bio = bio
	
	# Set admin status for admin username
	if username.lower() == "admin":
		user.admin = True
	
	return user

def send_direct_message(sender_id, recipient_id, subject, content):
	"""Send a direct message from one user to another"""
	sender = get_user_by_id(sender_id)
	recipient = get_user_by_id(recipient_id)
	
	if not sender or not recipient:
		return False, "Invalid sender or recipient"
	
	if not sender.can_send_message_to(recipient):
		return False, "Cannot send message to this user"
	
	if not subject or len(subject.strip()) == 0:
		return False, "Subject is required"
	
	if not content or len(content.strip()) < 10:
		return False, "Message content must be at least 10 characters"
	
	if len(content) > 5000:
		return False, "Message content cannot exceed 5000 characters"
	
	message = DirectMessage(sender_id=sender_id, 
						  recipient_id=recipient_id, 
						  subject=subject.strip(), 
						  content=content.strip())
	
	return True, message

def get_user_conversations(user_id):
	"""Get all conversations for a user (both sent and received messages)"""
	from .models import db
	
	# Get all messages where user is either sender or recipient
	sent_messages = DirectMessage.query.filter_by(sender_id=user_id).all()
	received_messages = DirectMessage.query.filter_by(recipient_id=user_id).all()
	
	# Combine and sort by timestamp
	all_messages = sent_messages + received_messages
	all_messages.sort(key=lambda x: x.timestamp, reverse=True)
	
	return all_messages

def mark_messages_as_read(user_id, other_user_id):
	"""Mark all messages from other_user_id to user_id as read"""
	from .models import db
	
	unread_messages = DirectMessage.query.filter_by(
		sender_id=other_user_id, 
		recipient_id=user_id, 
		is_read=False
	).all()
	
	for message in unread_messages:
		message.is_read = True
	
	db.session.commit()
	return len(unread_messages)
