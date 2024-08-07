from flask_blog import create_app, db


app = create_app()
app.app_context().push()
db.drop_all()
db.create_all()


#python -m flask_blog.update_db
