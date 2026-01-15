from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import Message, User
from datetime import datetime

# Store active users and their rooms
active_users = {}

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        active_users[request.sid] = current_user.id
        emit('user_connected', {'user_id': current_user.id}, broadcast=True)
        print(f"User {current_user.username} connected")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_users:
        user_id = active_users[request.sid]
        del active_users[request.sid]
        emit('user_disconnected', {'user_id': user_id}, broadcast=True)
        print(f"User disconnected")

@socketio.on('join_chat')
def handle_join_chat(data):
    """User joins a chat room with another user"""
    if not current_user.is_authenticated:
        return
    
    room = data.get('room')
    join_room(room)
    emit('joined_chat', {'room': room, 'user': current_user.username}, room=room)
    print(f"{current_user.username} joined room {room}")

@socketio.on('leave_chat')
def handle_leave_chat(data):
    """User leaves a chat room"""
    if not current_user.is_authenticated:
        return
    
    room = data.get('room')
    leave_room(room)
    emit('left_chat', {'user': current_user.username}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    """Handle real-time message sending"""
    if not current_user.is_authenticated:
        return
    
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    item_id = data.get('item_id')
    room = data.get('room')
    
    # Save message to database
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=content,
        item_id=item_id,
        subject=f"Chat message",
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    
    # Emit to the room
    emit('receive_message', {
        'message_id': message.id,
        'sender_id': current_user.id,
        'sender_username': current_user.username,
        'sender_avatar': current_user.avatar,
        'recipient_id': recipient_id,
        'content': content,
        'timestamp': message.timestamp.strftime('%H:%M'),
        'full_timestamp': message.timestamp.strftime('%B %d, %Y at %I:%M %p')
    }, room=room)
    
    print(f"Message sent from {current_user.username} in room {room}")

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator"""
    if not current_user.is_authenticated:
        return
    
    room = data.get('room')
    emit('user_typing', {
        'user': current_user.username,
        'user_id': current_user.id
    }, room=room, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Handle stop typing indicator"""
    if not current_user.is_authenticated:
        return
    
    room = data.get('room')
    emit('user_stop_typing', {
        'user': current_user.username,
        'user_id': current_user.id
    }, room=room, include_self=False)