from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import os
import secrets
from app import db
from app.models import User, Item, Message
from app.forms import RegistrationForm, LoginForm, ItemForm, MessageForm, ProfileForm
from sqlalchemy import or_, and_

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__, url_prefix='/auth')

# Helper function for saving pictures
def save_picture(form_picture, folder, size=(500, 500)):
    """Save and resize uploaded pictures"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', 'uploads', folder, picture_fn)
    
    # Resize image
    output_size = size
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_fn

@main.route('/')
def index():
    items = Item.query.order_by(Item.created_at.desc()).limit(6).all()
    return render_template('index.html', items=items)

@main.route('/marketplace')
def marketplace():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all')
    rarity = request.args.get('rarity', 'all')
    search = request.args.get('search', '')
    
    query = Item.query
    
    if category != 'all':
        query = query.filter_by(category=category)
    if rarity != 'all':
        query = query.filter_by(rarity=rarity)
    if search:
        query = query.filter(Item.name.ilike(f'%{search}%'))
    
    items = query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('marketplace.html', items=items, 
                         category=category, rarity=rarity, search=search)

@main.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

@main.route('/item/create', methods=['GET', 'POST'])
@login_required
def create_item():
    form = ItemForm()
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image_file = save_picture(form.image.data, 'items')
        else:
            image_file = 'default_item.png'
        
        item = Item(
            name=form.name.data,
            description=form.description.data,
            image=image_file,
            category=form.category.data,
            rarity=form.rarity.data,
            seller=current_user
        )
        db.session.add(item)
        db.session.commit()
        flash('Your item has been listed!', 'success')
        return redirect(url_for('main.item_detail', item_id=item.id))
    return render_template('create_item.html', form=form)

@main.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if item.seller != current_user:
        flash('You can only edit your own items.', 'danger')
        return redirect(url_for('main.item_detail', item_id=item.id))
    
    form = ItemForm()
    
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.category = form.category.data
        item.rarity = form.rarity.data
        
        # Handle image upload
        if form.image.data:
            image_file = save_picture(form.image.data, 'items')
            item.image = image_file
        
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('main.item_detail', item_id=item.id))
    
    elif request.method == 'GET':
        form.name.data = item.name
        form.description.data = item.description
        form.category.data = item.category
        form.rarity.data = item.rarity
    
    return render_template('edit_item.html', form=form, item=item)

@main.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if item.seller != current_user:
        flash('You can only delete your own items.', 'danger')
        return redirect(url_for('main.item_detail', item_id=item.id))
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item deleted successfully.', 'success')
    return redirect(url_for('main.marketplace'))

@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    items = Item.query.filter_by(seller_id=user.id).order_by(
        Item.created_at.desc()
    ).paginate(page=page, per_page=9, error_out=False)
    
    return render_template('profile.html', user=user, items=items)

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.avatar.data:
            avatar_file = save_picture(form.avatar.data, 'avatars', size=(200, 200))
            current_user.avatar = avatar_file
            db.session.commit()
            flash('Profile picture updated!', 'success')
            return redirect(url_for('main.profile', username=current_user.username))
    
    return render_template('edit_profile.html', form=form)

@main.route('/messages/inbox')
@login_required
def inbox():
    page = request.args.get('page', 1, type=int)
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(
        Message.timestamp.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('messages/inbox.html', messages=messages)

@main.route('/messages/sent')
@login_required
def sent():
    page = request.args.get('page', 1, type=int)
    messages = Message.query.filter_by(sender_id=current_user.id).order_by(
        Message.timestamp.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('messages/sent.html', messages=messages)

@main.route('/messages/compose/<int:recipient_id>', methods=['GET', 'POST'])
@main.route('/messages/compose/<int:recipient_id>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def compose_message(recipient_id, item_id=None):
    recipient = User.query.get_or_404(recipient_id)
    item = Item.query.get(item_id) if item_id else None
    
    form = MessageForm()
    
    if form.validate_on_submit():
        message = Message(
            sender=current_user,
            recipient=recipient,
            item_id=item_id,
            subject=form.subject.data,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('main.sent'))
    
    # Pre-fill subject if item is specified
    if item and request.method == 'GET':
        form.subject.data = f"Interested in: {item.name}"
    
    return render_template('messages/compose.html', form=form, recipient=recipient, item=item)

@main.route('/messages/<int:message_id>')
@login_required
def view_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Check if user is sender or recipient
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.inbox'))
    
    # Mark as read if recipient is viewing
    if message.recipient_id == current_user.id and not message.read:
        message.read = True
        db.session.commit()
    
    return render_template('messages/view.html', message=message)

@main.route('/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Check if user is sender or recipient
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.inbox'))
    
    db.session.delete(message)
    db.session.commit()
    
    flash('Message deleted.', 'success')
    return redirect(url_for('main.inbox'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main.route('/messages/chat/<int:other_user_id>')
@main.route('/messages/chat/<int:other_user_id>/<int:item_id>')
@login_required
def chat(other_user_id, item_id=None):
    """Real-time chat interface"""
    other_user = User.query.get_or_404(other_user_id)
    item = Item.query.get(item_id) if item_id else None
    
    # Get existing messages between these two users
    messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.recipient_id == other_user_id),
            db.and_(Message.sender_id == other_user_id, Message.recipient_id == current_user.id)
        )
    ).order_by(Message.timestamp.desc()).limit(50).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.recipient_id == current_user.id and not msg.read:
            msg.read = True
    db.session.commit()
    
    return render_template('messages/chat.html', 
                         other_user=other_user, 
                         item=item, 
                         messages=reversed(messages))