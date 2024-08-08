import os 
from secrets import token_hex
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flask_blog import mail

def save_profile_picture(form_picture, username):
    random_hex = token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    
    # Generate a filename based on the username and random hex
    picture_fn = f"{username}_{random_hex}{f_ext}"
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # Resize the profile image
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_post_picture(form_picture, post_id):
    random_hex = token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = f"{post_id}_{random_hex}{f_ext}"
    picture_path = os.path.join(current_app.root_path, 'static/post_pics', picture_fn)

    # Generate a unique filename if a file with that name already exists
    while os.path.exists(picture_path):
        random_hex = token_hex(8)
        picture_fn = f"{post_id}_{random_hex}{f_ext}"
        picture_path = os.path.join(current_app.root_path, 'static/post_pics', picture_fn)

    output_size = (300, 300)  # Example of resizing the image
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='gossiputad@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link: {url_for('users.reset_token', token=token, _external=True)}.
    
If you did not make this request, simply ignore this email.'''
    mail.send(msg)


def send_confirmation_email(user):
    token = user.get_email_confirmation_token()
    msg = Message('Email Confirmation', sender='gossiputad@gmail.com', recipients=[user.email])
    msg.body = f'''To confirm your email, visit the following link: {url_for('users.confirm_email', token=token, _external=True)}.
    
If you did not make this request, simply ignore this email.'''
    mail.send(msg)
