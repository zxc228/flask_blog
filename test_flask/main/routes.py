from flask import render_template, Blueprint
from test_flask.models import User

from flask import render_template


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')


