from flask import render_template, Blueprint
from test_flask.models import User

from flask import render_template


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')


# Обработчик для ошибки 404
@main.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# Обработчик для ошибки 401
@main.app_errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401