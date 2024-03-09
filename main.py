from flask import Flask,request,redirect,render_template,abort,session
from flask_bootstrap import Bootstrap
from settings import *
from datetime import datetime,timedelta
from forms import *
from markdown import markdown
from lib import *
from model import *
app = Flask(APP_NAME)
app.secret_key = APP_SECRETKEY
for config in APP_CONFIG:
    app.config[config] = APP_CONFIG[config]
db.init_app(app)
boot = Bootstrap(app)
@app.template_filter("tag_format")
def tagf(html,themeid):
    if themeid == 0:
        theme = "primary"
    elif themeid == 1:
        theme = "danger"
    elif themeid == 2:
        theme = "warning"
    elif themeid == 3:
        theme = "success"
    return html.format(theme=theme)
@app.template_filter("del_tag")
def deltag(html):
    return html.translate({ord(i):None for i in "abcdefghijklmnopqrstuvwxyz1234567890 !-\"'<>/%\{\}=#.:"})
def render_markdown(string):
    return markdown(string,extensions=mdmodules,extension_configs=mdconfigs)
@app.route("/",methods=["GET"])
def index():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid")}
    else:
        dic = {}
    try:
        id = int(request.args.get("id",-1))
        article = Article.query.get(id)
        if article:
            newest = Article.query.order_by(Article.id.desc()).limit(10).all()
            Article.query.get(id).count += 1
            db.session.commit()
            return render_template("page.html",article=article,newest=newest,**dic)
        elif not "id" in request.args:
            newest = Article.query.order_by(Article.id.desc()).limit(12).all()
            hot = Article.query.order_by(Article.count.desc()).limit(12).all()
            recommend = Article.query.filter(Article.recommend == True).order_by(Article.id.desc()).all()
            authors = User.query.order_by(User.count.desc()).limit(20).all()
            return render_template("index.html",newest=newest,hot=hot,authors=authors,recommend=recommend,**dic)
        else:
            abort(404)
    except Exception as e:
        return str(e)
@app.route("/login/",methods=["GET","POST"])
def login():
    if session.get("logged_in"):
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        yxid = form.yxid.data
        password = form.password.data
        try:
            user = User.query.get(int(yxid))
        except:
            abort(404)
        if user:
            if password == user.passwd:
                session["logged_in"] = True
                session["user"] = user.realname
                session["uid"] = user.id
                session["expire"] = datetime.now() + timedelta(days=1)
                return redirect("/")
            else:
                return redirect("/login/")
        else:
            res = yx_login(yxid,password)
            if res["status"] == "success":
                newuser = User()
                newuser.id = int(yxid)
                newuser.realname = res["data"]["userName"]
                newuser.passwd = password
                db.session.add(newuser)
                db.session.commit()
                session["logged_in"] = True
                session["user"] = res["data"]["userName"]
                session["uid"] = int(yxid)
                session["expire"] = datetime.now() + timedelta(days=1)
                return redirect("/")
            else:
                return redirect("/login/")
    return render_template("login.html",form=form)
@app.route("/write/",methods=["GET","POST"])
def write():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid")}
    else:
        return redirect("/login/")
    form = WriteForm()
    if form.validate_on_submit():
        title = form.title.data
        md = form.md.data
        theme = form.theme.data
        jumimg = form.jumimg.data
        author = session.get("user")
        time = datetime.now()
        article = Article()
        article.title = title
        article.html = render_markdown(md)
        article.theme = theme
        article.jumimg = jumimg
        article.author = author
        article.time = time
        User.query.filter(User.realname == author).update({"count":User.count + 1})
        db.session.add(article)
        db.session.commit()
        return redirect(f"/?id={article.id}")
    return render_template("write.html",form=form,**dic)
@app.route("/author/",methods=["GET"])
def author():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid")}
    else:
        dic = {}
    if "id" in request.args:
        try:
            author = User.query.get(int(request.args.get("id")))
        except:
            abort(404)
        if author:
            articles = Article.query.filter(Article.author == author.realname).order_by(Article.id.desc()).all()
            return render_template("author.html",author=author,articles=articles,**dic)
    abort(404)
@app.route("/recommend/",methods=["GET"])
def recommend():
    if session.get("logged_in"):
        user = session.get("user")
        if "id" in request.args and user in TEACHERS:
            art = Article.query.get(int(request.args.get("id")))
            art.recommend = not art.recommend
            db.session.commit()
            return redirect("/")
        else:
            abort(404)
    else:
        abort(404)
@app.route("/about/",methods=["GET"])
def about():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid")}
    else:
        dic = {}
    return render_template("about.html",**dic,fluid=True)
if __name__ == "__main__":
    app.run(HOST,PORT,DEBUG)