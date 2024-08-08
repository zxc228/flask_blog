from datetime import datetime, timedelta
from flask_blog import db
from flask_blog.models import User

def remove_unconfirmed_users():
    time_limit = datetime.utcnow() - timedelta(hours=24)  # Например, 24 часа
    unconfirmed_users = User.query.filter(User.email_confirmed == False, User.date_created < time_limit).all()

    for user in unconfirmed_users:
        db.session.delete(user)
    
    db.session.commit()
