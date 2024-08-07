from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate


db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    print(__name__)
    app = Flask(__name__)

    app.config.from_object(Config)
    
    print("Initializing database...")
    db.init_app(app)


    print("Initializing login manager...")
    login_manager.init_app(app)
    
    print("Initializing bcrypt...")
    bcrypt.init_app(app)

    mail.init_app(app)

    migrate = Migrate(app, db)
    from flask_blog.models import User, Post, Comment  # Импортируйте ваши модели здесь
    
    from flask_blog.main.routes import main
    from flask_blog.users.routes import users
    from flask_blog.posts.routes import posts
    from flask_blog.errors.handlers import errors

    print("Registering blueprints...")
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)
    
    print("Application created successfully!")



    return app
