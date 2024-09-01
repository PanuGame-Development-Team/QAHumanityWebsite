from flask import Flask,request,redirect,render_template,abort,session,flash
from flask_bootstrap import Bootstrap
from settings import *
from datetime import datetime
from forms import *
from lib import *
from model import *
import mods.mod_edit
import mods.mod_admin
app = Flask(APP_NAME)
app.secret_key = APP_SECRETKEY
for config in APP_CONFIG:
    app.config[config] = APP_CONFIG[config]
db.init_app(app)
boot = Bootstrap(app)
app.register_blueprint(mods.mod_edit.app)
app.register_blueprint(mods.mod_admin.app)
app.add_template_filter(tagf,"tag_format")
app.add_template_filter(deltag,"del_tag")
app.add_template_filter(safe_script,"safe_script")
app.add_template_filter(uidencode,"uidencode")
@app.route("/",methods=["GET"])
def index():
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),**dic}
    try:
        id = int(request.args.get("id",-1))
    except ValueError:
        abort(404)
    article = Article.query.get(id)
    if article and (not article.delete or session.get("user") in ADMINISTRATOS):
        Article.query.get(id).count += 1
        db.session.commit()
        newest = Article.query.filter(Article.delete == False).order_by(Article.id.desc()).limit(10).all()
        comments = Comment.query.filter(Comment.article == id).order_by(Comment.id.desc()).all()
        return render_template("page.html",article=article,newest=newest,comments=comments,teachers=ADMINISTRATOS,**dic)
    elif not "id" in request.args:
        newest = Article.query.filter(Article.delete == False).order_by(Article.id.desc()).limit(12).all()
        hot = Article.query.filter(Article.delete == False).order_by(Article.count.desc()).limit(12).all()
        recommend = Article.query.filter(Article.delete == False).filter(Article.recommend == True).order_by(Article.id.desc()).all()
        authors = User.query.order_by(User.count.desc()).limit(10).all()
        return render_template("index.html",newest=newest,hot=hot,authors=authors,recommend=recommend,**dic)
    else:
        abort(404)
@app.route("/login/",methods=["GET","POST"])
def login():
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        yxid = form.yxid.data
        password = form.password.data
        user = getuser_id(yxid)
        if user:
            if "HITET" in session and datetime.now() < session["HITET"].replace(tzinfo=None):
                flash("您的休息时长仍未结束，请稍候再试","danger")
                return redirect("/login/")
            elif check_password_hash(user.passwd,password):
                session.clear()
                session["logged_in"] = True
                session["user"] = user.realname
                session["uid"] = user.id
                flash("登录成功","success")
                return redirect("/")
            elif session.get("HIT",0) > HITMAXCNT:
                session["HITET"] = (datetime.now() + timedelta(minutes=HITWAITTIME))
                flash("登录失败，您已经超出了试错最大范围，请%d分钟后重试"%HITWAITTIME,"danger")
                return redirect("/login/")
            else:
                session["HIT"] = session.get("HIT",0) + 1
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
                session["user"] = newuser.realname
                session["uid"] = newuser.id
                flash("登录成功","success")
                return redirect("/")
            else:
                flash("登录失败，可能因为密码错误或无法连接云校","danger")
                return redirect("/login/")
    return render_template("login.html",form=form,**dic)
@app.route("/logout/",methods=["GET"])
def logout():
    session.clear()
    flash("登出成功","success")
    return redirect("/")
@app.route("/write/",methods=["GET","POST"])
def write():
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),**dic}
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
            author = dic["user"]
            time = datetime.now()
            article = Article()
            article.title = title
            article.html = render_markdown(md)
            article.theme = theme
            article.jumimg = jumimg if jumimg else "/static/favicon.jpg"
            article.author = author
            article.time = time
        elif request.form["type"] == "1" and lin(["title","jumimg"],request.form) and "files" in request.files:
            title = request.form["title"]
            jumimg = request.form["jumimg"]
            files = request.files.getlist("files")
            author = dic["user"]
            html = ""
            for file in files:
                webfile = save_file(file,["jpg","png","jpeg","gif","mp4","mov"])
                if webfile:
                    if webfile.split(".")[-1] in ["jpg","png","jpeg","gif"]:
                        html += f"""<img style="width:100%;" src="{webfile}"/>"""
                    else:
                        html += f"""<video controls style="width:100%;" src="{webfile}"></video>"""
            time = datetime.now()
            article = Article()
            article.title = title
            article.html = html
            article.theme = 0
            article.jumimg = jumimg if jumimg else "/static/favicon.jpg"
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
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),**dic}
    if "id" in request.args:
        try:
            author = getuser_intid(int(uiddecode(request.args.get("id"))))
        except:
            abort(400)
        if author:
            if session.get("user") in ADMINISTRATOS:
                articles = Article.query.filter(Article.author == author.realname).order_by(Article.id.desc()).all()
            else:
                articles = Article.query.filter(Article.delete == False).filter(Article.author == author.realname).order_by(Article.id.desc()).all()
            return render_template("author.html",author=author,articles=articles,**dic)
    abort(404)
@app.route("/recommend/",methods=["GET"])
def recommend():
    if session.get("logged_in"):
        user = session.get("user")
        if "id" in request.args and user in ADMINISTRATOS:
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
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),**dic}
    else:
        flash("请先登录","warning")
        return redirect("/login/")
    if "id" in request.args:
        try:
            article = Article.query.get(int(request.args.get("id")))
            article = article if not article.delete else None
        except ValueError:
            abort(404)
    if article and (article.author == dic["user"] or dic["user"] in ADMINISTRATOS):
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
                    webfile = save_file(file,["jpg","png","jpeg","gif","mp4","mov"])
                    if webfile:
                        if webfile.split(".")[-1] in ["jpg","png","jpeg","gif"]:
                            html += f"""<img style="width:100%;" src="{webfile}"/>"""
                        else:
                            html += f"""<video controls style="width:100%;" src="{webfile}"></video>"""
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
            article = article if not article.delete else None
        except ValueError:
            abort(404)
    if article and (article.author == session.get("user") or session.get("user") in ADMINISTRATOS):
        article.delete = True
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
            article = article if not article.delete else None
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
        for name in request.form:
            if name.startswith("comment-"):
                com = request.form.get(name)
                name = name.replace("comment-","",1)
                try:
                    comid = int(name)
                    comment = Comment.query.get(comid)
                    if not comment:
                        abort(400)
                except:
                    abort(400)
                comcom = Comcom()
                comcom.ori_comment = comment
                comcom.ori_comment_id = comid
                comcom.comment = com
                comcom.author = session.get("user")
                db.session.add(comcom)
                db.session.commit()
                flash("评论成功","success")
                return redirect(f"/?id={article.id}")
    abort(404)
@app.route("/about/",methods=["GET"])
def about():
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),**dic}
    return render_template("about.html",**dic,fluid=True)
if __name__ == "__main__":
    app.run(HOST,PORT,DEBUG)