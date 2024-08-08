import os 

from secrets import token_hex
from PIL import Image

from flask import url_for, current_app
from flask_mail import Message
from flask_blog import mail


def save_profile_picture(form_picture, username):
    random_hex = token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    
    # Генерируем имя файла на основе имени пользователя и случайного хеша
    picture_fn = f"{username}_{random_hex}{f_ext}"
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # Изменение размера изображения для профиля
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

    # Генерация уникального имени файла, если файл с таким именем уже существует
    while os.path.exists(picture_path):
        random_hex = token_hex(8)
        picture_fn = f"{post_id}_{random_hex}{f_ext}"
        picture_path = os.path.join(current_app.root_path, 'static/post_pics', picture_fn)

    output_size = (300, 300)  # Пример изменения размера изображения
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Запрос на сброс пароля', sender='gossiputad@gmail.com', recipients=[user.email])
    msg.body = f'''Чтобы сбросить пароль перейдите по следующей ссылке: {url_for('users.reset_token', token=token, _external=True)}.
    
Если вы не делали этот запрос, просто проигнорируйте это сообщение.'''
    mail.send(msg)
