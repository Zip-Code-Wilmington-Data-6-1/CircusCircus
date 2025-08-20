"""
Direct messaging functionality for CircusCircus forum
"""

from .models import db, DirectMessage, User
from .user import get_user_by_id
import datetime

class MessageManager:
    """Class to handle direct message operations"""
    
    def __init__(self, user):
        self.user = user
    
    def send_message(self, recipient_username, subject, content):
        """Send a direct message to another user"""
        recipient = User.query.filter_by(username=recipient_username).first()
        
        if not recipient:
            return False, "Recipient not found"
        
        if recipient.id == self.user.id:
            return False, "Cannot send message to yourself"
        
        if not self.user.can_send_message_to(recipient):
            return False, "Cannot send message to this user"
        
        # Validate message content
        errors = []
        if not subject or len(subject.strip()) == 0:
            errors.append("Subject is required")
        elif len(subject) > 200:
            errors.append("Subject cannot exceed 200 characters")
        
        if not content or len(content.strip()) < 10:
            errors.append("Message content must be at least 10 characters")
        elif len(content) > 5000:
            errors.append("Message content cannot exceed 5000 characters")
        
        if errors:
            return False, errors
        
        # Create and save the message
        message = DirectMessage(
            sender_id=self.user.id,
            recipient_id=recipient.id,
            subject=subject.strip(),
            content=content.strip()
        )
        
        db.session.add(message)
        db.session.commit()
        
        return True, message
    
    def get_inbox(self, page=1, per_page=20):
        """Get received messages for the user"""
        return DirectMessage.query.filter_by(recipient_id=self.user.id)\
                                 .order_by(DirectMessage.timestamp.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
    
    def get_sent_messages(self, page=1, per_page=20):
        """Get sent messages by the user"""
        return DirectMessage.query.filter_by(sender_id=self.user.id)\
                                 .order_by(DirectMessage.timestamp.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
    
    def get_conversation_with(self, other_user_id):
        """Get all messages in a conversation with another user"""
        messages = DirectMessage.query.filter(
            ((DirectMessage.sender_id == self.user.id) & (DirectMessage.recipient_id == other_user_id)) |
            ((DirectMessage.sender_id == other_user_id) & (DirectMessage.recipient_id == self.user.id))
        ).order_by(DirectMessage.timestamp.asc()).all()
        
        return messages
    
    def mark_conversation_as_read(self, other_user_id):
        """Mark all messages from another user as read"""
        unread_messages = DirectMessage.query.filter_by(
            sender_id=other_user_id,
            recipient_id=self.user.id,
            is_read=False
        ).all()
        
        for message in unread_messages:
            message.is_read = True
        
        db.session.commit()
        return len(unread_messages)
    
    def get_unread_count(self):
        """Get count of unread messages"""
        return DirectMessage.query.filter_by(
            recipient_id=self.user.id,
            is_read=False
        ).count()
    
    def delete_message(self, message_id):
        """Delete a message (only if user is sender or recipient)"""
        message = DirectMessage.query.get(message_id)
        
        if not message:
            return False, "Message not found"
        
        if message.sender_id != self.user.id and message.recipient_id != self.user.id:
            return False, "You don't have permission to delete this message"
        
        db.session.delete(message)
        db.session.commit()
        
        return True, "Message deleted successfully"
    
    def get_recent_conversations(self, limit=10):
        """Get recent conversations (users the current user has messaged with)"""
        # Get recent messages where user is sender or recipient
        sent_messages = DirectMessage.query.filter_by(sender_id=self.user.id)\
                                          .order_by(DirectMessage.timestamp.desc())\
                                          .limit(limit * 2).all()
        
        received_messages = DirectMessage.query.filter_by(recipient_id=self.user.id)\
                                              .order_by(DirectMessage.timestamp.desc())\
                                              .limit(limit * 2).all()
        
        # Get unique users and their latest message
        users_dict = {}
        
        for msg in sent_messages + received_messages:
            other_user_id = msg.recipient_id if msg.sender_id == self.user.id else msg.sender_id
            
            if other_user_id not in users_dict or msg.timestamp > users_dict[other_user_id]['timestamp']:
                other_user = User.query.get(other_user_id)
                if other_user:
                    users_dict[other_user_id] = {
                        'user': other_user,
                        'latest_message': msg,
                        'timestamp': msg.timestamp,
                        'unread_count': self.get_unread_count_from(other_user_id)
                    }
        
        # Sort by timestamp and limit
        conversations = sorted(users_dict.values(), key=lambda x: x['timestamp'], reverse=True)
        return conversations[:limit]
    
    def get_unread_count_from(self, other_user_id):
        """Get count of unread messages from a specific user"""
        return DirectMessage.query.filter_by(
            sender_id=other_user_id,
            recipient_id=self.user.id,
            is_read=False
        ).count()

def get_message_manager(user_id):
    """Factory function to create MessageManager"""
    user = User.query.get(user_id)
    if not user:
        return None
    return MessageManager(user)

def get_all_users_for_messaging(current_user_id, search_term=None):
    """Get all users that can receive messages (excluding current user)"""
    query = User.query.filter(
        User.id != current_user_id,
        User.is_active == True
    )
    
    if search_term:
        query = query.filter(
            (User.username.ilike(f"%{search_term}%")) |
            (User.first_name.ilike(f"%{search_term}%")) |
            (User.last_name.ilike(f"%{search_term}%"))
        )
    
    return query.order_by(User.username).all()

def get_message_by_id(message_id, user_id):
    """Get a message by ID, ensuring user has permission to view it"""
    message = DirectMessage.query.get(message_id)
    
    if not message:
        return None
    
    # User can only view messages they sent or received
    if message.sender_id != user_id and message.recipient_id != user_id:
        return None
    
    return message
