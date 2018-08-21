# -*- coding: UTF-8 -*-

import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request
from . import login_manager
from . import db
from datetime import datetime


class Permission:
    FOLLOW = 1            # 关注其他用户
    COMMENT = 2           # 评论其他文章
    WRITE = 4             # 写原创文章
    MODERATE = 8          # 查处他人不当言论
    ADMIN = 16            # 管理网站


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:                                   # 查询并赋予用户权限角色
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:         # 有user对象头像链接为空时生成链接
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property                                   # 设置password为只读
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader                  # 是否登录验证
    def load_user(user_email):
        return User.query.get(int(user_email))

    def can(self, perm):                        # 判断是否由指定权限
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):                 # 判断是否为管理员权限
        return self.can(Permission.ADMIN)

    def ping(self):                             # 更新最后一次登录时间
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # def change_email(self, token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token.encode('utf-8'))
    #     except:
    #         return False
    #     if data.get('change_email') != self.id:
    #         return False
    #     new_email = data.get('new_email')
    #     if new_email is None:
    #         return False
    #     if self.query.filter_by(email=new_email).first() is not None:
    #         return False
    #     new_email = self.get('email')
    #     self.email = new_email
    #     self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
    #     db.session.add(self)
    #     return True

    def gravatar(self, size=100, default='identicon', rating='g'):      # 头像url地址生成
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash                                 # or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


class AnonymousUser(AnonymousUserMixin):  # 重写匿名用户，为保持默认用户与其他用户一致性
    def can(self, perm):
        return False

    def is_administrator(self):
        return False


# 向 LoginManager 提供一个创建匿名用户的回调
login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    # 初始化角色权限
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        # 通过角色查找现有角色去设置权限，方便修改权限和添加新角色
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:                       # 当数据库中没有某个角色时创建个新角色
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:                  # 添加相应权限
                role.add_permission(perm)
            role.default = (role.name == default_role)      # 判断是否为默认角色
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):                # 添加角色权限
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):             # 移除角色权限
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):                   # 重置角色权限
        self.permissions = 0

    def has_permission(self, perm):                # 判断角色是否有该权限
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name
