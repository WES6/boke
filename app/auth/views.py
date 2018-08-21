# -*- coding: UTF-8 -*-

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user,  login_required, current_user
from . import auth
from .. models import User
from .forms import LoginForm, RegistrationForm
from .. import db


# 每次请求前运行
@auth.before_app_request
def before_request():
    if current_user.is_authenticated():             # 如果通过验证的用户登录，更新最后登录时间
        current_user.ping()
        # if not current_user.confirmed \
        #         and request.endpoint \
        #         and request.blueprint != 'auth' \
        #         and request.endpoint != 'static':
        #     return redirect(url_for('auth.unconfirmed'))


# 登录路由
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


# 登出路由
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


# 注册路由
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    name=form.name.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Successful register.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
