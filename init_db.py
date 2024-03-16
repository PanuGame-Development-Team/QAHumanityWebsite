from main import *
with app.app_context():
    db.drop_all()
    db.create_all()
    user1 = User()
    user1.id = 23061323
    user1.passwd = "123456"
    user1.realname = "吴尚卿"
    user2 = ExUser()
    user2.name = "gaoyu"
    user2.realname = "高宇"
    user2.passwd = "123456"
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()