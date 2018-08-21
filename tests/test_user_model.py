# -*- coding: utf-8 -*-
__author__ = "WES"

import unittest
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission


class UserModelTestCase(unittest.TestCase):
    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
