from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from forum.models import db, User, Message
import datetime

messages_bp = Blueprint('messages', __name__, template_folder='templates')

@messages_bp.route('/inbox')
@login_required
def inbox():
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('inbox.html', messages=messages)

@messages_bp.route('/sent')
@login_required
def sent():
    messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('sent.html', messages=messages)

@messages_bp.route('/compose')
@login_required
def compose():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('compose.html', users=users)

@messages_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    recipient_id = request.form['recipient_id']
    subject = request.form['subject']
    body = request.form['body']
    
    if not recipient_id or not subject or not body:
        flash('All fields are required!', 'error')
        return redirect(url_for('messages.compose'))
    
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        subject=subject,
        body=body
    )
    
    db.session.add(message)
    db.session.commit()
    flash('Message sent successfully!', 'success')
    return redirect(url_for('messages.sent'))

@messages_bp.route('/message/<int:message_id>')
@login_required
def view_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Check if user is sender or recipient
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('messages.inbox'))
    
    # Mark as read if recipient is viewing
    if message.recipient_id == current_user.id and not message.read:
        message.read = True
        db.session.commit()
    
    return render_template('view_message.html', message=message)

@messages_bp.route('/delete_message/<int:message_id>')
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('messages.inbox'))
    
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted!', 'success')
    return redirect(url_for('messages.inbox'))