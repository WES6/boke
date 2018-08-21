# -*- coding: UTF-8 -*-
import hashlib

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..decorators import admin_required
from app.main.forms import EditProfileForm, EditProfileAdminForm, PostForm
from . import main
from ..models import User, db, Role, Permission, Post


# 主页路由
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash("Submission of success !")
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)
    # show_followed = False
    # if current_user.is_authenticated:
    #     show_followed = bool(request.cookies.get('show_followed', ''))
    # if show_followed:
    #     query = current_user.followed_posts
    # else:
    #     query = Post.query
    # pagination = query.order_by(Post.timestamp.desc()).paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=False)
    # posts = pagination.items
    # return render_template('index.html', form=form, posts=posts,
    #                        show_followed=show_followed, pagination=pagination)


# 用户页路由
@main.route('/user/<name>')
def user(name):
    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user.html', user=user)


# 用户资料编辑路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', name=current_user.name))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# 管理员编辑路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        if user.email != form.email.data:                                 # 若邮箱更改，重新计算用户头像URL地址
            user.avatar_hash = hashlib.md5(form.email.data.encode('utf-8')).hexdigest()
        user.email = form.email.data
        # user.username = form.username.data
        # user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', name=user.name))
    form.email.data = user.email
    # form.username.data = user.username
    # form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
