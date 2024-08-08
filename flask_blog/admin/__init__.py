from flask import redirect, url_for, request
from flask_login import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login', next=request.url))

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('users.login'))
        return super(MyAdminIndexView, self).index()
    


from flask_admin import Admin
from flask_blog import create_app, db
from flask_blog.models import User, Post

app = create_app()

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Post, db.session))
