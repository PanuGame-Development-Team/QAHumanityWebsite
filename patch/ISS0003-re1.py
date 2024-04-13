import sys
import os
from werkzeug.security import generate_password_hash,check_password_hash
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from main import *
with app.app_context():
    for i in ExUser.query.all():
        i.passwd = generate_password_hash(i.passwd)
    db.session.commit()