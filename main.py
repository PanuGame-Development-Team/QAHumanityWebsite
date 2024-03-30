from flask import Flask,request,redirect,render_template,abort,session,flash
from flask_bootstrap import Bootstrap
from settings import *
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from forms import *
from markdown import markdown
from lib import *
from model import *
from uuid import uuid4
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
    return html.translate({ord(i):None for i in "abcdefghijklmnopqrstuvwxyz1234567890 !-\"'<>/%\{\}=#.:;"})
def render_markdown(string):
    return markdown(string,extensions=mdmodules,extension_configs=mdconfigs)
@app.route("/",methods=["GET"])
def index():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"version":APP_VERSION}
    else:
        dic = {"version":APP_VERSION}
    try:
        id = int(request.args.get("id",-1))
    except ValueError:
        abort(404)
    article = Article.query.get(id)
    if article:
        Article.query.get(id).count += 1
        db.session.commit()
        newest = Article.query.order_by(Article.id.desc()).limit(10).all()
        comments = Comment.query.filter(Comment.article == id).order_by(Comment.id.desc()).limit(20).all()
        return render_template("page.html",article=article,newest=newest,comments=comments,teachers=TEACHERS,**dic)
    elif not "id" in request.args:
        newest = Article.query.order_by(Article.id.desc()).limit(12).all()
        hot = Article.query.order_by(Article.count.desc()).limit(12).all()
        recommend = Article.query.filter(Article.recommend == True).order_by(Article.id.desc()).all()
        authors = User.query.order_by(User.count.desc()).limit(10).all()
        return render_template("index.html",newest=newest,hot=hot,authors=authors,recommend=recommend,**dic)
    else:
        abort(404)
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
        except ValueError:
            user = ExUser.query.filter(ExUser.name == yxid).first()
        except:
            abort(404)
        if user:
            if check_password_hash(user.passwd,password):
                session["logged_in"] = True
                session["user"] = user.realname
                session["uid"] = user.id
                flash("登录成功","success")
                return redirect("/")
            else:
                flash("登录失败，可能因为密码错误或密码更改（以第一次登录本网站时为准）","danger")
                return redirect("/login/")
        else:
            res = yx_login(yxid,password)
            if res["status"] == "success":
                try:
                    newuser = User()
                    newuser.id = int(yxid)
                except ValueError:
                    newuser = ExUser()
                    newuser.name = yxid
                newuser.realname = res["data"]["userName"]
                newuser.passwd = generate_password_hash(password)
                db.session.add(newuser)
                db.session.commit()
                session["logged_in"] = True
                session["user"] = res["data"]["userName"]
                session["uid"] = int(yxid)
                flash("登录成功","success")
                return redirect("/")
            else:
                flash("登录失败，可能因为密码错误或无法连接云校","danger")
                return redirect("/login/")
    return render_template("login.html",form=form,version=APP_VERSION)
@app.route("/write/",methods=["GET","POST"])
def write():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"version":APP_VERSION}
    else:
        return redirect("/login/")
    if request.method == "GET":
        return render_template("write.html",**dic)
    if "type" in request.form:
        if request.form["type"] == "0" and lin(["title","md","theme","jumimg"],request.form):
            title = request.form["title"]
            md = request.form["md"]
            theme = int(request.form["theme"])
            jumimg = request.form["jumimg"]
            author = session.get("user")
            time = datetime.now()
            article = Article()
            article.title = title
            article.html = render_markdown(md)
            article.theme = theme
            article.jumimg = jumimg
            article.author = author
            article.time = time
        elif request.form["type"] == "1" and lin(["title","jumimg"],request.form) and "files" in request.files:
            title = request.form["title"]
            jumimg = request.form["jumimg"]
            files = request.files.getlist("files")
            author = session.get("user")
            html = ""
            for file in files:
                fileext = file.filename.strip().split(".")[-1].lower()
                if fileext in ["jpg","png","jpeg","gif","mp4","mov"]:
                    uuid = uuid4().hex
                    file.save(open(f"static/uploads/{uuid}.{fileext}","wb"))
                    if fileext in ["jpg","png","jpeg","gif"]:
                        html += f"<img style=\"width:100%;\" src=\"/static/uploads/{uuid}.{fileext}\"/>"
                    else:
                        html += f"<video controls style=\"width:100%;\" src=\"/static/uploads/{uuid}.{fileext}\"></video>"
            time = datetime.now()
            article = Article()
            article.title = title
            article.html = html
            article.theme = 0
            article.jumimg = jumimg
            article.author = author
            article.time = time
        else:
            abort(404)
        User.query.filter(User.realname == author).update({"count":User.count + 1})
        ExUser.query.filter(ExUser.realname == author).update({"count":ExUser.count + 1})
        db.session.add(article)
        db.session.commit()
        flash("发布成功","success")
        return redirect(f"/?id={article.id}")
    abort(404)
@app.route("/author/",methods=["GET"])
def author():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"version":APP_VERSION}
    else:
        dic = {"version":APP_VERSION}
    if "id" in request.args:
        try:
            author = User.query.get(int(request.args.get("id")))
        except ValueError:
            abort(404)
        if author:
            articles = Article.query.filter(Article.author == author.realname).order_by(Article.id.desc()).all()
        else:
            author = ExUser.query.get(int(request.args.get("id")))
            if author:
                articles = Article.query.filter(Article.author == author.realname).order_by(Article.id.desc()).all()
        if author:
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
            flash("推荐成功","success")
            return redirect("/")
        else:
            abort(404)
    else:
        abort(404)
@app.route("/change/",methods=["GET","POST"])
def change():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"version":APP_VERSION}
    else:
        flash("请先登录","warning")
        return redirect("/login/")
    if "id" in request.args:
        try:
            article = Article.query.get(int(request.args.get("id")))
        except ValueError:
            abort(404)
    if article and (article.author == dic["user"] or dic["user"] in TEACHERS):
        if request.method == "GET":
            return render_template("write.html",**dic,basetext=article.html,basetitle=article.title,basejumimg=article.jumimg)
        if "type" in request.form:
            if request.form["type"] == "0" and lin(["title","md","theme","jumimg"],request.form):
                title = request.form["title"]
                md = request.form["md"]
                theme = int(request.form["theme"])
                jumimg = request.form["jumimg"]
                article.title = title
                article.html = render_markdown(md)
                article.theme = theme
                article.jumimg = jumimg
            elif request.form["type"] == "1" and lin(["title","jumimg"],request.form) and "files" in request.files:
                title = request.form["title"]
                jumimg = request.form["jumimg"]
                files = request.files.getlist("files")
                html = ""
                for file in files:
                    fileext = file.filename.strip().split(".")[-1].lower()
                    if fileext in ["jpg","png","jpeg","gif","mp4","mov"]:
                        uuid = uuid4().hex
                        file.save(open(f"static/uploads/{uuid}.{fileext}","wb"))
                        if fileext in ["jpg","png","jpeg","gif"]:
                            html += f"<img style=\"width:100%;\" src=\"/static/uploads/{uuid}.{fileext}\"/>"
                        else:
                            html += f"<video controls style=\"width:100%;\" src=\"/static/uploads/{uuid}.{fileext}\"></video>"
                article.title = title
                article.html = html
                article.jumimg = jumimg
            else:
                abort(404)
            db.session.commit()
            flash("修改成功","success")
            return redirect(f"/?id={article.id}")
    elif article:
        flash("您不能修改别人发布的文章","danger")
        return redirect(f"/?id={article.id}")
    abort(404)
@app.route("/delete/",methods=["GET"])
def delete():
    if not session.get("logged_in"):
        flash("请先登录","warning")
        return redirect("/login")
    if "id" in request.args:
        try:
            article = Article.query.get(int(request.args.get("id")))
        except ValueError:
            abort(404)
    if article and (article.author == session.get("user") or session.get("user") in TEACHERS):
        db.session.delete(article)
        User.query.filter(User.realname == article.author).update({"count":User.count - 1})
        ExUser.query.filter(ExUser.realname == article.author).update({"count":ExUser.count - 1})
        db.session.commit()
        flash("删除成功","success")
        return redirect("/")
    elif article:
        flash("您不能删除别人发布的文章","danger")
        return redirect("/")
    abort(404)
@app.route("/comment/",methods=["POST"])
def comment():
    if not session.get("logged_in"):
        flash("请先登录","warning")
        return redirect("/login/")
    if "id" in request.args:
        try:
            article = Article.query.get(int(request.args.get("id")))
        except ValueError:
            abort(404)
    if article:
        if "comment" in request.form:
            com = request.form.get("comment")
            comment = Comment()
            comment.article = article.id
            comment.comment = com
            comment.author = session.get("user")
            db.session.add(comment)
            db.session.commit()
            flash("评论成功","success")
            return redirect(f"/?id={article.id}")
    abort(404)
@app.route("/about/",methods=["GET"])
def about():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"version":APP_VERSION}
    else:
        dic = {"version":APP_VERSION}
    return render_template("about.html",**dic,fluid=True)
if __name__ == "__main__":
    app.run(HOST,PORT,DEBUG)