from main import *
with app.app_context():
    db.drop_all()
    db.create_all()
    a = Article()
    a.title = "title"
    a.html = """<button class="btn btn-{theme}">点我</button>"""
    a.jumimg = ""
    a.theme = 1
    a.author = "author"
    a.jumimg = "/static/upload/1.jpg"
    db.session.add(a)
    db.session.commit()