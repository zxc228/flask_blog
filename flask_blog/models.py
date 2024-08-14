from datetime import datetime, timezone, timedelta
from . import db, login_manager
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(120), default='default.png')
    password = db.Column(db.String(60), nullable=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    comments = db.relationship('Comment', backref='author', lazy=True, overlaps="user_comments, user_comments")

    def __repr__(self):
        return f'User({self.username}) {self.email} {self.image_file}'


    def get_reset_token(self, expires_sec=1800):
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_sec)
        }
        return encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")

    def get_email_confirmation_token(self, expires_sec=3600):
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_sec)
        }
        return encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    @staticmethod
    def verify_reset_token(token):
        try:
            data = decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data.get('user_id')
            return User.query.get(user_id)
        except ExpiredSignatureError:
            return None  # Токен истек
        except InvalidTokenError:
            return None  # Токен недействителен

    @staticmethod
    def verify_email_confirmation_token(token):
        try:
            data = decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data.get('user_id')
            return User.query.get(user_id)
        except ExpiredSignatureError:
            return None  # Токен истек
        except InvalidTokenError:
            return None  # Токен недействителен



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('Comment', backref='title', lazy='select', cascade='all, delete-orphan')

   image_file = db.Column(db.String(120), nullable=False, default='default.png')


    
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def likes_count(self):
        return Like.query.filter_by(post_id=self.id, value=True).count()

    def dislikes_count(self):
        return Like.query.filter_by(post_id=self.id, value=False).count()

    
    def __repr__(self):
        return f"Запись {self.title}, {self.date_posted}"
    
    




class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_comments', lazy=True, overlaps="author, comments"))




class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.String(36), db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.Boolean, nullable=False)  # True для лайка, False для дизлайка
