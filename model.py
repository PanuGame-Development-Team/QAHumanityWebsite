from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
class Article(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Unicode(128),nullable=False)
    html = db.Column(db.UnicodeText)
    theme = db.Column(db.Integer,default=0)
    # 0:蓝色调
    # 1:红色调
    # 2:橙色调
    # 3:绿色调
    jumimg = db.Column(db.String(64))
    count = db.Column(db.Integer,default=0)
    author = db.Column(db.Unicode(16))
    time = db.Column(db.DateTime,default=datetime.now())
    recommend = db.Column(db.Boolean,default=False)
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    passwd = db.Column(db.Unicode(256))
    realname = db.Column(db.Unicode(32))
    count = db.Column(db.Integer,default=0)