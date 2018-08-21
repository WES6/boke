# -*- coding: UTF-8 -*-

import sys

from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Shell

reload(sys)
sys.setdefaultencoding('utf-8')
app = create_app('default')
manager = Manager(app)


def make_shell_context():
    return dict(db=db, User=User, Role=Role)


# Test
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
