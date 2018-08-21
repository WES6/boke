# -*- coding: UTF-8 -*-

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
# flask_moment是一个集成moment.js到Jinja2模板的Flask扩展
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
# LoginManager 对象的session_protection 属性可以设为None、'basic' 或'strong'，以提
# 供不同的安全等级防止用户会话遭篡改。设为'strong' 时，Flask-Login 会记录客户端IP
# 地址和浏览器的用户代理信息，如果发现异动就登出用户
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.config[config_name])
    config.config[config_name].init_app(app)

    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
