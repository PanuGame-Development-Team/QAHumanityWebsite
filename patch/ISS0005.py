import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from main import *
with app.app_context():
    for i in User.query.all():
        if not i.headimg:
            i.headimg = "/static/user.jpg"
    for i in ExUser.query.all():
        if not i.headimg:
            i.headimg = "/static/user.jpg"
    db.session.commit()