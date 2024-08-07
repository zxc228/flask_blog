from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
from flask_bcrypt import Bcrypt
from flask_mail import Mail


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

    from test_flask.main.routes import main
    from test_flask.users.routes import users
    from test_flask.posts.routes import posts

    
    print("Registering blueprints...")
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    
    print("Application created successfully!")
    
    return app
