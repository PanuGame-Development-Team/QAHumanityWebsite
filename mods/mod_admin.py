from psutil import virtual_memory,cpu_percent,disk_usage
from flask import *
from model import *
from settings import *
from forms import *
from lib import *
import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
app = Blueprint("admin_mod","admin_mod",url_prefix="/admin")
@app.route("/console",methods=["GET"])
@app.route("/console/",methods=["GET"])
def console():
    return render_template("mod_admin/console.html")
@app.route("/data",methods=["GET"])
@app.route("/data/",methods=["GET"])
def data():
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"fluid":True,**dic}
        me = getuser_intid(dic["uid"])
    else:
        flash("您未登录，无法管理站点","danger")
        return redirect("/")
    if not me.realname in ADMINISTRATOS:
        msgqueue.push(f"""用户{me.realname}，于{datetime.now().strftime("%Y/%m/%d %H:%M")}时尝试盗取系统信息。""")
        flash("您无权管理该站点，此事已被通报。","danger")
        return redirect("/")
    sys_data = {}
    sys_data["cpu"] = cpu_percent()
    sys_data["mem"] = virtual_memory().percent
    sys_data["disk"] = disk_usage("/").percent
    return jsonify(sys_data)
@app.route("/admin",methods=["GET"])
@app.route("/admin/",methods=["GET"])
def admin():
    global msgqueue
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"fluid":True,**dic}
        me = getuser_intid(dic["uid"])
    else:
        flash("您未登录，无法管理站点","danger")
        return redirect("/")
    if not me.realname in ADMINISTRATOS:
        msgqueue.push(f"""用户{me.realname}，于{datetime.now().strftime("%Y/%m/%d %H:%M")}时尝试登录管理站点。""")
        flash("您无权管理该站点，此事已被通报。","danger")
        return redirect("/")
    page = request.args.get("page",1)
    try:
        page = int(page)
    except:
        flash("页面有误，退回主页","warning")
        return redirect("/")
    db = request.args.get("db","user")
    if db == "user":
        table = [["ID","真实姓名","文章计数","外号标签",""]]
        for i in User.query.paginate(page=page,max_per_page=10).items:
            table.append([i.id,i.realname,i.count,i.nickname,f"""<a class="btn btn-primary" href="/admin/edit/{i.id}/?db={db}">编辑</a>"""])
    elif db == "article":
        table = [["ID","标题","浏览计数","发布时间","推荐","已删除",""]]
        for i in Article.query.paginate(page=page,max_per_page=10).items:
            table.append([i.id,i.title,i.count,i.time.strftime("%Y/%m/%d %H:%M"),i.recommend,i.delete,f"""<a class="btn btn-primary" href="/admin/edit/{i.id}/?db={db}">编辑</a>"""])
    elif db == "comment":
        table = [["ID","对应文章","评论者","发布时间","内容",""]]
        for i in Comment.query.paginate(page=page,max_per_page=10).items:
            table.append([i.id,i.article,i.author,i.time.strftime("%Y/%m/%d %H:%M"),i.comment,f"""<a class="btn btn-primary" href="/admin/edit/{i.id}/?db={db}">编辑</a>"""])
    else:
        flash("无效数据库，退回主页","warning")
        return redirect("/")
    mq = msgqueue.queue[:]
    mq.reverse()
    return render_template("mod_admin/admin.html",**dic,current=db,msgqueue=mq,table=table)
@app.route("/edit/<int:id>",methods=["GET","POST"])
@app.route("/edit/<int:id>/",methods=["GET","POST"])
def edit_admin(id):
    dic = {i:view_initdic[i] for i in view_initdic}
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"fluid":True,**dic}
        me = getuser_intid(dic["uid"])
    else:
        flash("您未登录，无法管理站点","danger")
        return redirect("/")
    if not me.realname in ADMINISTRATOS:
        msgqueue.push(f"""用户{me.realname}，于{datetime.now().strftime("%Y/%m/%d %H:%M")}时尝试登录管理站点。""")
        flash("您无权管理该站点，此事已被通报。","danger")
        return redirect("/")
    dbn = request.args.get("db","user")
    if dbn == "user":
        user = getuser_intid(id)
        if user:
            form = Admin_User()
            if form.validate_on_submit():
                try:
                    user.realname = form.data["realname"]
                    if form.data["passwd"]:
                        user.passwd = generate_password_hash(form.data["passwd"])
                    user.nickname = form.data["nickname"]
                    db.session.commit()
                    flash("修改成功","success")
                except Exception as e:
                    flash("修改失败，可能用户名或真实姓名等重复","danger")
                return redirect("/admin/admin")
            form.realname.default = user.realname
            form.nickname.default = user.nickname
        else:
            abort(404)
    elif dbn == "article":
        art = Article.query.get(id)
        if art:
            form = Admin_Article()
            if form.validate_on_submit():
                try:
                    art.title = form.data["title"]
                    art.html = form.data["html"]
                    db.session.commit()
                    flash("修改成功","success")
                except Exception as e:
                    flash("修改失败","danger")
                return redirect("/admin/admin")
            form.title.defualt = art.title
            form.html.default = art.html
        else:
            abort(404)
    elif dbn == "comment":
        comment = Comment.query.get(id)
        if comment:
            form = Admin_Comment()
            if form.validate_on_submit():
                try:
                    comment.comment = form.data["comment"]
                    db.session.commit()
                    flash("修改成功","success")
                except Exception as e:
                    flash("修改失败","danger")
                return redirect("/admin/admin")
            form.comment.defualt = comment.comment
        else:
            abort(404)
    else:
        flash("无效数据库，退回主页","warning")
        return redirect("/")
    form.process()
    return render_template(f"mod_admin/db_{dbn}.html",form=form,**dic)