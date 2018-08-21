
from datetime import datetime
from flask import session, render_template, redirect, url_for, request
from flask_login import current_app
from . import main
from .. import db
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/user/<name>')
def user(name):
    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user.html', user=user)
