from flask import Blueprint, request, jsonify, render_template, redirect
from flask_login import login_required, current_user
from forum.usersDirectMessages import DirectMessageManager

messages_bp = Blueprint('messages', __name__)
dm_manager = DirectMessageManager()

@messages_bp.route('/messages')
@login_required
def messages_inbox():
    """Display user's message inbox"""
    user_id = current_user.id
    conversations = dm_manager.get_user_conversations(user_id)
    unread_count = dm_manager.get_unread_count(user_id)
    
    return render_template('messages/inbox.html', 
                         conversations=conversations, 
                         unread_count=unread_count)

@messages_bp.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    """Send a new message"""
    data = request.get_json()
    sender_id = current_user.id
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    try:
        message_id = dm_manager.send_message(sender_id, receiver_id, content)
        return jsonify({'success': True, 'message_id': message_id})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@messages_bp.route('/messages/unread-count')
@login_required
def get_unread_count():
    """Get unread message count for navbar"""
    count = dm_manager.get_unread_count(current_user.id)
    return jsonify({'count': count})