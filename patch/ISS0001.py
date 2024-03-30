import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from main import *
with app.app_context():
    for i in User.query.all():
        i.count = Article.query.filter(Article.author == i.realname).count()
    for i in ExUser.query.all():
        i.count = Article.query.filter(Article.author == i.realname).count()
    db.session.commit()