from datetime import datetime
from typing import List, Optional, Dict, Any
import sqlite3
import logging

class DirectMessage:
    """Represents a direct message between two users"""
    
    def __init__(self, message_id: int = None, sender_id: int = None,  # type: ignore
                 receiver_id: int = None, content: str = "",  # type: ignore
                 timestamp: datetime = None, is_read: bool = False): # type: ignore
        self.message_id = message_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.is_read = is_read

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_read': self.is_read
        }

class DirectMessageManager:
    """Manages direct messages between users"""
    
    def __init__(self, db_path: str = "forum.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the direct messages table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS direct_messages (
                        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (sender_id) REFERENCES users (user_id),
                        FOREIGN KEY (receiver_id) REFERENCES users (user_id)
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
    
    def send_message(self, sender_id: int, receiver_id: int, content: str) -> Optional[int]:
        """Send a direct message from sender to receiver"""
        if sender_id == receiver_id:
            raise ValueError("Cannot send message to yourself")
        
        if not content.strip():
            raise ValueError("Message content cannot be empty")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO direct_messages (sender_id, receiver_id, content)
                    VALUES (?, ?, ?)
                ''', (sender_id, receiver_id, content.strip()))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error sending message: {e}")
            return None
    
    def get_conversation(self, user1_id: int, user2_id: int, 
                        limit: int = 50, offset: int = 0) -> List[DirectMessage]:
        """Get conversation between two users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT message_id, sender_id, receiver_id, content, timestamp, is_read
                    FROM direct_messages
                    WHERE (sender_id = ? AND receiver_id = ?) 
                       OR (sender_id = ? AND receiver_id = ?)
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                ''', (user1_id, user2_id, user2_id, user1_id, limit, offset))
                
                messages = []
                for row in cursor.fetchall():
                    message = DirectMessage(
                        message_id=row[0],
                        sender_id=row[1],
                        receiver_id=row[2],
                        content=row[3],
                        timestamp=datetime.fromisoformat(row[4]) if row[4] else None, # type: ignore
                        is_read=bool(row[5])
                    )
                    messages.append(message)
                return messages
        except sqlite3.Error as e:
            logging.error(f"Error retrieving conversation: {e}")
            return []
    
    def get_user_conversations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all conversations for a user with latest message info"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN sender_id = ? THEN receiver_id 
                            ELSE sender_id 
                        END as other_user_id,
                        MAX(timestamp) as last_message_time,
                        COUNT(CASE WHEN receiver_id = ? AND is_read = FALSE THEN 1 END) as unread_count
                    FROM direct_messages
                    WHERE sender_id = ? OR receiver_id = ?
                    GROUP BY other_user_id
                    ORDER BY last_message_time DESC
                ''', (user_id, user_id, user_id, user_id))
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        'other_user_id': row[0],
                        'last_message_time': row[1],
                        'unread_count': row[2]
                    })
                return conversations
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user conversations: {e}")
            return []
    
    def mark_as_read(self, message_id: int, user_id: int) -> bool:
        """Mark a message as read (only by the receiver)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE direct_messages 
                    SET is_read = TRUE 
                    WHERE message_id = ? AND receiver_id = ?
                ''', (message_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error marking message as read: {e}")
            return False
    
    def mark_conversation_as_read(self, user_id: int, other_user_id: int) -> int:
        """Mark all messages in a conversation as read for the current user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE direct_messages 
                    SET is_read = TRUE 
                    WHERE receiver_id = ? AND sender_id = ? AND is_read = FALSE
                ''', (user_id, other_user_id))
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"Error marking conversation as read: {e}")
            return 0
    
    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete a message (only by sender)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM direct_messages 
                    WHERE message_id = ? AND sender_id = ?
                ''', (message_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error deleting message: {e}")
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Get total unread message count for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM direct_messages 
                    WHERE receiver_id = ? AND is_read = FALSE
                ''', (user_id,))
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting unread count: {e}")
            return 0

# Example usage
if __name__ == "__main__":
    # Initialize the message manager
    dm_manager = DirectMessageManager()
    
    # Send a message
    message_id = dm_manager.send_message(
        sender_id=1, 
        receiver_id=2, 
        content="Hello! How are you doing?"
    )
    
    # Get conversation between two users
    conversation = dm_manager.get_conversation(user1_id=1, user2_id=2)
    
    # Get all conversations for a user
    user_conversations = dm_manager.get_user_conversations(user_id=1)
    
    # Mark messages as read
    dm_manager.mark_conversation_as_read(user_id=2, other_user_id=1)
    
    print(f"Message sent with ID: {message_id}")
    print(f"Conversation has {len(conversation)} messages")