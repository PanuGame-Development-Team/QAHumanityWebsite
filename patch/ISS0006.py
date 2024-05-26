import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from main import *
with app.app_context():
    for i in Article.query.all():
        i.delete = False
    db.session.commit()