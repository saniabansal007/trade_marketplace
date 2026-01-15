from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    category = SelectField('Category', choices=[
        ('weapon', 'Weapon'),
        ('armor', 'Armor'),
        ('potion', 'Potion'),
        ('artifact', 'Artifact'),
        ('scroll', 'Scroll'),
        ('jewel', 'Jewel'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    rarity = SelectField('Rarity', choices=[
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
        ('mythical', 'Mythical')
    ], validators=[DataRequired()])
    image= FileField('Upload Image', validators= [FileAllowed(['jpg', 'jpeg', 'png'], 'images only')])

class MessageForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])

class MessageForm(FlaskForm):
    subject= StringField('Subject', validators=[DataRequired(), Length(min=3, max= 200)])
    content= TextAreaField('Message', validators= [DataRequired(), Length(min=10, max= 500)])

class ProfileForm(FlaskForm):
    avatar = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])